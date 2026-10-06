from django.conf import settings
from django.db import migrations


def create_guest_and_assign_legacy(apps, schema_editor):
    alias = schema_editor.connection.alias
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Account = apps.get_model('accounts', 'Account')
    guest = User.objects.using(alias).create(
        username='guest', email='guest@hellohr.invalid', password='!',
        is_active=True, is_staff=False, is_superuser=False,
    )
    Account.objects.using(alias).create(user_id=guest.pk, email=guest.email, name='게스트')
    for app, model in [('employees', 'Department'), ('employees', 'Employee'), ('trainings', 'Training')]:
        apps.get_model(app, model).objects.using(alias).filter(owner__isnull=True).update(owner_id=guest.pk)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
        ('employees', '0002_department_owner_employee_owner_and_more'),
        ('trainings', '0003_training_owner'),
    ]
    operations = [migrations.RunPython(create_guest_and_assign_legacy)]
