from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='employees'
    )
    employee_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f'{self.name} ({self.employee_number})'
