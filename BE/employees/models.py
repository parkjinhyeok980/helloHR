from django.db import models
from django.conf import settings


class Department(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='owned_departments')
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner', 'name'], name='unique_owner_department')]

    def __str__(self):
        return self.name


class Employee(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='owned_employees')
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='employees'
    )
    employee_number = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner', 'employee_number'], name='unique_owner_employee_number')]

    def __str__(self):
        return f'{self.name} ({self.employee_number})'
