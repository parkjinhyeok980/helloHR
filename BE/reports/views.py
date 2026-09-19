from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from trainings.queries import training_queryset
from trainings.serializers import serialize_training


@require_GET
@never_cache
def training_report(request, training_id):
    training = get_object_or_404(training_queryset(), pk=training_id)
    data = serialize_training(training)
    participants = {person.id: person for person in training.participants.all()}
    for person in data['participants']:
        records = participants[person['id']].attendance_records.all()
        latest = max(
            (record for record in records if record.status == 'present'
             and hasattr(record, 'signature') and record.signature.strokes),
            key=lambda record: record.id, default=None,
        )
        signature = latest.signature if latest else None
        person['signature'] = signature.strokes if signature else []
        person['signed_at'] = signature.signed_at.isoformat() if signature else None
    return JsonResponse(data)
