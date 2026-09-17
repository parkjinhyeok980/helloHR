from django.db import models



class Training(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
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
