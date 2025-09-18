"""
소셜 로그인 인증 모델
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets
import string


class SocialProvider(models.Model):
    """소셜 로그인 제공업체"""
    
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('naver', 'Naver'),
        ('kakao', 'Kakao'),
        ('apple', 'Apple'),
        ('github', 'GitHub'),
        ('twitter', 'Twitter'),
    ]
    
    name = models.CharField('제공업체명', max_length=20, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField('표시명', max_length=50)
    client_id = models.CharField('클라이언트 ID', max_length=255)
    client_secret = models.CharField('클라이언트 시크릿', max_length=255, blank=True)
    authorization_url = models.URLField('인증 URL')
    token_url = models.URLField('토큰 URL')
    user_info_url = models.URLField('사용자 정보 URL')
    scope = models.TextField('스코프', help_text='쉼표로 구분된 권한 목록')
    icon_url = models.URLField('아이콘 URL', blank=True)
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '소셜 제공업체'
        verbose_name_plural = '소셜 제공업체들'
        ordering = ['name']
    
    def __str__(self):
        return self.display_name


class SocialAccount(models.Model):
    """소셜 계정 연동 정보"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    social_id = models.CharField('소셜 ID', max_length=255)
    email = models.EmailField('소셜 이메일', blank=True)
    name = models.CharField('소셜 이름', max_length=100, blank=True)
    profile_image_url = models.URLField('프로필 이미지 URL', blank=True)
    access_token = models.TextField('액세스 토큰', blank=True)
    refresh_token = models.TextField('리프레시 토큰', blank=True)
    token_expires_at = models.DateTimeField('토큰 만료일', null=True, blank=True)
    extra_data = models.JSONField('추가 데이터', default=dict, blank=True)
    is_verified = models.BooleanField('인증 완료', default=False)
    is_primary = models.BooleanField('주 계정', default=False)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    last_login_at = models.DateTimeField('마지막 로그인', null=True, blank=True)
    
    class Meta:
        verbose_name = '소셜 계정'
        verbose_name_plural = '소셜 계정들'
        unique_together = ['provider', 'social_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.display_name}"
    
    @property
    def is_token_expired(self):
        """토큰 만료 여부 확인"""
        if not self.token_expires_at:
            return False
        return timezone.now() > self.token_expires_at
    
    def update_last_login(self):
        """마지막 로그인 시간 업데이트"""
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])


class SocialLoginAttempt(models.Model):
    """소셜 로그인 시도 기록"""
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('success', '성공'),
        ('failed', '실패'),
        ('cancelled', '취소'),
    ]
    
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    social_id = models.CharField('소셜 ID', max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    state_token = models.CharField('상태 토큰', max_length=255, unique=True)
    ip_address = models.GenericIPAddressField('IP 주소', null=True, blank=True)
    user_agent = models.TextField('사용자 에이전트', blank=True)
    error_message = models.TextField('오류 메시지', blank=True)
    extra_data = models.JSONField('추가 데이터', default=dict, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    completed_at = models.DateTimeField('완료일', null=True, blank=True)
    
    class Meta:
        verbose_name = '소셜 로그인 시도'
        verbose_name_plural = '소셜 로그인 시도들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider.display_name} - {self.status} - {self.created_at}"
    
    @classmethod
    def generate_state_token(cls):
        """상태 토큰 생성"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def mark_completed(self, status, user=None, error_message=''):
        """로그인 시도 완료 처리"""
        self.status = status
        self.user = user
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()


class SocialConnectRequest(models.Model):
    """소셜 계정 연동 요청"""
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('approved', '승인'),
        ('rejected', '거부'),
        ('expired', '만료'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    social_id = models.CharField('소셜 ID', max_length=255)
    social_email = models.EmailField('소셜 이메일', blank=True)
    social_name = models.CharField('소셜 이름', max_length=100, blank=True)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_token = models.CharField('인증 토큰', max_length=255, unique=True)
    expires_at = models.DateTimeField('만료일')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    processed_at = models.DateTimeField('처리일', null=True, blank=True)
    
    class Meta:
        verbose_name = '소셜 계정 연동 요청'
        verbose_name_plural = '소셜 계정 연동 요청들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.display_name} - {self.status}"
    
    @classmethod
    def generate_verification_token(cls):
        """인증 토큰 생성"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
    
    @property
    def is_expired(self):
        """만료 여부 확인"""
        return timezone.now() > self.expires_at
    
    def approve(self):
        """연동 요청 승인"""
        if self.is_expired:
            self.status = 'expired'
        else:
            self.status = 'approved'
        self.processed_at = timezone.now()
        self.save()
    
    def reject(self):
        """연동 요청 거부"""
        self.status = 'rejected'
        self.processed_at = timezone.now()
        self.save()


class SocialAuthConfig(models.Model):
    """소셜 인증 설정"""
    
    provider = models.OneToOneField(SocialProvider, on_delete=models.CASCADE)
    auto_create_user = models.BooleanField('자동 사용자 생성', default=True, help_text='새 소셜 계정으로 로그인 시 자동으로 사용자 생성')
    require_email_verification = models.BooleanField('이메일 인증 필요', default=False)
    allow_multiple_accounts = models.BooleanField('다중 계정 허용', default=True, help_text='한 사용자가 여러 소셜 계정 연동 허용')
    sync_profile_data = models.BooleanField('프로필 데이터 동기화', default=True)
    sync_on_login = models.BooleanField('로그인 시 동기화', default=True)
    default_user_type = models.CharField('기본 사용자 유형', max_length=10, default='free')
    required_scopes = models.TextField('필수 권한', blank=True, help_text='쉼표로 구분된 필수 권한 목록')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '소셜 인증 설정'
        verbose_name_plural = '소셜 인증 설정들'
    
    def __str__(self):
        return f"{self.provider.display_name} 설정"


class SocialLoginSession(models.Model):
    """소셜 로그인 세션"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    session_key = models.CharField('세션 키', max_length=255, unique=True)
    access_token = models.TextField('액세스 토큰')
    refresh_token = models.TextField('리프레시 토큰', blank=True)
    expires_at = models.DateTimeField('만료일')
    ip_address = models.GenericIPAddressField('IP 주소', null=True, blank=True)
    user_agent = models.TextField('사용자 에이전트', blank=True)
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    last_accessed_at = models.DateTimeField('마지막 접근일', auto_now=True)
    
    class Meta:
        verbose_name = '소셜 로그인 세션'
        verbose_name_plural = '소셜 로그인 세션들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.display_name} - {self.created_at}"
    
    @property
    def is_expired(self):
        """세션 만료 여부 확인"""
        return timezone.now() > self.expires_at
    
    def refresh_session(self, new_token, new_expires_at):
        """세션 갱신"""
        self.access_token = new_token
        self.expires_at = new_expires_at
        self.last_accessed_at = timezone.now()
        self.save()
    
    def deactivate(self):
        """세션 비활성화"""
        self.is_active = False
        self.save()
