import json

from django.test import Client, TestCase

from .models import Training


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

    def test_write_requires_csrf_token(self):
        response = self.client.post(
            '/api/trainings/',
            data=json.dumps(self.payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
