from uuid import uuid4

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from helloHR.payloads import read_json_object
from .models import Account


def user_data(user):
    account = getattr(user, 'account', None)
    return {'id': user.pk, 'email': account.email if account else user.email,
            'name': account.name if account else user.get_full_name() or user.username}


@require_GET
@never_cache
def session(request):
    return JsonResponse({'user': user_data(request.user) if request.user.is_authenticated else None})


@require_POST
@never_cache
def signup(request):
    data, errors = read_json_object(request)
    if errors:
        return JsonResponse({'errors': errors}, status=400)
    email, name, password = (data.get(key) for key in ('email', 'name', 'password'))
    errors = {}
    if not isinstance(email, str) or len(email) > 254:
        errors['email'] = '올바른 이메일을 입력해 주세요.'
    else:
        email = email.strip().lower()
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = '올바른 이메일을 입력해 주세요.'
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
        errors['name'] = '이름은 1~100자로 입력해 주세요.'
    if not isinstance(password, str) or len(password) > 128:
        errors['password'] = '비밀번호는 8~128자로 입력해 주세요.'
    elif not errors:
        try:
            validate_password(password, get_user_model()(email=email, first_name=name))
        except ValidationError:
            errors['password'] = '비밀번호는 8자 이상으로, 개인정보나 흔한 단어·숫자만으로 구성하지 마세요.'
    if errors:
        return JsonResponse({'errors': errors}, status=400)
    try:
        with transaction.atomic():
            user = get_user_model().objects.create_user(username=uuid4().hex, email=email, password=password)
            Account.objects.create(user=user, email=email, name=name.strip())
    except IntegrityError:
        return JsonResponse({'errors': {'email': '이미 가입된 이메일입니다.'}}, status=409)
    login(request, user)
    return JsonResponse({'user': user_data(user)}, status=201)


@require_POST
@never_cache
def signin(request):
    data, errors = read_json_object(request)
    if errors:
        return JsonResponse({'errors': errors}, status=400)
    email, password = data.get('email'), data.get('password')
    if not isinstance(email, str) or not isinstance(password, str) or len(password) > 128:
        return JsonResponse({'detail': '이메일과 비밀번호를 확인해 주세요.'}, status=400)
    account = Account.objects.select_related('user').filter(email=email.strip().lower()).first()
    user = authenticate(request, username=account.user.username if account else '__unknown_account__', password=password)
    if user is None or account is None:
        return JsonResponse({'detail': '이메일 또는 비밀번호가 일치하지 않습니다.'}, status=401)
    login(request, user)
    return JsonResponse({'user': user_data(user)})


@require_POST
@never_cache
def signout(request):
    logout(request)
    return JsonResponse({'ok': True})


@require_POST
@never_cache
def guest_login(request):
    user = get_user_model().objects.filter(
        username='guest', is_active=True, is_staff=False, is_superuser=False,
    ).first()
    if user is None or user.has_usable_password():
        return JsonResponse({'detail': '게스트 계정을 이용할 수 없습니다.'}, status=503)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'user': user_data(user)})
