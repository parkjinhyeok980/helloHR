from django.db import models
from secrets import randbelow


def generate_attendance_code():
    return f'{randbelow(10000):04d}'



class Training(models.Model):
    class Category(models.TextChoices):
        REQUIRED = '법정 필수', '법정 필수'
        INTERNAL = '사내 교육', '사내 교육'
        OTHER = '기타', '기타'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.INTERNAL)
    location = models.CharField(max_length=200, blank=True)
    attendance_code = models.CharField(max_length=4, default=generate_attendance_code)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class TrainingParticipant(models.Model):
    class CompletionStatus(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not started'
        IN_PROGRESS = 'in_progress', 'In progress'
        COMPLETED = 'completed', 'Completed'

    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name='participants'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.PROTECT, related_name='trainings'
    )
    completion_status = models.CharField(
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.NOT_STARTED,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['training', 'employee'], name='unique_training_employee'
            )
        ]

    def __str__(self):
        return f'{self.employee} - {self.training}'
