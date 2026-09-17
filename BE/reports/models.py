from django.db import models



class GeneratedReport(models.Model):
    training = models.ForeignKey(
        'trainings.Training', on_delete=models.CASCADE, related_name='reports'
    )
    file = models.FileField(upload_to='reports/')
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report for {self.training} ({self.generated_at})'
