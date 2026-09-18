from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from trainings.models import Training
from trainings.views import serialize_training


@require_GET
@never_cache
def training_report(request, training_id):
    training = get_object_or_404(Training.objects.prefetch_related(
        'participants__employee__department', 'participants__attendance_records__signature',
    ), pk=training_id)
    data = serialize_training(training)
    participants = {person.id: person for person in training.participants.all()}
    for person in data['participants']:
        records = participants[person['id']].attendance_records.all()
        signed = sorted(
            (record for record in records if record.status == 'present'
             and hasattr(record, 'signature') and record.signature.strokes),
            key=lambda record: record.id, reverse=True,
        )
        signature = signed[0].signature if signed else None
        person['signature'] = signature.strokes if signature else []
        person['signed_at'] = signature.signed_at.isoformat() if signature else None
    return JsonResponse(data)
