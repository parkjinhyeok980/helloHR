from django.utils import timezone


def serialize_participant(participant):
    records = list(participant.attendance_records.all())
    return {
        'id': participant.id,
        'employee_number': participant.employee.employee_number,
        'name': participant.employee.name,
        'department': participant.employee.department.name,
        'attended': any(record.status == 'present' for record in records),
        'signed': any(record.status == 'present' and hasattr(record, 'signature') for record in records),
    }


def serialize_training(training):
    starts_at = timezone.localtime(training.starts_at) if training.starts_at else None
    participants = list(training.participants.all())
    return {
        'id': training.id,
        'title': training.title,
        'description': training.description,
        'category': training.category,
        'date': starts_at.strftime('%Y-%m-%d') if starts_at else '',
        'time': starts_at.strftime('%H:%M') if starts_at else '',
        'location': training.location,
        'code': training.attendance_code,
        'participant_count': len(participants),
        'participants': [serialize_participant(item) for item in participants],
    }


