from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """사용자 모델"""
    
    USER_TYPE_CHOICES = [
        ('free', '무료 사용자'),
        ('paid', '유료 사용자'),
        ('admin', '관리자'),
    ]
    
    SUBSCRIPTION_STATUS_CHOICES = [
        ('inactive', '비활성'),
        ('active', '활성'),
        ('expired', '만료'),
    ]
    
    email = models.EmailField('이메일', unique=True)
    user_type = models.CharField('사용자 유형', max_length=10, choices=USER_TYPE_CHOICES, default='free')
    subscription_status = models.CharField('구독 상태', max_length=10, choices=SUBSCRIPTION_STATUS_CHOICES, default='inactive')
    free_access_count = models.IntegerField('무료 접근 횟수', default=0)
    referral_code = models.CharField('추천 코드', max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='추천인')
    total_profit = models.DecimalField('총 수익률', max_digits=10, decimal_places=2, default=0)
    prediction_accuracy = models.DecimalField('예측 정확도', max_digits=5, decimal_places=2, default=0)
    social_provider = models.CharField('소셜 로그인 제공자', max_length=20, blank=True)
    social_id = models.CharField('소셜 ID', max_length=100, blank=True)
    phone_number = models.CharField('전화번호', max_length=20, blank=True)
    language_preference = models.CharField('언어 설정', max_length=10, default='ko')
    subscription_expiry = models.DateTimeField('구독 만료일', null=True, blank=True)
    created_at = models.DateTimeField('가입일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
        
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def can_access_premium(self):
        """프리미엄 기능 접근 권한 확인"""
        # Admin users have full access
        if self.user_type == 'admin':
            return True
        
        # Paid users have full access
        if self.user_type == 'paid':
            return True
            
        # Free users get basic chart access (no limit for basic viewing)
        # Only advanced features like predictions/rankings have limits
        if self.user_type == 'free':
            return True  # Allow basic chart viewing for all logged-in users
            
        return False
    
    def increment_free_access(self):
        """무료 접근 횟수 증가"""
        if self.user_type == 'free':
            self.free_access_count += 1
            self.save()

class UserProfile(models.Model):
    """사용자 프로필"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='사용자')
    avatar = models.ImageField('프로필 사진', upload_to='avatars/', blank=True)
    bio = models.TextField('자기소개', max_length=500, blank=True)
    website = models.URLField('웹사이트', blank=True)
    location = models.CharField('위치', max_length=100, blank=True)
    birth_date = models.DateField('생년월일', null=True, blank=True)
    
    class Meta:
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필들'
    
    def __str__(self):
        return f"{self.user.username} 프로필"

class Subscription(models.Model):
    """구독 정보"""
    
    PLAN_CHOICES = [
        ('basic', '기본 요금제'),
        ('premium', '프리미엄 요금제'),
        ('pro', '프로 요금제'),
    ]
    
    STATUS_CHOICES = [
        ('active', '활성'),
        ('cancelled', '취소됨'),
        ('expired', '만료됨'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='사용자')
    plan = models.CharField('요금제', max_length=20, choices=PLAN_CHOICES)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateTimeField('시작일')
    end_date = models.DateTimeField('종료일')
    payment_id = models.CharField('결제 ID', max_length=100, blank=True)
    amount = models.DecimalField('금액', max_digits=10, decimal_places=2)
    currency = models.CharField('통화', max_length=10, default='KRW')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '구독'
        verbose_name_plural = '구독들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"
