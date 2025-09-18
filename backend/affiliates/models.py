from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
import string
import random


class AffiliatePartner(models.Model):
    """홍보파트너 모델"""
    
    STATUS_CHOICES = [
        ('pending', '승인대기'),
        ('active', '활성'),
        ('suspended', '일시정지'),
        ('terminated', '해지'),
    ]
    
    COMMISSION_TYPE_CHOICES = [
        ('percentage', '퍼센트'),
        ('fixed', '고정금액'),
        ('tiered', '단계별'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자', related_name='affiliate_partner')
    partner_code = models.CharField('파트너 코드', max_length=20, unique=True, blank=True)
    company_name = models.CharField('회사명', max_length=200, blank=True)
    business_registration = models.CharField('사업자등록번호', max_length=50, blank=True)
    phone_number = models.CharField('연락처', max_length=20)
    website = models.URLField('웹사이트', blank=True)
    social_media = models.JSONField('소셜미디어', default=dict, blank=True)
    
    # Status and Commission
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    commission_type = models.CharField('수수료 유형', max_length=20, choices=COMMISSION_TYPE_CHOICES, default='percentage')
    commission_rate = models.DecimalField('수수료율(%)', max_digits=5, decimal_places=2, default=10.00)
    fixed_commission = models.DecimalField('고정 수수료', max_digits=10, decimal_places=2, default=0)
    
    # Statistics
    total_referrals = models.IntegerField('총 추천수', default=0)
    total_conversions = models.IntegerField('총 전환수', default=0)
    total_commission_earned = models.DecimalField('총 수수료', max_digits=15, decimal_places=2, default=0)
    total_commission_paid = models.DecimalField('지급된 수수료', max_digits=15, decimal_places=2, default=0)
    
    # Settings
    minimum_payout = models.DecimalField('최소 지급액', max_digits=10, decimal_places=2, default=50000)
    payout_method = models.CharField('지급 방법', max_length=50, default='bank_transfer')
    bank_info = models.JSONField('은행 정보', default=dict, blank=True)
    
    # Dates
    applied_at = models.DateTimeField('신청일', auto_now_add=True)
    approved_at = models.DateTimeField('승인일', null=True, blank=True)
    last_payout_at = models.DateTimeField('마지막 지급일', null=True, blank=True)
    
    class Meta:
        verbose_name = '홍보파트너'
        verbose_name_plural = '홍보파트너들'
        ordering = ['-applied_at']
    
    def save(self, *args, **kwargs):
        if not self.partner_code:
            self.partner_code = self.generate_partner_code()
        super().save(*args, **kwargs)
    
    def generate_partner_code(self):
        """파트너 코드 생성"""
        while True:
            code = 'SP' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not AffiliatePartner.objects.filter(partner_code=code).exists():
                return code
    
    def get_referral_link(self, base_url='https://stockchart.kr'):
        """추천 링크 생성"""
        return f"{base_url}?ref={self.partner_code}"
    
    def calculate_commission(self, amount):
        """수수료 계산"""
        if self.commission_type == 'percentage':
            return amount * (self.commission_rate / 100)
        elif self.commission_type == 'fixed':
            return self.fixed_commission
        return Decimal('0.00')
    
    def __str__(self):
        return f"{self.user.username} ({self.partner_code})"


class ReferralLink(models.Model):
    """추천 링크 모델"""
    
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.CASCADE, related_name='referral_links')
    link_id = models.UUIDField('링크 ID', default=uuid.uuid4, unique=True)
    name = models.CharField('링크명', max_length=100)
    target_url = models.URLField('타겟 URL', default='/')
    utm_source = models.CharField('UTM Source', max_length=100, blank=True)
    utm_medium = models.CharField('UTM Medium', max_length=100, blank=True)
    utm_campaign = models.CharField('UTM Campaign', max_length=100, blank=True)
    
    # Statistics
    click_count = models.IntegerField('클릭수', default=0)
    conversion_count = models.IntegerField('전환수', default=0)
    
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '추천 링크'
        verbose_name_plural = '추천 링크들'
        ordering = ['-created_at']
    
    def get_full_url(self, base_url='https://stockchart.kr'):
        """전체 URL 생성"""
        url = f"{base_url}{self.target_url}"
        params = []
        params.append(f"ref={self.partner.partner_code}")
        params.append(f"link_id={self.link_id}")
        
        if self.utm_source:
            params.append(f"utm_source={self.utm_source}")
        if self.utm_medium:
            params.append(f"utm_medium={self.utm_medium}")
        if self.utm_campaign:
            params.append(f"utm_campaign={self.utm_campaign}")
        
        return f"{url}?{'&'.join(params)}"
    
    def __str__(self):
        return f"{self.partner.partner_code} - {self.name}"


class ReferralClick(models.Model):
    """추천 링크 클릭 추적"""
    
    link = models.ForeignKey(ReferralLink, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField('IP 주소')
    user_agent = models.TextField('User Agent')
    referer = models.URLField('리퍼러', blank=True)
    clicked_at = models.DateTimeField('클릭일시', auto_now_add=True)
    
    # Session tracking
    session_id = models.CharField('세션 ID', max_length=100, blank=True)
    converted = models.BooleanField('전환 여부', default=False)
    converted_at = models.DateTimeField('전환일시', null=True, blank=True)
    
    class Meta:
        verbose_name = '추천 클릭'
        verbose_name_plural = '추천 클릭들'
        ordering = ['-clicked_at']


class CommissionTransaction(models.Model):
    """수수료 거래 내역"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('earned', '수수료 발생'),
        ('paid', '수수료 지급'),
        ('adjustment', '조정'),
        ('refund', '환불'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('completed', '완료'),
        ('failed', '실패'),
        ('cancelled', '취소'),
    ]
    
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.CASCADE, related_name='commission_transactions')
    transaction_type = models.CharField('거래 유형', max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField('금액', max_digits=15, decimal_places=2)
    currency = models.CharField('통화', max_length=10, default='KRW')
    
    # Reference information
    reference_payment_id = models.CharField('참조 결제 ID', max_length=200, blank=True)
    description = models.TextField('설명', blank=True)
    
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField('처리일시', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    # Payout information
    payout_method = models.CharField('지급 방법', max_length=50, blank=True)
    payout_reference = models.CharField('지급 참조번호', max_length=200, blank=True)
    
    class Meta:
        verbose_name = '수수료 거래'
        verbose_name_plural = '수수료 거래들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.partner.partner_code} - {self.get_transaction_type_display()} - {self.amount}"


class PartnerPerformance(models.Model):
    """파트너 성과 통계 (월별)"""
    
    partner = models.ForeignKey(AffiliatePartner, on_delete=models.CASCADE, related_name='performance_stats')
    year = models.IntegerField('년도')
    month = models.IntegerField('월')
    
    # Statistics
    total_clicks = models.IntegerField('총 클릭수', default=0)
    unique_clicks = models.IntegerField('유니크 클릭수', default=0)
    conversions = models.IntegerField('전환수', default=0)
    revenue_generated = models.DecimalField('발생 매출', max_digits=15, decimal_places=2, default=0)
    commission_earned = models.DecimalField('발생 수수료', max_digits=15, decimal_places=2, default=0)
    
    # Rates
    conversion_rate = models.DecimalField('전환율(%)', max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '파트너 성과'
        verbose_name_plural = '파트너 성과들'
        unique_together = ['partner', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.partner.partner_code} - {self.year}/{self.month:02d}"


class PartnerMaterial(models.Model):
    """홍보 자료"""
    
    MATERIAL_TYPE_CHOICES = [
        ('banner', '배너'),
        ('text', '텍스트'),
        ('video', '비디오'),
        ('landing_page', '랜딩페이지'),
        ('email_template', '이메일 템플릿'),
    ]
    
    name = models.CharField('자료명', max_length=200)
    material_type = models.CharField('자료 유형', max_length=20, choices=MATERIAL_TYPE_CHOICES)
    description = models.TextField('설명', blank=True)
    
    # File/Content
    file_url = models.URLField('파일 URL', blank=True)
    thumbnail_url = models.URLField('썸네일 URL', blank=True)
    content = models.TextField('내용', blank=True)
    
    # Dimensions (for banners)
    width = models.IntegerField('가로', null=True, blank=True)
    height = models.IntegerField('세로', null=True, blank=True)
    
    # Usage stats
    download_count = models.IntegerField('다운로드수', default=0)
    
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '홍보 자료'
        verbose_name_plural = '홍보 자료들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_material_type_display()})"
