import json

from django.test import Client, TestCase
from employees.models import Department, Employee
from trainings.models import Training, TrainingParticipant
from .models import Attendance, Signature


class SignedAttendanceTests(TestCase):
    def setUp(self):
        self.training = Training.objects.create(title='Signature test', attendance_code='0123')
        department = Department.objects.create(name='HR')
        employee = Employee.objects.create(name='Kim', employee_number='E001', department=department)
        self.person = TrainingParticipant.objects.create(training=self.training, employee=employee)
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/api/csrf/')
        self.token = self.client.cookies['csrftoken'].value
        self.url = f'/api/trainings/{self.training.id}/check-in/'
        self.payload = {'name': 'Kim', 'employee_number': 'E001', 'code': '0123',
                        'signature': [[[0.1, 0.2], [0.4, 0.7], [0.8, 0.3]]]}

    def post(self, url=None, payload=None):
        return self.client.post(url or self.url, json.dumps(payload or self.payload),
                                content_type='application/json', HTTP_X_CSRFTOKEN=self.token,
                                HTTP_ORIGIN='http://localhost:5173')

    def test_signature_persists_and_retry_is_idempotent(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['attended'])
        self.assertTrue(response.json()['signed'])
        self.assertEqual(Signature.objects.get().strokes, self.payload['signature'])
        self.assertEqual(self.post().status_code, 200)
        self.assertEqual(Attendance.objects.count(), 1)
        self.assertEqual(Signature.objects.count(), 1)
        other_browser = Client()
        person = other_browser.get('/api/trainings/').json()['results'][0]['participants'][0]
        self.assertTrue(person['attended'])
        self.assertTrue(person['signed'])
        self.assertNotIn('signature', person)

    def test_invalid_identity_code_and_signature_do_not_write(self):
        invalid = [('code', '9999'), ('code', '가나다라'), ('name', 'Other'),
                   ('employee_number', 'E002'), ('signature', []),
                   ('signature', [[[0.5, 0.5]]]), ('signature', [[[0, 0], [2, 1]]]),
                   ('signature', [[[0, 0], [float('nan'), 1]]]),
                   ('signature', [[[0, 0], [True, 1]]]),
                   ('signature', [[[0, 0], [1, 1]]] * 101)]
        for key, value in invalid:
            with self.subTest(key=key, value=value):
                self.assertEqual(self.post(payload={**self.payload, key: value}).status_code, 400)
        self.assertFalse(Attendance.objects.exists())
        self.assertFalse(Signature.objects.exists())

    def test_csrf_is_required(self):
        response = self.client.post(self.url, json.dumps(self.payload), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Attendance.objects.exists())

    def test_cancel_preserves_signature_and_check_in_creates_new_record(self):
        self.post()
        url = f'/api/participants/{self.person.id}/attendance/'
        response = self.post(url=url, payload={'attended': False})
        self.assertFalse(response.json()['attended'])
        self.assertFalse(response.json()['signed'])
        self.assertEqual(Signature.objects.count(), 1)
        self.assertEqual(self.post().status_code, 200)
        self.assertEqual(Signature.objects.count(), 2)

    def test_manual_attendance_persists_without_claiming_a_signature(self):
        url = f'/api/participants/{self.person.id}/attendance/'
        response = self.post(url=url, payload={'attended': True})
        self.assertTrue(response.json()['attended'])
        self.assertFalse(response.json()['signed'])
        self.assertEqual(self.post().status_code, 200)
        self.assertEqual(Attendance.objects.count(), 1)
        self.assertEqual(Signature.objects.count(), 1)

    def test_deleted_training_link_returns_not_found(self):
        self.training.delete()
        self.assertEqual(self.post().status_code, 404)
