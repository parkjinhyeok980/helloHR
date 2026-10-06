from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import RevokedToken


class Command(BaseCommand):
    help = 'Delete expired JWT revocation records; expired JWTs remain invalid.'

    def handle(self, *args, **options):
        count, _ = RevokedToken.objects.filter(expires_at__lte=timezone.now()).delete()
        self.stdout.write(f'Deleted {count} expired token records.')
