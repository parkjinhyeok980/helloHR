from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from attendance.models import Attendance
from trainings.models import Training, TrainingParticipant
from trainings.participants import enroll


class Command(BaseCommand):
    help = '교육 및 대상자 데모 데이터를 중복 없이 생성합니다.'

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        people = [
            {'employee_number': 'DEMO-001', 'name': '김민수', 'department': '인사팀'},
            {'employee_number': 'DEMO-002', 'name': '이지은', 'department': '마케팅팀'},
            {'employee_number': 'DEMO-003', 'name': '박현우', 'department': '개발팀'},
            {'employee_number': 'DEMO-004', 'name': '최수빈', 'department': '경영지원팀'},
            {'employee_number': 'DEMO-005', 'name': '정하늘', 'department': '디자인팀'},
        ]
        examples = [
            ('[데모] 산업안전보건교육', '법정 필수', 2, '10:00', '본관 3층 대회의실', [0, 1, 2, 3, 4], [0, 1, 4]),
            ('[데모] 직장 내 괴롭힘 예방교육', '법정 필수', 7, '14:00', '온라인 교육', [0, 1, 2, 3], []),
            ('[데모] 정보보안 기본 교육', '사내 교육', -5, '15:00', '별관 교육장', [0, 2, 4], [0, 2, 4]),
        ]
        created_trainings = 0
        created_participants = 0
        for title, category, day_offset, time, location, members, attendees in examples:
            start = datetime.combine(today + timedelta(days=day_offset), datetime.strptime(time, '%H:%M').time())
            training, created = Training.objects.get_or_create(
                title=title,
                defaults={
                    'category': category,
                    'location': location,
                    'starts_at': timezone.make_aware(start),
                    'description': '화면 확인을 위한 예시 교육입니다.',
                },
            )
            created_trainings += created
            for index in members:
                participant, was_created = enroll(training, people[index])
                created_participants += was_created
                if index in attendees:
                    Attendance.objects.get_or_create(
                        participant=participant, status=Attendance.Status.PRESENT
                    )
                    if participant.completion_status != TrainingParticipant.CompletionStatus.COMPLETED:
                        participant.completion_status = TrainingParticipant.CompletionStatus.COMPLETED
                        participant.save(update_fields=['completion_status'])
        self.stdout.write(self.style.SUCCESS(
            f'데모 교육 {created_trainings}건, 대상자 등록 {created_participants}건 생성 완료'
        ))
