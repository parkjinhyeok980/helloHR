import time

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from .models import RevokedToken
from .tokens import issue_token


class JWTTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.get(username='guest')

    def test_guest_issues_http_only_jwt_with_fixed_expiry(self):
        with override_settings(JWT_ACCESS_TTL_SECONDS=60):
            response = self.client.post('/api/accounts/guest/')
        cookie = response.cookies[settings.JWT_COOKIE_NAME]
        claims = jwt.decode(cookie.value, settings.JWT_SIGNING_KEY, algorithms=['HS256'],
                            audience='helloHR-api', issuer='helloHR')
        self.assertEqual(claims['sub'], str(self.user.pk))
        self.assertEqual(claims['exp'] - claims['iat'], 60)
        self.assertEqual(response.json()['expires_at'], claims['exp'])
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/')
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertNotIn('sessionid', response.cookies)
        self.assertNotIn(cookie.value, response.content.decode())
        first_exp = claims['exp']
        self.assertEqual(self.client.get('/api/accounts/session/').json()['expires_at'], first_exp)
        self.assertNotIn(settings.JWT_COOKIE_NAME, self.client.get('/api/trainings/').cookies)

    def test_expired_tampered_and_wrong_algorithm_are_rejected(self):
        token, claims = issue_token(self.user)
        bad_tokens = [token[:-8] + 'tampered',
            jwt.encode({**claims, 'iat': int(time.time()) - 120, 'exp': int(time.time()) - 1}, settings.JWT_SIGNING_KEY, algorithm='HS256'),
            jwt.encode(claims, settings.JWT_SIGNING_KEY, algorithm='HS384'),
            jwt.encode({key: value for key, value in claims.items() if key != 'exp'}, settings.JWT_SIGNING_KEY, algorithm='HS256'),
            jwt.encode({**claims, 'aud': 'another-app'}, settings.JWT_SIGNING_KEY, algorithm='HS256')]
        for token in bad_tokens:
            with self.subTest(token_type=bad_tokens.index(token)):
                self.client.cookies[settings.JWT_COOKIE_NAME] = token
                self.assertEqual(self.client.get('/api/trainings/').status_code, 401)
                self.assertEqual(self.client.get('/api/accounts/session/').status_code, 401)

    def test_logout_revokes_only_current_token_and_replay_fails(self):
        self.client.post('/api/accounts/guest/')
        stolen = self.client.cookies[settings.JWT_COOKIE_NAME].value
        other = Client()
        other.post('/api/accounts/guest/')
        self.client.post('/api/accounts/logout/')
        self.assertEqual(RevokedToken.objects.count(), 1)
        self.client.cookies[settings.JWT_COOKIE_NAME] = stolen
        self.assertEqual(self.client.get('/api/trainings/').status_code, 401)
        self.assertEqual(other.get('/api/trainings/').status_code, 200)

    def test_old_django_session_cannot_authenticate_api(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/trainings/').status_code, 401)

    def test_inactive_user_and_changed_password_invalidate_token(self):
        self.client.post('/api/accounts/guest/')
        self.user.is_active = False
        self.user.save()
        self.assertEqual(self.client.get('/api/trainings/').status_code, 401)
        self.user.is_active = True
        self.user.set_password('changed-password-739!')
        self.user.save()
        self.assertEqual(self.client.get('/api/trainings/').status_code, 401)

    @override_settings(DEBUG=False)
    def test_production_cookie_is_secure(self):
        response = self.client.post('/api/accounts/guest/')
        self.assertTrue(response.cookies[settings.JWT_COOKIE_NAME]['secure'])

    def test_jwt_cookie_writes_still_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        token, _ = issue_token(self.user)
        client.cookies[settings.JWT_COOKIE_NAME] = token
        self.assertEqual(client.post('/api/accounts/logout/').status_code, 403)
        self.assertEqual(client.post('/api/trainings/', {}, content_type='application/json').status_code, 403)

    def test_refresh_extends_expiry_and_preserves_csrf_and_login_identity(self):
        client = Client(enforce_csrf_checks=True)
        _, claims = issue_token(self.user)
        old_claims = {**claims, 'iat': int(time.time()) - 3500, 'exp': int(time.time()) + 100}
        old_token = jwt.encode(old_claims, settings.JWT_SIGNING_KEY, algorithm='HS256')
        client.cookies[settings.JWT_COOKIE_NAME] = old_token
        self.assertEqual(client.post('/api/accounts/refresh/').status_code, 403)
        client.get('/api/csrf/')
        csrf = client.cookies['csrftoken'].value
        response = client.post('/api/accounts/refresh/', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()['expires_at'], old_claims['exp'])
        self.assertEqual(response.json()['expires_at'] - response.json()['server_time'], 3600)
        self.assertEqual(client.cookies['csrftoken'].value, csrf)
        new_token = client.cookies[settings.JWT_COOKIE_NAME].value
        decoded = jwt.decode(new_token, settings.JWT_SIGNING_KEY, algorithms=['HS256'], audience='helloHR-api')
        self.assertEqual(decoded['jti'], old_claims['jti'])
        self.assertEqual(decoded['sub'], old_claims['sub'])
        # Both parallel requests and different tabs can use the previous version.
        self.client.cookies[settings.JWT_COOKIE_NAME] = old_token
        self.assertEqual(self.client.get('/api/trainings/').status_code, 200)
        client.post('/api/accounts/logout/', HTTP_X_CSRFTOKEN=csrf)
        for token in [old_token, new_token]:
            self.client.cookies[settings.JWT_COOKIE_NAME] = token
            self.assertEqual(self.client.post('/api/accounts/refresh/').status_code, 401)
        self.assertGreaterEqual(RevokedToken.objects.get(jti=decoded['jti']).expires_at.timestamp(), decoded['exp'])

    def test_expired_and_missing_tokens_cannot_be_refreshed(self):
        self.assertEqual(self.client.post('/api/accounts/refresh/').status_code, 401)
        _, claims = issue_token(self.user)
        claims.update(iat=int(time.time()) - 100, exp=int(time.time()) - 1)
        self.client.cookies[settings.JWT_COOKIE_NAME] = jwt.encode(claims, settings.JWT_SIGNING_KEY, algorithm='HS256')
        response = self.client.post('/api/accounts/refresh/')
        self.assertEqual(response.status_code, 401)
        self.assertNotIn(settings.JWT_COOKIE_NAME, response.cookies)
