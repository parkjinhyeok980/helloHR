from accounts.decorators import account_required
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from helloHR.payloads import read_json_object
from .models import Training
from .queries import training_queryset
from .serializers import serialize_training


def parse_payload(request):
    data, errors = read_json_object(request)
    if errors:
        return None, errors

    errors = {}
    title = data.get('title')
    category = data.get('category')
    description = data.get('description', '')
    location = data.get('location', '')
    date = data.get('date')
    time = data.get('time')

    if not isinstance(title, str) or not title.strip() or len(title.strip()) > 200:
        errors['title'] = '교육명은 1~200자로 입력해 주세요.'
    if category not in Training.Category.values:
        errors['category'] = '교육 유형을 선택해 주세요.'
    if not isinstance(description, str):
        errors['description'] = '설명은 문자열로 입력해 주세요.'
    if not isinstance(location, str) or len(location.strip()) > 200:
        errors['location'] = '장소는 200자 이내로 입력해 주세요.'
    try:
        starts_at = timezone.make_aware(datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M'))
    except (TypeError, ValueError):
        errors['date'] = '교육일과 시간을 확인해 주세요.'
        starts_at = None

    if errors:
        return None, errors
    return {
        'title': title.strip(),
        'category': category,
        'description': description.strip(),
        'location': location.strip(),
        'starts_at': starts_at,
    }, None


@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({'ok': True})


@require_GET
def public_training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    starts_at = timezone.localtime(training.starts_at) if training.starts_at else None
    return JsonResponse({'id': training.id, 'title': training.title,
                         'category': training.category, 'location': training.location,
                         'date': starts_at.strftime('%Y-%m-%d') if starts_at else '',
                         'time': starts_at.strftime('%H:%M') if starts_at else ''})


@require_http_methods(['GET', 'POST'])
@account_required
def training_list(request):
    if request.method == 'GET':
        trainings = training_queryset().filter(owner=request.user).order_by('-starts_at', '-id')
        return JsonResponse({'results': [serialize_training(item) for item in trainings]})

    fields, errors = parse_payload(request)
    if errors:
        return JsonResponse({'errors': errors}, status=400)
    training = Training.objects.create(owner=request.user, **fields)
    return JsonResponse(serialize_training(training), status=201)


@require_http_methods(['GET', 'PUT', 'DELETE'])
@account_required
def training_detail(request, training_id):
    queryset = Training.objects.all() if request.method == 'DELETE' else training_queryset()
    training = get_object_or_404(queryset, pk=training_id, owner=request.user)
    if request.method == 'GET':
        return JsonResponse(serialize_training(training))
    if request.method == 'DELETE':
        training.delete()
        return HttpResponse(status=204)

    fields, errors = parse_payload(request)
    if errors:
        return JsonResponse({'errors': errors}, status=400)
    for field, value in fields.items():
        setattr(training, field, value)
    training.save(update_fields=list(fields))
    return JsonResponse(serialize_training(training))
