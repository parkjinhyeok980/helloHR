import json
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext
from openpyxl import Workbook

from attendance.models import Attendance, Signature
from employees.models import Employee
from .models import Training, TrainingParticipant


class TrainingApiTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/api/csrf/')
        self.csrf = self.client.cookies['csrftoken'].value
        self.payload = {
            'title': '산업안전보건교육',
            'category': '법정 필수',
            'date': '2026-10-16',
            'time': '14:00',
            'location': '본관 교육장',
            'description': '하반기 필수 교육',
        }

    def request_json(self, method, path, payload):
        return getattr(self.client, method)(
            path,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=self.csrf,
            HTTP_ORIGIN='http://localhost:5173',
        )

    def test_create_read_update_delete(self):
        created = self.request_json('post', '/api/trainings/', self.payload)
        self.assertEqual(created.status_code, 201)
        training_id = created.json()['id']
        self.assertEqual(created.json()['date'], '2026-10-16')
        self.assertEqual(created.json()['time'], '14:00')
        self.assertEqual(len(created.json()['code']), 4)

        listed = self.client.get('/api/trainings/')
        self.assertEqual(listed.json()['results'][0]['id'], training_id)

        changed = {**self.payload, 'title': '수정된 교육', 'location': '별관 교육장'}
        updated = self.request_json('put', f'/api/trainings/{training_id}/', changed)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()['title'], '수정된 교육')
        self.assertEqual(Training.objects.get(pk=training_id).location, '별관 교육장')

        deleted = self.client.delete(
            f'/api/trainings/{training_id}/', HTTP_X_CSRFTOKEN=self.csrf
        )
        self.assertEqual(deleted.status_code, 204)
        self.assertFalse(Training.objects.filter(pk=training_id).exists())

    def test_invalid_payload_does_not_create_training(self):
        invalid = {**self.payload, 'title': '', 'date': 'wrong-date'}
        response = self.request_json('post', '/api/trainings/', invalid)
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['errors'])
        self.assertIn('date', response.json()['errors'])
        self.assertEqual(Training.objects.count(), 0)

    def test_json_validation_is_consistent_across_write_endpoints(self):
        training = Training.objects.create(title='Validation')
        path = f'/api/trainings/{training.id}/participants/'
        person = self.request_json('post', path, {
            'employee_number': 'E01', 'name': 'Kim', 'department': 'HR',
        }).json()
        endpoints = [
            ('post', '/api/trainings/'),
            ('put', f'/api/trainings/{training.id}/'),
            ('post', path),
            ('put', f'{path}{person["id"]}/'),
        ]
        for method, url in endpoints:
            for body, message in [
                ('{', '올바른 JSON을 보내 주세요.'),
                ('[]', '객체 형식의 데이터를 보내 주세요.'),
                ('null', '객체 형식의 데이터를 보내 주세요.'),
            ]:
                with self.subTest(method=method, url=url, body=body):
                    response = getattr(self.client, method)(
                        url, data=body, content_type='application/json',
                        HTTP_X_CSRFTOKEN=self.csrf,
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.json(), {'errors': {'body': message}})

    def test_read_query_count_does_not_grow_with_participants(self):
        training = Training.objects.create(title='Query count')
        path = f'/api/trainings/{training.id}/participants/'
        urls = ['/api/trainings/', f'/api/trainings/{training.id}/',
                path, f'/api/trainings/{training.id}/report/']

        def enroll_signed(number):
            person = self.request_json('post', path, {
                'employee_number': number, 'name': number, 'department': 'HR',
            }).json()
            attendance = Attendance.objects.create(participant_id=person['id'])
            Signature.objects.create(attendance=attendance, strokes=[[[0, 0], [1, 1]]])

        def query_counts():
            counts = []
            for url in urls:
                with CaptureQueriesContext(connection) as queries:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                counts.append(len(queries))
            return counts

        enroll_signed('E01')
        baseline = query_counts()
        for number in range(2, 7):
            enroll_signed(f'E{number:02}')
        self.assertEqual(query_counts(), baseline)
        people = self.client.get(path).json()['results']
        self.assertEqual(len(people), 6)
        self.assertTrue(all(person['attended'] and person['signed'] for person in people))

    def test_write_requires_csrf_token(self):
        response = self.client.post(
            '/api/trainings/',
            data=json.dumps(self.payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def make_workbook(self, rows):
        workbook = Workbook()
        sheet = workbook.active
        for row in rows:
            sheet.append(row)
        output = BytesIO()
        workbook.save(output)
        return SimpleUploadedFile(
            'participants.xlsx', output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_manual_registration_and_excel_upload(self):
        training = Training.objects.create(title='업로드 테스트')
        path = f'/api/trainings/{training.id}/participants/'
        person = {'employee_number': 'EMP-001', 'name': '김민수', 'department': '인사팀'}
        created = self.request_json('post', path, person)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(self.request_json('post', path, person).status_code, 200)

        upload = self.make_workbook([
            ['사번', '이름', '부서'],
            ['EMP-001', '김민수', '인사팀'],
            ['EMP-002', '이지은', '개발팀'],
            ['EMP-002', '이지은', '개발팀'],
        ])
        response = self.client.post(
            f'{path}upload/', {'file': upload},
            HTTP_X_CSRFTOKEN=self.csrf, HTTP_ORIGIN='http://localhost:5173',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['added'], 1)
        self.assertEqual(response.json()['skipped'], 2)
        self.assertEqual(TrainingParticipant.objects.filter(training=training).count(), 2)
        self.assertEqual(len(self.client.get(path).json()['results']), 2)

    def test_invalid_excel_row_does_not_partially_import(self):
        training = Training.objects.create(title='잘못된 파일 테스트')
        upload = self.make_workbook([
            ['사번', '이름', '부서'],
            ['EMP-001', '김민수', '인사팀'],
            ['EMP-002', None, '개발팀'],
        ])
        response = self.client.post(
            f'/api/trainings/{training.id}/participants/upload/', {'file': upload},
            HTTP_X_CSRFTOKEN=self.csrf, HTTP_ORIGIN='http://localhost:5173',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('3행', response.json()['errors']['file'])
        self.assertEqual(TrainingParticipant.objects.count(), 0)

    def test_update_shared_employee_and_delete_only_selected_enrollment(self):
        first = Training.objects.create(title='첫 교육')
        second = Training.objects.create(title='둘째 교육')
        person = {'employee_number': 'EMP-001', 'name': '김민수', 'department': '인사팀'}
        first_created = self.request_json(
            'post', f'/api/trainings/{first.id}/participants/', person
        ).json()
        self.request_json('post', f'/api/trainings/{second.id}/participants/', person)
        other = {'employee_number': 'EMP-002', 'name': '이지은', 'department': '개발팀'}
        self.request_json('post', f'/api/trainings/{first.id}/participants/', other)
        participant = TrainingParticipant.objects.get(pk=first_created['id'])
        Attendance.objects.create(participant=participant, status=Attendance.Status.PRESENT)

        path = f'/api/trainings/{first.id}/participants/{participant.id}/'
        conflict = self.request_json('put', path, {**person, 'employee_number': 'EMP-002'})
        self.assertEqual(conflict.status_code, 409)
        updated = self.request_json(
            'put', path,
            {'employee_number': 'EMP-003', 'name': '김민수 수정', 'department': '총무팀'},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()['employee_number'], 'EMP-003')
        self.assertEqual(updated.json()['department'], '총무팀')
        other_list = self.client.get(f'/api/trainings/{second.id}/participants/').json()
        self.assertEqual(other_list['results'][0]['name'], '김민수 수정')

        deleted = self.client.delete(path, HTTP_X_CSRFTOKEN=self.csrf)
        self.assertEqual(deleted.status_code, 204)
        self.assertFalse(TrainingParticipant.objects.filter(pk=participant.id).exists())
        self.assertFalse(Attendance.objects.filter(participant_id=participant.id).exists())
        self.assertEqual(TrainingParticipant.objects.filter(training=second).count(), 1)
        self.assertTrue(Employee.objects.filter(employee_number='EMP-003').exists())
