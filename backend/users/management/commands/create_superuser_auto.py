from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = '자동으로 슈퍼유저를 생성합니다 (Railway 배포용)'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # 환경 변수에서 슈퍼유저 정보 가져오기 (기본값 설정)
        username = os.environ.get('SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('SUPERUSER_EMAIL', 'admin@stockchart.kr')
        password = os.environ.get('SUPERUSER_PASSWORD', 'stockchart2024!')
        
        # 슈퍼유저가 이미 존재하는지 확인
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'슈퍼유저 "{username}"가 이미 존재합니다.')
            )
            return
        
        # 슈퍼유저 생성
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'슈퍼유저 "{username}"가 성공적으로 생성되었습니다.')
            )
            self.stdout.write(
                self.style.SUCCESS(f'관리자 패널: /admin/')
            )
            self.stdout.write(
                self.style.SUCCESS(f'로그인 정보 - 사용자명: {username}, 이메일: {email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'슈퍼유저 생성 중 오류 발생: {e}')
            )
