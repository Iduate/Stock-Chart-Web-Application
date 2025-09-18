from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class PaymentProvider(models.Model):
    """결제 서비스 제공업체"""
    
    PROVIDER_CHOICES = [
        ('iamport', 'Iamport (아임포트)'),
        ('toss', 'Toss Payments (토스페이먼츠)'),
        ('kakaopay', 'Kakao Pay (카카오페이)'),
        ('naverpay', 'Naver Pay (네이버페이)'),
        ('payco', 'PAYCO (페이코)'),
        ('kginicis', 'KG이니시스'),
        ('ksnet', 'KSNET'),
        ('settle', 'NHN 페이코'),
        ('nice', 'NICE정보통신'),
        ('danal', '다날'),
        ('mobilians', '모빌리언스'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True, verbose_name='제공업체')
    display_name = models.CharField(max_length=100, verbose_name='표시명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    is_korean = models.BooleanField(default=True, verbose_name='한국 결제사')
    
    # API 설정
    api_key = models.CharField(max_length=500, blank=True, verbose_name='API 키')
    secret_key = models.CharField(max_length=500, blank=True, verbose_name='비밀 키')
    merchant_id = models.CharField(max_length=100, blank=True, verbose_name='가맹점 ID')
    
    # 결제 방법 지원
    supports_card = models.BooleanField(default=True, verbose_name='신용카드 지원')
    supports_bank = models.BooleanField(default=True, verbose_name='계좌이체 지원')
    supports_vbank = models.BooleanField(default=True, verbose_name='가상계좌 지원')
    supports_phone = models.BooleanField(default=False, verbose_name='휴대폰 결제 지원')
    supports_point = models.BooleanField(default=False, verbose_name='포인트 결제 지원')
    
    # 수수료 설정
    card_fee_rate = models.DecimalField(max_digits=5, decimal_places=3, default=0.0, verbose_name='신용카드 수수료율(%)')
    bank_fee_rate = models.DecimalField(max_digits=5, decimal_places=3, default=0.0, verbose_name='계좌이체 수수료율(%)')
    vbank_fee_amount = models.IntegerField(default=0, verbose_name='가상계좌 수수료(원)')
    
    # 기타 설정
    min_amount = models.IntegerField(default=100, verbose_name='최소 결제금액(원)')
    max_amount = models.IntegerField(default=50000000, verbose_name='최대 결제금액(원)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '결제 제공업체'
        verbose_name_plural = '결제 제공업체 목록'
        ordering = ['name']
    
    def __str__(self):
        return self.display_name


class PaymentMethod(models.Model):
    """결제 수단"""
    
    METHOD_CHOICES = [
        ('card', '신용카드'),
        ('bank', '계좌이체'),
        ('vbank', '가상계좌'),
        ('phone', '휴대폰 결제'),
        ('kakaopay', '카카오페이'),
        ('naverpay', '네이버페이'),
        ('payco', '페이코'),
        ('samsung', '삼성페이'),
        ('lpay', 'LPAY'),
        ('ssgpay', 'SSG페이'),
        ('paypal', 'PayPal'),
        ('point', '포인트'),
    ]
    
    code = models.CharField(max_length=20, choices=METHOD_CHOICES, unique=True, verbose_name='결제수단 코드')
    name = models.CharField(max_length=50, verbose_name='결제수단명')
    icon = models.CharField(max_length=100, blank=True, verbose_name='아이콘 클래스')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    is_korean = models.BooleanField(default=True, verbose_name='한국 결제수단')
    
    # 지원 제공업체
    providers = models.ManyToManyField(PaymentProvider, blank=True, verbose_name='지원 제공업체')
    
    # 설정
    requires_identity_verification = models.BooleanField(default=False, verbose_name='본인인증 필요')
    min_amount = models.IntegerField(default=100, verbose_name='최소 결제금액(원)')
    max_amount = models.IntegerField(default=10000000, verbose_name='최대 결제금액(원)')
    
    display_order = models.IntegerField(default=0, verbose_name='표시 순서')
    
    class Meta:
        verbose_name = '결제 수단'
        verbose_name_plural = '결제 수단 목록'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    """결제 거래"""
    
    STATUS_CHOICES = [
        ('pending', '결제 대기'),
        ('ready', '결제 준비'),
        ('paid', '결제 완료'),
        ('failed', '결제 실패'),
        ('cancelled', '결제 취소'),
        ('partial_cancelled', '부분 취소'),
        ('refunded', '환불 완료'),
    ]
    
    # 기본 정보
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='거래 ID')
    merchant_uid = models.CharField(max_length=100, unique=True, verbose_name='가맹점 주문번호')
    
    # 사용자 및 결제 정보
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='사용자')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.PROTECT, verbose_name='결제 제공업체')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name='결제 수단')
    
    # 결제 금액
    amount = models.PositiveIntegerField(verbose_name='결제 금액(원)')
    fee_amount = models.PositiveIntegerField(default=0, verbose_name='수수료(원)')
    discount_amount = models.PositiveIntegerField(default=0, verbose_name='할인 금액(원)')
    final_amount = models.PositiveIntegerField(verbose_name='최종 결제 금액(원)')
    
    # 결제 상태
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='결제 상태')
    
    # 외부 결제사 정보
    imp_uid = models.CharField(max_length=100, blank=True, verbose_name='결제사 거래번호')
    pg_tid = models.CharField(max_length=100, blank=True, verbose_name='PG사 거래번호')
    pg_provider = models.CharField(max_length=50, blank=True, verbose_name='PG사')
    
    # 결제 상품 정보
    name = models.CharField(max_length=200, verbose_name='결제 상품명')
    description = models.TextField(blank=True, verbose_name='결제 상품 설명')
    
    # 구매자 정보
    buyer_name = models.CharField(max_length=50, verbose_name='구매자명')
    buyer_email = models.EmailField(verbose_name='구매자 이메일')
    buyer_tel = models.CharField(max_length=20, blank=True, verbose_name='구매자 연락처')
    buyer_addr = models.CharField(max_length=255, blank=True, verbose_name='구매자 주소')
    buyer_postcode = models.CharField(max_length=10, blank=True, verbose_name='구매자 우편번호')
    
    # 결제 상세 정보 (JSON)
    payment_details = models.JSONField(default=dict, blank=True, verbose_name='결제 상세 정보')
    
    # 가상계좌 정보
    vbank_num = models.CharField(max_length=50, blank=True, verbose_name='가상계좌 번호')
    vbank_name = models.CharField(max_length=50, blank=True, verbose_name='가상계좌 은행명')
    vbank_holder = models.CharField(max_length=50, blank=True, verbose_name='가상계좌 예금주')
    vbank_date = models.DateTimeField(null=True, blank=True, verbose_name='가상계좌 입금기한')
    
    # 카드 정보
    card_name = models.CharField(max_length=50, blank=True, verbose_name='카드사명')
    card_number = models.CharField(max_length=20, blank=True, verbose_name='카드번호(마스킹)')
    card_quota = models.IntegerField(null=True, blank=True, verbose_name='할부개월수')
    
    # 시간 정보
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='결제 완료일')
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name='취소일')
    failed_at = models.DateTimeField(null=True, blank=True, verbose_name='실패일')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '결제 거래'
        verbose_name_plural = '결제 거래 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.merchant_uid} - {self.name} ({self.final_amount:,}원)"
    
    def save(self, *args, **kwargs):
        # 가맹점 주문번호 자동 생성
        if not self.merchant_uid:
            self.merchant_uid = f"SC_{timezone.now().strftime('%Y%m%d%H%M%S')}_{self.user.id}_{uuid.uuid4().hex[:8]}"
        
        # 최종 결제 금액 계산
        if not self.final_amount:
            self.final_amount = self.amount + self.fee_amount - self.discount_amount
        
        super().save(*args, **kwargs)


class PaymentRefund(models.Model):
    """결제 환불"""
    
    STATUS_CHOICES = [
        ('requested', '환불 요청'),
        ('processing', '환불 처리중'),
        ('completed', '환불 완료'),
        ('failed', '환불 실패'),
        ('rejected', '환불 거부'),
    ]
    
    REASON_CHOICES = [
        ('user_request', '사용자 요청'),
        ('service_issue', '서비스 이슈'),
        ('payment_error', '결제 오류'),
        ('duplicate_payment', '중복 결제'),
        ('other', '기타'),
    ]
    
    refund_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='환불 ID')
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.PROTECT, verbose_name='원본 거래')
    
    # 환불 정보
    amount = models.PositiveIntegerField(verbose_name='환불 금액(원)')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name='환불 사유')
    reason_detail = models.TextField(blank=True, verbose_name='환불 사유 상세')
    
    # 환불 상태
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested', verbose_name='환불 상태')
    
    # 외부 결제사 환불 정보
    imp_uid = models.CharField(max_length=100, blank=True, verbose_name='환불 거래번호')
    
    # 처리자 정보
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='requested_refunds', verbose_name='요청자')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds', verbose_name='처리자')
    
    # 시간 정보
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='요청일')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='처리일')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='완료일')
    
    class Meta:
        verbose_name = '결제 환불'
        verbose_name_plural = '결제 환불 목록'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"환불 {self.refund_id} - {self.amount:,}원"


class PaymentWebhook(models.Model):
    """결제 웹훅 로그"""
    
    webhook_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='웹훅 ID')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.PROTECT, verbose_name='결제 제공업체')
    
    # 웹훅 데이터
    event_type = models.CharField(max_length=50, verbose_name='이벤트 타입')
    imp_uid = models.CharField(max_length=100, blank=True, verbose_name='결제사 거래번호')
    merchant_uid = models.CharField(max_length=100, blank=True, verbose_name='가맹점 주문번호')
    
    # 원본 데이터
    raw_data = models.JSONField(verbose_name='원본 웹훅 데이터')
    headers = models.JSONField(default=dict, verbose_name='HTTP 헤더')
    
    # 처리 상태
    is_processed = models.BooleanField(default=False, verbose_name='처리 완료')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='처리일')
    error_message = models.TextField(blank=True, verbose_name='오류 메시지')
    
    # 연결된 거래
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='연결된 거래')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='수신일')
    
    class Meta:
        verbose_name = '결제 웹훅'
        verbose_name_plural = '결제 웹훅 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider.display_name} - {self.event_type} ({self.created_at})"


class PaymentConfig(models.Model):
    """결제 설정"""
    
    # 사이트 설정
    site_name = models.CharField(max_length=100, default='StockChart', verbose_name='사이트명')
    company_name = models.CharField(max_length=100, default='StockChart Inc.', verbose_name='회사명')
    business_number = models.CharField(max_length=20, blank=True, verbose_name='사업자등록번호')
    
    # 기본 결제 설정
    default_provider = models.ForeignKey(PaymentProvider, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='기본 결제 제공업체')
    min_payment_amount = models.IntegerField(default=1000, verbose_name='최소 결제금액(원)')
    max_payment_amount = models.IntegerField(default=10000000, verbose_name='최대 결제금액(원)')
    
    # 환불 설정
    auto_refund_enabled = models.BooleanField(default=False, verbose_name='자동 환불 허용')
    refund_deadline_days = models.IntegerField(default=7, verbose_name='환불 신청 기한(일)')
    
    # 이메일 알림 설정
    send_payment_notification = models.BooleanField(default=True, verbose_name='결제 완료 알림 발송')
    send_refund_notification = models.BooleanField(default=True, verbose_name='환불 완료 알림 발송')
    
    # 관리자 알림 설정
    admin_notification_email = models.EmailField(blank=True, verbose_name='관리자 알림 이메일')
    send_admin_notification = models.BooleanField(default=True, verbose_name='관리자 알림 발송')
    
    # 기타 설정
    test_mode = models.BooleanField(default=True, verbose_name='테스트 모드')
    webhook_verification_enabled = models.BooleanField(default=True, verbose_name='웹훅 검증 활성화')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '결제 설정'
        verbose_name_plural = '결제 설정'
    
    def __str__(self):
        return f"{self.site_name} 결제 설정"
    
    def save(self, *args, **kwargs):
        # 싱글톤 패턴 구현
        if not self.pk and PaymentConfig.objects.exists():
            raise ValueError('결제 설정은 하나만 존재할 수 있습니다.')
        super().save(*args, **kwargs)
