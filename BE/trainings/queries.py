from django.db.models import Prefetch

from .models import Training, TrainingParticipant


def participant_queryset():
    return TrainingParticipant.objects.select_related('employee__department').prefetch_related(
        'attendance_records__signature',
    )


def training_queryset():
    return Training.objects.prefetch_related(
        Prefetch('participants', queryset=participant_queryset()),
    )
