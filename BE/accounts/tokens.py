from datetime import datetime, timezone
from uuid import uuid4

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare, salted_hmac

from .models import RevokedToken


def password_stamp(user):
    return salted_hmac('accounts.jwt.password', user.password, secret=settings.JWT_SIGNING_KEY).hexdigest()


def issue_token(user):
    now = int(datetime.now(timezone.utc).timestamp())
    claims = {'sub': str(user.pk), 'iat': now, 'exp': now + settings.JWT_ACCESS_TTL_SECONDS,
              'jti': uuid4().hex, 'iss': 'helloHR', 'aud': 'helloHR-api',
              'pwd': password_stamp(user)}
    return jwt.encode(claims, settings.JWT_SIGNING_KEY, algorithm='HS256'), claims


def revoke_token(request):
    claims = getattr(request, 'jwt_claims', None)
    if claims:
        RevokedToken.objects.get_or_create(jti=claims['jti'], defaults={
            'expires_at': datetime.fromtimestamp(claims['exp'], timezone.utc),
        })


def attach_token(request, response, token):
    rotate_token(request)
    response.set_cookie(settings.JWT_COOKIE_NAME, token, max_age=settings.JWT_ACCESS_TTL_SECONDS,
                        httponly=True, secure=not settings.DEBUG, samesite='Lax', path='/api/')
    return response


class JWTAuthenticationMiddleware:
    """The application API accepts JWT cookies only; Django admin keeps its sessions."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            request.user = AnonymousUser()
            request.jwt_claims = None
            request.jwt_error = None
            token = request.COOKIES.get(settings.JWT_COOKIE_NAME)
            if token:
                try:
                    claims = jwt.decode(token, settings.JWT_SIGNING_KEY, algorithms=['HS256'],
                        issuer='helloHR', audience='helloHR-api',
                        options={'require': ['sub', 'iat', 'exp', 'jti', 'iss', 'aud', 'pwd']})
                    if not claims['sub'].isdigit() or len(claims['sub']) > 18:
                        raise jwt.InvalidTokenError()
                    user = get_user_model().objects.filter(pk=int(claims['sub']), is_active=True).first()
                    if (user is None or not isinstance(claims['pwd'], str)
                            or not constant_time_compare(claims['pwd'], password_stamp(user))
                            or RevokedToken.objects.filter(jti=claims['jti']).exists()):
                        raise jwt.InvalidTokenError()
                    request.user, request.jwt_claims = user, claims
                except jwt.ExpiredSignatureError:
                    request.jwt_error = 'token_expired'
                except (jwt.InvalidTokenError, ValueError, TypeError):
                    request.jwt_error = 'invalid_token'
        return self.get_response(request)
