"""
국제 결제 시스템 Serializers
"""

from rest_framework import serializers
from decimal import Decimal
from .models import (
    InternationalPayment, ExchangeRate, PaymentWebhook,
    PaymentMethod, PaymentPlan
)


class InternationalPaymentSerializer(serializers.ModelSerializer):
    """국제 결제 Serializer"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    total_amount_with_fees = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = InternationalPayment
        fields = [
            'id', 'user', 'user_name', 'provider', 'provider_display',
            'payment_id', 'merchant_uid', 'amount_original', 'currency_original',
            'amount_converted', 'currency_converted', 'exchange_rate',
            'platform_fee', 'gateway_fee', 'total_fee', 'total_amount_with_fees',
            'status', 'status_display', 'payment_url', 'buyer_name', 'buyer_email',
            'buyer_country', 'product_name', 'product_description',
            'is_completed', 'is_pending', 'created_at', 'updated_at',
            'completed_at', 'failed_at'
        ]
        read_only_fields = [
            'id', 'user', 'payment_id', 'exchange_rate', 'platform_fee',
            'gateway_fee', 'total_fee', 'created_at', 'updated_at',
            'completed_at', 'failed_at'
        ]


class InternationalPaymentCreateSerializer(serializers.Serializer):
    """국제 결제 생성 Serializer"""
    
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('crypto', 'Crypto Gateway'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
    ]
    
    provider = serializers.ChoiceField(
        choices=PROVIDER_CHOICES,
        help_text="결제 제공업체를 선택하세요"
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=1000,
        help_text="결제 금액 (KRW 기준, 최소 1,000원)"
    )
    currency = serializers.ChoiceField(
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="결제 통화"
    )
    product_name = serializers.CharField(
        max_length=200,
        help_text="상품명"
    )
    product_description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="상품 설명 (선택사항)"
    )
    buyer_name = serializers.CharField(
        max_length=100,
        help_text="구매자 이름"
    )
    buyer_email = serializers.EmailField(
        help_text="구매자 이메일"
    )
    country = serializers.CharField(
        max_length=2,
        required=False,
        allow_blank=True,
        help_text="국가 코드 (2자리, 예: US, KR)"
    )
    success_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="결제 성공 시 리다이렉트 URL"
    )
    cancel_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="결제 취소 시 리다이렉트 URL"
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
        help_text="추가 메타데이터"
    )
    
    def validate_amount(self, value):
        """금액 유효성 검사"""
        if value < 1000:
            raise serializers.ValidationError("최소 결제 금액은 1,000원입니다.")
        if value > 10000000:  # 1천만원
            raise serializers.ValidationError("최대 결제 금액은 10,000,000원입니다.")
        return value
    
    def validate_country(self, value):
        """국가 코드 유효성 검사"""
        if value and len(value) != 2:
            raise serializers.ValidationError("국가 코드는 2자리여야 합니다.")
        return value.upper() if value else value


class ExchangeRateSerializer(serializers.ModelSerializer):
    """환율 Serializer"""
    
    class Meta:
        model = ExchangeRate
        fields = [
            'id', 'from_currency', 'to_currency', 'rate',
            'source', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """결제 웹훅 Serializer"""
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'provider', 'event_type', 'payment_id',
            'raw_data', 'processed', 'processed_at',
            'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentMethodEnhancedSerializer(serializers.ModelSerializer):
    """개선된 결제 수단 Serializer"""
    
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    supported_currencies = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'provider', 'provider_display',
            'is_active', 'icon_url', 'description',
            'supported_currencies'
        ]
    
    def get_supported_currencies(self, obj):
        """제공업체별 지원 통화"""
        currency_map = {
            'paypal': ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD'],
            'stripe': ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'SEK'],
            'coingate': ['USD', 'EUR', 'BTC', 'ETH', 'LTC'],
            'nowpayments': ['USD', 'EUR', 'BTC', 'ETH', 'LTC', 'XMR'],
            'moonpay': ['USD', 'EUR', 'GBP', 'BTC', 'ETH'],
            'binance_pay': ['USD', 'EUR', 'BTC', 'ETH', 'BNB'],
            'wise': ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'SGD'],
            'skrill': ['USD', 'EUR', 'GBP', 'JPY'],
            'neteller': ['USD', 'EUR', 'GBP', 'JPY']
        }
        return currency_map.get(obj.provider, ['USD'])


class PaymentPlanEnhancedSerializer(serializers.ModelSerializer):
    """개선된 결제 요금제 Serializer"""
    
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    price_usd_formatted = serializers.SerializerMethodField()
    price_krw_formatted = serializers.SerializerMethodField()
    duration_text = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentPlan
        fields = [
            'id', 'name', 'plan_type', 'plan_type_display',
            'price_krw', 'price_krw_formatted', 'price_usd', 'price_usd_formatted',
            'duration_days', 'duration_text', 'features', 'is_active', 'created_at'
        ]
    
    def get_price_usd_formatted(self, obj):
        """USD 가격 포맷팅"""
        return f"${obj.price_usd:.2f}"
    
    def get_price_krw_formatted(self, obj):
        """KRW 가격 포맷팅"""
        return f"₩{obj.price_krw:,.0f}"
    
    def get_duration_text(self, obj):
        """기간 텍스트"""
        if obj.duration_days == 30:
            return "1개월"
        elif obj.duration_days == 90:
            return "3개월"
        elif obj.duration_days == 365:
            return "1년"
        else:
            return f"{obj.duration_days}일"


class PaymentSummarySerializer(serializers.Serializer):
    """결제 요약 Serializer"""
    
    total_payments = serializers.IntegerField()
    total_amount_krw = serializers.DecimalField(max_digits=15, decimal_places=0)
    total_amount_usd = serializers.DecimalField(max_digits=15, decimal_places=2)
    completed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    avg_payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    most_used_provider = serializers.CharField()
    most_used_currency = serializers.CharField()


class CurrencyConversionSerializer(serializers.Serializer):
    """통화 변환 Serializer"""
    
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    converted_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    exchange_rate = serializers.DecimalField(max_digits=15, decimal_places=6, read_only=True)
    conversion_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    def validate(self, data):
        """통화 변환 유효성 검사"""
        from_currency = data['from_currency'].upper()
        to_currency = data['to_currency'].upper()
        
        # 지원되는 통화 목록
        supported_currencies = ['KRW', 'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'BTC', 'ETH']
        
        if from_currency not in supported_currencies:
            raise serializers.ValidationError(f"지원하지 않는 기준 통화입니다: {from_currency}")
        
        if to_currency not in supported_currencies:
            raise serializers.ValidationError(f"지원하지 않는 대상 통화입니다: {to_currency}")
        
        if from_currency == to_currency:
            raise serializers.ValidationError("기준 통화와 대상 통화가 같을 수 없습니다.")
        
        data['from_currency'] = from_currency
        data['to_currency'] = to_currency
        
        return data
