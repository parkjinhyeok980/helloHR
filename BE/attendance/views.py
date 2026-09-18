import json
import math
from secrets import compare_digest

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from trainings.models import Training, TrainingParticipant
from trainings.views import serialize_participant
from .models import Attendance, Signature


def read_payload(request):
    try:
        data = json.loads(request.body)
        return data if isinstance(data, dict) else {}
    except (ValueError, UnicodeDecodeError):
        return {}


def valid_signature(strokes):
    if not isinstance(strokes, list) or not 1 <= len(strokes) <= 100:
        return False
    count = 0
    has_line = False
    for stroke in strokes:
        if not isinstance(stroke, list) or not stroke:
            return False
        count += len(stroke)
        if count > 10000:
            return False
        for point in stroke:
            if not isinstance(point, list) or len(point) != 2:
                return False
            if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in point):
                return False
        has_line = has_line or any(point != stroke[0] for point in stroke[1:])
    return has_line


@require_POST
@transaction.atomic
def check_in(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    data = read_payload(request)
    code = data.get('code')
    if not isinstance(code, str) or not compare_digest(code.encode(), training.attendance_code.encode()):
        return JsonResponse({'detail': '출석 번호가 일치하지 않습니다.'}, status=400)
    name, number = data.get('name'), data.get('employee_number')
    if not isinstance(name, str) or not isinstance(number, str):
        return JsonResponse({'detail': '이름과 사번을 입력해 주세요.'}, status=400)
    participant = TrainingParticipant.objects.select_for_update().filter(
        training=training, employee__name=name.strip(), employee__employee_number=number.strip(),
    ).first()
    if participant is None:
        return JsonResponse({'detail': '등록된 대상자의 이름과 사번을 확인해 주세요.'}, status=400)
    strokes = data.get('signature')
    if not valid_signature(strokes):
        return JsonResponse({'detail': '서명란에 이름을 직접 적어 주세요.'}, status=400)
    # Preserve the original signature and timestamp when a request is retried.
    record = participant.attendance_records.filter(status=Attendance.Status.PRESENT).order_by('-id').first()
    if record is None:
        record = Attendance.objects.create(participant=participant)
    Signature.objects.get_or_create(attendance=record, defaults={'strokes': strokes})
    return JsonResponse(serialize_participant(participant))


@require_POST
@transaction.atomic
def set_attendance(request, participant_id):
    participant = get_object_or_404(TrainingParticipant.objects.select_for_update(), pk=participant_id)
    attended = read_payload(request).get('attended')
    if type(attended) is not bool:
        return JsonResponse({'detail': '출석 상태를 확인해 주세요.'}, status=400)
    if attended:
        if not participant.attendance_records.filter(status=Attendance.Status.PRESENT).exists():
            Attendance.objects.create(participant=participant)
    else:
        participant.attendance_records.update(status=Attendance.Status.ABSENT)
    return JsonResponse(serialize_participant(participant))
