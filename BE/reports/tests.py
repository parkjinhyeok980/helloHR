from django.test import TestCase
from attendance.models import Attendance, Signature
from employees.models import Department, Employee
from trainings.models import Training, TrainingParticipant


class SignedReportTests(TestCase):
    def setUp(self):
        self.training = Training.objects.create(title='Signed report')
        department = Department.objects.create(name='HR')
        employee = Employee.objects.create(name='Kim', employee_number='E01', department=department)
        self.person = TrainingParticipant.objects.create(training=self.training, employee=employee)
        self.url = f'/api/trainings/{self.training.id}/report/'
        self.strokes = [[[0.1, 0.2], [0.8, 0.7]]]

    def test_report_includes_original_signature_and_time(self):
        attendance = Attendance.objects.create(participant=self.person)
        signature = Signature.objects.create(attendance=attendance, strokes=self.strokes)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        person = response.json()['participants'][0]
        self.assertEqual(person['signature'], self.strokes)
        self.assertEqual(person['signed_at'], signature.signed_at.isoformat())
        self.assertEqual(person['employee_number'], 'E01')
        self.assertIn('no-store', response['Cache-Control'])
        self.assertNotIn('signature', self.client.get('/api/trainings/').json()['results'][0]['participants'][0])

    def test_absent_and_unsigned_participants_have_no_signature(self):
        absent = Attendance.objects.create(participant=self.person, status='absent')
        Signature.objects.create(attendance=absent, strokes=self.strokes)
        person = self.client.get(self.url).json()['participants'][0]
        self.assertFalse(person['attended'])
        self.assertEqual(person['signature'], [])
        Attendance.objects.create(participant=self.person)
        person = self.client.get(self.url).json()['participants'][0]
        self.assertTrue(person['attended'])
        self.assertEqual(person['signature'], [])
        self.assertIsNone(person['signed_at'])

    def test_only_selected_training_and_latest_active_signature(self):
        older = Attendance.objects.create(participant=self.person)
        Signature.objects.create(attendance=older, strokes=[[[0, 0], [1, 1]]])
        latest = Attendance.objects.create(participant=self.person)
        Signature.objects.create(attendance=latest, strokes=self.strokes)
        other = Training.objects.create(title='Other')
        other_person = TrainingParticipant.objects.create(training=other, employee=self.person.employee)
        other_attendance = Attendance.objects.create(participant=other_person)
        Signature.objects.create(attendance=other_attendance, strokes=[[[1, 0], [0, 1]]])
        people = self.client.get(self.url).json()['participants']
        self.assertEqual(len(people), 1)
        self.assertEqual(people[0]['signature'], self.strokes)

    def test_missing_training_returns_404(self):
        self.training.delete()
        self.assertEqual(self.client.get(self.url).status_code, 404)
