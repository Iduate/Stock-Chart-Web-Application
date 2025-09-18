from django.db import models
from django.conf import settings

class PaymentMethod(models.Model):
    """결제 수단"""
    
    PROVIDER_CHOICES = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('coingate', 'CoinGate'),
        ('nowpayments', 'NOWPayments'),
        ('moonpay', 'MoonPay'),
        ('binance_pay', 'Binance Pay'),
        ('wise', 'Wise (TransferWise)'),
        ('skrill', 'Skrill'),
        ('neteller', 'Neteller'),
    ]
    
    name = models.CharField('결제 수단명', max_length=100)
    provider = models.CharField('제공업체', max_length=50, choices=PROVIDER_CHOICES)
    is_active = models.BooleanField('활성 상태', default=True)
    icon_url = models.URLField('아이콘 URL', blank=True)
    description = models.TextField('설명', blank=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '결제 수단'
        verbose_name_plural = '결제 수단들'
    
    def __str__(self):
        return self.name

class PaymentPlan(models.Model):
    """결제 요금제"""
    
    PLAN_TYPE_CHOICES = [
        ('basic', '기본'),
        ('premium', '프리미엄'),
        ('pro', '프로'),
    ]
    
    name = models.CharField('요금제명', max_length=100)
    plan_type = models.CharField('요금제 유형', max_length=20, choices=PLAN_TYPE_CHOICES)
    price_krw = models.DecimalField('가격(원)', max_digits=10, decimal_places=0)
    price_usd = models.DecimalField('가격(달러)', max_digits=10, decimal_places=2)
    duration_days = models.IntegerField('기간(일)')
    features = models.JSONField('기능 목록', default=list)
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '결제 요금제'
        verbose_name_plural = '결제 요금제들'
    
    def __str__(self):
        return f"{self.name} - {self.price_krw}원"

class Payment(models.Model):
    """결제 내역"""
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('completed', '완료'),
        ('failed', '실패'),
        ('cancelled', '취소'),
        ('refunded', '환불'),
    ]
    
    CURRENCY_CHOICES = [
        ('KRW', '한국 원'),
        ('USD', '미국 달러'),
        ('BTC', '비트코인'),
        ('ETH', '이더리움'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, verbose_name='요금제')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name='결제 수단')
    amount = models.DecimalField('결제 금액', max_digits=15, decimal_places=8)
    currency = models.CharField('통화', max_length=10, choices=CURRENCY_CHOICES)
    exchange_rate = models.DecimalField('환율', max_digits=15, decimal_places=8, null=True, blank=True)
    status = models.CharField('결제 상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField('거래 ID', max_length=200, unique=True)
    external_payment_id = models.CharField('외부 결제 ID', max_length=200, blank=True)
    payment_url = models.URLField('결제 URL', blank=True)
    callback_data = models.JSONField('콜백 데이터', default=dict, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    completed_at = models.DateTimeField('완료일', null=True, blank=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '결제'
        verbose_name_plural = '결제들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} - {self.amount} {self.currency}"

class Coupon(models.Model):
    """쿠폰"""
    
    COUPON_TYPE_CHOICES = [
        ('percentage', '퍼센트 할인'),
        ('fixed', '고정 할인'),
        ('free_access', '무료 이용권'),
    ]
    
    code = models.CharField('쿠폰 코드', max_length=50, unique=True)
    name = models.CharField('쿠폰명', max_length=100)
    coupon_type = models.CharField('쿠폰 유형', max_length=20, choices=COUPON_TYPE_CHOICES)
    discount_value = models.DecimalField('할인 값', max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField('최소 구매 금액', max_digits=10, decimal_places=2, default=0)
    max_usage_count = models.IntegerField('최대 사용 횟수', null=True, blank=True)
    used_count = models.IntegerField('사용된 횟수', default=0)
    valid_from = models.DateTimeField('유효 시작일')
    valid_until = models.DateTimeField('유효 종료일')
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '쿠폰'
        verbose_name_plural = '쿠폰들'
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class CouponUsage(models.Model):
    """쿠폰 사용 내역"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name='쿠폰')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True, verbose_name='결제')
    discount_amount = models.DecimalField('할인 금액', max_digits=10, decimal_places=2)
    used_at = models.DateTimeField('사용일', auto_now_add=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '쿠폰 사용 내역'
        verbose_name_plural = '쿠폰 사용 내역들'
        unique_together = ['user', 'coupon']

class Referral(models.Model):
    """추천 프로그램"""
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='referrals_made', on_delete=models.CASCADE, verbose_name='추천인')
    referred = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='referrals_received', on_delete=models.CASCADE, verbose_name='피추천인')
    commission_rate = models.DecimalField('수수료율(%)', max_digits=5, decimal_places=2, default=10)
    total_commission = models.DecimalField('총 수수료', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '추천'
        verbose_name_plural = '추천들'
        unique_together = ['referrer', 'referred']

class CommissionPayment(models.Model):
    """수수료 지급"""
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('paid', '지급완료'),
        ('cancelled', '취소'),
    ]
    
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, verbose_name='추천')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, verbose_name='원본 결제')
    commission_amount = models.DecimalField('수수료 금액', max_digits=10, decimal_places=2)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField('지급일', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '수수료 지급'
        verbose_name_plural = '수수료 지급들'


class InternationalPayment(models.Model):
    """국제 결제 거래"""
    
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('crypto', 'Crypto Gateway'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('processing', '처리중'),
        ('completed', '완료'),
        ('failed', '실패'),
        ('cancelled', '취소'),
        ('refunded', '환불'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('KRW', 'Korean Won'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
    ]
    
    # 기본 정보
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    provider = models.CharField('결제 제공업체', max_length=20, choices=PROVIDER_CHOICES)
    payment_id = models.CharField('결제 ID', max_length=255, unique=True)
    merchant_uid = models.CharField('가맹점 거래 ID', max_length=100)
    
    # 금액 정보
    amount_original = models.DecimalField('원래 금액', max_digits=15, decimal_places=2)
    currency_original = models.CharField('원래 통화', max_length=3, default='KRW')
    amount_converted = models.DecimalField('변환 금액', max_digits=15, decimal_places=2)
    currency_converted = models.CharField('변환 통화', max_length=3, choices=CURRENCY_CHOICES)
    exchange_rate = models.DecimalField('환율', max_digits=15, decimal_places=6, default=1)
    
    # 수수료 정보
    platform_fee = models.DecimalField('플랫폼 수수료', max_digits=10, decimal_places=2, default=0)
    gateway_fee = models.DecimalField('게이트웨이 수수료', max_digits=10, decimal_places=2, default=0)
    total_fee = models.DecimalField('총 수수료', max_digits=10, decimal_places=2, default=0)
    
    # 상태 정보
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_url = models.URLField('결제 URL', blank=True)
    client_secret = models.CharField('클라이언트 시크릿', max_length=255, blank=True)
    
    # 구매자 정보
    buyer_name = models.CharField('구매자명', max_length=100)
    buyer_email = models.EmailField('구매자 이메일')
    buyer_country = models.CharField('구매자 국가', max_length=2, blank=True)
    
    # 상품 정보
    product_name = models.CharField('상품명', max_length=200)
    product_description = models.TextField('상품 설명', blank=True)
    
    # 추가 데이터
    gateway_response = models.JSONField('게이트웨이 응답', default=dict, blank=True)
    metadata = models.JSONField('메타데이터', default=dict, blank=True)
    
    # 시간 정보
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    completed_at = models.DateTimeField('완료일', null=True, blank=True)
    failed_at = models.DateTimeField('실패일', null=True, blank=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '국제 결제'
        verbose_name_plural = '국제 결제들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider} - {self.merchant_uid} - {self.amount_converted} {self.currency_converted}"
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def total_amount_with_fees(self):
        return self.amount_converted + self.total_fee


class ExchangeRate(models.Model):
    """환율 정보"""
    
    from_currency = models.CharField('기준 통화', max_length=3)
    to_currency = models.CharField('대상 통화', max_length=3)
    rate = models.DecimalField('환율', max_digits=15, decimal_places=6)
    source = models.CharField('환율 소스', max_length=50, default='manual')
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '환율'
        verbose_name_plural = '환율들'
        unique_together = ['from_currency', 'to_currency']
    
    def __str__(self):
        return f"{self.from_currency}/{self.to_currency}: {self.rate}"


class PaymentWebhook(models.Model):
    """결제 웹훅 로그"""
    
    provider = models.CharField('제공업체', max_length=20)
    event_type = models.CharField('이벤트 유형', max_length=50)
    payment_id = models.CharField('결제 ID', max_length=255, blank=True)
    raw_data = models.JSONField('원본 데이터', default=dict)
    processed = models.BooleanField('처리 완료', default=False)
    processed_at = models.DateTimeField('처리일', null=True, blank=True)
    error_message = models.TextField('오류 메시지', blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = '결제 웹훅'
        verbose_name_plural = '결제 웹훅들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider} - {self.event_type} - {self.created_at}"
