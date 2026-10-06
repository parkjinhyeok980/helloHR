from accounts.testing import authenticate_client
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase

from employees.models import Department, Employee
from trainings.models import Training
from trainings.participants import enroll
from .models import Account


class AccountTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.payload = {'email': 'manager@example.com', 'name': '교육 담당자', 'password': 'Strong-education-739!'}

    def post(self, path, payload):
        self.client.get('/api/csrf/')
        return self.client.post(path, payload, content_type='application/json',
                                HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value)

    def test_signup_session_logout_login(self):
        self.assertIsNone(self.client.get('/api/accounts/session/').json()['user'])
        response = self.post('/api/accounts/signup/', self.payload)
        self.assertEqual(response.status_code, 201)
        user = Account.objects.get(email=self.payload['email']).user
        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotEqual(user.password, self.payload['password'])
        self.assertEqual(self.client.get('/api/accounts/session/').json()['user']['name'], self.payload['name'])
        self.assertEqual(self.client.get('/api/trainings/').json()['results'], [])
        self.assertEqual(self.post('/api/accounts/logout/', {}).status_code, 200)
        self.assertEqual(self.client.get('/api/trainings/').status_code, 401)
        self.assertIsNone(self.client.get('/api/accounts/session/').json()['user'])
        self.assertEqual(self.post('/api/accounts/login/', {**self.payload, 'password': 'wrong'}).status_code, 401)
        self.assertEqual(self.post('/api/accounts/login/', {**self.payload, 'email': 'MANAGER@EXAMPLE.COM'}).status_code, 200)

    def test_validation_duplicate_and_csrf(self):
        for payload in [{**self.payload, 'password': '123'}, {**self.payload, 'email': 'bad'},
                        {**self.payload, 'name': ''}, {'email': [], 'name': {}, 'password': []}]:
            self.assertEqual(self.post('/api/accounts/signup/', payload).status_code, 400)
        self.assertFalse(Account.objects.filter(email=self.payload['email']).exists())
        self.post('/api/accounts/signup/', self.payload)
        self.assertEqual(self.post('/api/accounts/signup/', {**self.payload, 'email': 'MANAGER@example.com'}).status_code, 409)
        self.assertEqual(get_user_model().objects.exclude(username='guest').count(), 1)
        for endpoint in ['signup', 'login', 'logout']:
            self.assertEqual(self.client.post(f'/api/accounts/{endpoint}/', self.payload, content_type='application/json').status_code, 403)

    def test_inactive_account_cannot_login(self):
        self.post('/api/accounts/signup/', self.payload)
        self.post('/api/accounts/logout/', {})
        get_user_model().objects.update(is_active=False)
        self.assertEqual(self.post('/api/accounts/login/', self.payload).status_code, 401)


class GuestAccountTests(TestCase):
    def setUp(self):
        self.guest = get_user_model().objects.get(username='guest')
        self.training = Training.objects.create(owner=self.guest, title='Guest training')

    def test_guest_login_session_and_logout(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.get('/api/accounts/guest/').status_code, 405)
        self.assertEqual(client.post('/api/accounts/guest/').status_code, 403)
        client.get('/api/csrf/')
        response = client.post('/api/accounts/guest/', HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['id'], self.guest.pk)
        self.assertEqual(client.get('/api/accounts/session/').json()['user']['id'], self.guest.pk)
        self.assertEqual(client.get('/api/trainings/').json()['results'][0]['id'], self.training.pk)
        client.post('/api/accounts/logout/', HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertIsNone(client.get('/api/accounts/session/').json()['user'])
        self.assertFalse(self.guest.has_usable_password())
        self.assertFalse(self.guest.is_staff)

    def test_shared_guest_does_not_access_private_accounts(self):
        owner = get_user_model().objects.create_user(username='private')
        private = Training.objects.create(owner=owner, title='Private')
        for client in [Client(), Client()]:
            self.assertEqual(client.post('/api/accounts/guest/').json()['user']['id'], self.guest.pk)
            self.assertEqual(client.get(f'/api/trainings/{private.pk}/').status_code, 404)
            self.assertEqual(len(client.get('/api/trainings/').json()['results']), 1)
        self.assertEqual(get_user_model().objects.filter(username='guest').count(), 1)

    def test_disabled_or_privileged_guest_cannot_login(self):
        for field in ['is_staff', 'is_superuser', 'is_active']:
            original = getattr(self.guest, field)
            setattr(self.guest, field, not original)
            self.guest.save()
            self.assertEqual(self.client.post('/api/accounts/guest/').status_code, 503)
            setattr(self.guest, field, original)
        self.guest.set_password('Not-for-public-login-739!')
        self.guest.save()
        self.assertEqual(self.client.post('/api/accounts/guest/').status_code, 503)

    def test_migration_assigns_only_legacy_and_preserves_relations(self):
        from importlib import import_module
        from types import SimpleNamespace
        from django.apps import apps
        from django.db import connection
        from attendance.models import Attendance, Signature

        self.training.delete()
        self.guest.delete()
        owner = get_user_model().objects.create_user(username='private')
        private = Training.objects.create(owner=owner, title='Private')
        legacy = Training.objects.create(title='Legacy')
        person, _ = enroll(legacy, {'employee_number': 'OLD', 'name': 'Kim', 'department': 'HR'})
        attendance = Attendance.objects.create(participant=person)
        signature = Signature.objects.create(attendance=attendance, strokes=[[[0, 0], [1, 1]]])
        migration = import_module('accounts.migrations.0002_guest_account')
        migration.create_guest_and_assign_legacy(apps, SimpleNamespace(connection=connection))
        guest = get_user_model().objects.get(username='guest')
        legacy.refresh_from_db()
        private.refresh_from_db()
        self.assertEqual(legacy.owner, guest)
        self.assertEqual(private.owner, owner)
        self.assertEqual(Employee.objects.get(pk=person.employee_id).owner, guest)
        self.assertEqual(Department.objects.get(pk=person.employee.department_id).owner, guest)
        self.assertTrue(Signature.objects.filter(pk=signature.pk, attendance__participant=person).exists())


class IsolationTests(TestCase):
    def setUp(self):
        self.a = get_user_model().objects.create_user(username='a')
        self.b = get_user_model().objects.create_user(username='b')
        self.training_a = Training.objects.create(owner=self.a, title='A')
        self.training_b = Training.objects.create(owner=self.b, title='B')
        self.person = {'employee_number': 'E001', 'name': 'Kim', 'department': 'HR'}
        self.pa, _ = enroll(self.training_a, self.person)
        self.pb, _ = enroll(self.training_b, self.person)
        authenticate_client(self.client, self.a)

    def test_list_and_create_are_owned(self):
        Training.objects.create(title='Legacy')
        self.assertEqual([row['id'] for row in self.client.get('/api/trainings/').json()['results']], [self.training_a.id])
        response = self.client.post('/api/trainings/', {'title': 'New', 'category': '사내 교육',
            'date': '2026-10-10', 'time': '10:00', 'owner': self.b.id}, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Training.objects.get(pk=response.json()['id']).owner, self.a)

    def test_other_accounts_resources_cannot_be_accessed_or_changed(self):
        base = f'/api/trainings/{self.training_b.id}/'
        endpoints = [('get', base), ('put', base), ('delete', base), ('get', base+'report/'),
                     ('get', base+'participants/'), ('post', base+'participants/'),
                     ('post', base+'participants/upload/'),
                     ('put', base+f'participants/{self.pb.id}/'),
                     ('delete', base+f'participants/{self.pb.id}/'),
                     ('post', f'/api/participants/{self.pb.id}/attendance/')]
        for method, path in endpoints:
            with self.subTest(method=method, path=path):
                self.assertEqual(getattr(self.client, method)(path, {}, content_type='application/json').status_code, 404)
        self.assertTrue(Training.objects.filter(pk=self.training_b.id).exists())
        self.assertFalse(self.pb.attendance_records.exists())

    def test_same_employee_number_does_not_share_personal_data(self):
        self.assertNotEqual(self.pa.employee_id, self.pb.employee_id)
        self.assertNotEqual(self.pa.employee.department_id, self.pb.employee.department_id)
        enroll(self.training_a, {**self.person, 'name': 'Changed'})
        self.pb.employee.refresh_from_db()
        self.assertEqual(self.pb.employee.name, 'Kim')
        response = self.client.put(f'/api/trainings/{self.training_a.id}/participants/{self.pa.id}/',
                                  {**self.person, 'name': 'Updated'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.pb.employee.refresh_from_db()
        self.assertEqual(self.pb.employee.name, 'Kim')

    def test_public_link_exposes_only_training_metadata(self):
        anonymous = Client()
        base = f'/api/trainings/{self.training_b.id}/'
        self.assertEqual(anonymous.get('/api/trainings/').status_code, 401)
        self.assertEqual(anonymous.get(base+'report/').status_code, 401)
        self.assertEqual(anonymous.get(base+'participants/').status_code, 401)
        data = anonymous.get(base+'public/').json()
        self.assertEqual(set(data), {'id', 'title', 'category', 'location', 'date', 'time'})
        response = anonymous.post(base+'check-in/', {**self.person, 'code': self.training_b.attendance_code,
                                  'signature': [[[0, 0], [1, 1]]]}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_legacy_transfer_preview_and_apply(self):
        Account.objects.create(user=self.a, email='a@example.com', name='A')
        legacy = Training.objects.create(title='Legacy')
        person, _ = enroll(legacy, {**self.person, 'employee_number': 'OLD', 'department': 'Old department'})
        call_command('assign_legacy_data', email='a@example.com', stdout=StringIO())
        legacy.refresh_from_db()
        self.assertIsNone(legacy.owner)
        call_command('assign_legacy_data', email='a@example.com', apply=True, stdout=StringIO())
        legacy.refresh_from_db()
        self.assertEqual(legacy.owner, self.a)
        self.assertEqual(Employee.objects.get(pk=person.employee_id).owner, self.a)
        self.assertEqual(Department.objects.get(pk=person.employee.department_id).owner, self.a)
