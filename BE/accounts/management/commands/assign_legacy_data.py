from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Account
from employees.models import Department, Employee
from trainings.models import Training


class Command(BaseCommand):
    help = '소유자 없는 기존 데이터 전체를 지정한 계정으로 이전합니다. 기본은 미리보기입니다.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--apply', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        account = Account.objects.select_for_update().filter(email=options['email'].strip().lower()).first()
        if account is None:
            raise CommandError('먼저 회원가입한 계정의 이메일을 지정해 주세요.')
        departments = Department.objects.filter(owner__isnull=True)
        employees = Employee.objects.filter(owner__isnull=True)
        trainings = Training.objects.filter(owner__isnull=True)
        self.stdout.write(f'교육 {trainings.count()}건, 사원 {employees.count()}명, 부서 {departments.count()}개 → {account.email}')
        if not options['apply']:
            self.stdout.write('이전하려면 같은 명령에 --apply 옵션을 추가하세요.')
            return
        if Employee.objects.filter(owner=account.user, employee_number__in=employees.values('employee_number')).exists():
            raise CommandError('대상 계정에 같은 사번이 있습니다. 중복을 정리한 후 다시 실행하세요.')
        if Department.objects.filter(owner=account.user, name__in=departments.values('name')).exists():
            raise CommandError('대상 계정에 같은 부서명이 있습니다. 중복을 정리한 후 다시 실행하세요.')
        departments.update(owner=account.user)
        employees.update(owner=account.user)
        trainings.update(owner=account.user)
        self.stdout.write(self.style.SUCCESS('기존 데이터와 연결된 출석·서명·보고서의 이전이 완료되었습니다.'))
