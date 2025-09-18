from django.db import models
from django.conf import settings


class Language(models.Model):
    """지원하는 언어 정보"""
    
    LANGUAGE_CHOICES = [
        ('ko', '한국어'),
        ('en', 'English'),
        ('ja', '日本語'),
        ('zh', '中文'),
        ('es', 'Español'),
        ('fr', 'Français'),
        ('de', 'Deutsch'),
        ('pt', 'Português'),
        ('ru', 'Русский'),
        ('ar', 'العربية'),
    ]
    
    code = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, unique=True, verbose_name='언어 코드')
    name = models.CharField(max_length=50, verbose_name='언어명')
    native_name = models.CharField(max_length=50, verbose_name='원어명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    flag_icon = models.CharField(max_length=10, blank=True, verbose_name='국기 아이콘')
    rtl = models.BooleanField(default=False, verbose_name='우측에서 좌측으로 읽기')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    
    class Meta:
        verbose_name = '언어'
        verbose_name_plural = '언어 목록'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.native_name} ({self.code})"


class Translation(models.Model):
    """번역 키-값 저장"""
    
    CATEGORY_CHOICES = [
        ('navigation', '네비게이션'),
        ('buttons', '버튼'),
        ('forms', '폼'),
        ('messages', '메시지'),
        ('content', '컨텐츠'),
        ('errors', '오류'),
        ('charts', '차트'),
        ('predictions', '예측'),
        ('payments', '결제'),
        ('affiliate', '제휴'),
        ('general', '일반'),
    ]
    
    key = models.CharField(max_length=255, verbose_name='번역 키')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name='언어')
    value = models.TextField(verbose_name='번역값')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', verbose_name='카테고리')
    context = models.CharField(max_length=500, blank=True, verbose_name='컨텍스트')
    is_validated = models.BooleanField(default=False, verbose_name='검증됨')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '번역'
        verbose_name_plural = '번역 목록'
        unique_together = ['key', 'language']
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key} ({self.language.code})"


class UserLanguagePreference(models.Model):
    """사용자별 언어 설정"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name='선호 언어')
    timezone = models.CharField(max_length=50, default='Asia/Seoul', verbose_name='시간대')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD', verbose_name='날짜 형식')
    number_format = models.CharField(max_length=20, default='ko', verbose_name='숫자 형식')
    currency = models.CharField(max_length=10, default='KRW', verbose_name='기본 통화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '사용자 언어 설정'
        verbose_name_plural = '사용자 언어 설정'
    
    def __str__(self):
        return f"{self.user.username} - {self.language.native_name}"


class TranslationRequest(models.Model):
    """번역 요청"""
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('rejected', '거부'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '낮음'),
        ('medium', '보통'),
        ('high', '높음'),
        ('urgent', '긴급'),
    ]
    
    key = models.CharField(max_length=255, verbose_name='번역 키')
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_requests', verbose_name='원본 언어')
    target_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='target_requests', verbose_name='대상 언어')
    source_text = models.TextField(verbose_name='원본 텍스트')
    translated_text = models.TextField(blank=True, verbose_name='번역 텍스트')
    category = models.CharField(max_length=20, choices=Translation.CATEGORY_CHOICES, default='general', verbose_name='카테고리')
    context = models.TextField(blank=True, verbose_name='컨텍스트')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='우선순위')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='상태')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='요청자')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='translation_assignments', verbose_name='담당자')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='마감일')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='완료일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '번역 요청'
        verbose_name_plural = '번역 요청 목록'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.key} ({self.source_language.code} → {self.target_language.code})"
