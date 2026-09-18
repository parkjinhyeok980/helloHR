from django.db import models



class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'

    participant = models.ForeignKey(
        'trainings.TrainingParticipant',
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PRESENT
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.participant} - {self.status}'


class Signature(models.Model):
    attendance = models.OneToOneField(
        Attendance, on_delete=models.CASCADE, related_name='signature'
    )
    file = models.FileField(upload_to='signatures/')
    strokes = models.JSONField(default=list, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Signature for {self.attendance}'
