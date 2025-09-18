from rest_framework import serializers
from .models import PaymentProvider, PaymentMethod, PaymentTransaction, PaymentRefund, PaymentConfig


class PaymentProviderSerializer(serializers.ModelSerializer):
    """결제 제공업체 시리얼라이저"""
    
    class Meta:
        model = PaymentProvider
        fields = [
            'name', 'display_name', 'is_active', 'is_korean',
            'supports_card', 'supports_bank', 'supports_vbank', 
            'supports_phone', 'supports_point',
            'card_fee_rate', 'bank_fee_rate', 'vbank_fee_amount',
            'min_amount', 'max_amount'
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    """결제 수단 시리얼라이저"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'code', 'name', 'icon', 'is_active', 'is_korean',
            'requires_identity_verification', 'min_amount', 'max_amount',
            'display_order'
        ]


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """결제 거래 시리얼라이저"""
    
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'transaction_id', 'merchant_uid', 'user_username',
            'provider_name', 'payment_method_name',
            'amount', 'fee_amount', 'discount_amount', 'final_amount',
            'status', 'imp_uid', 'pg_tid', 'pg_provider',
            'name', 'description',
            'buyer_name', 'buyer_email', 'buyer_tel',
            'vbank_num', 'vbank_name', 'vbank_holder', 'vbank_date',
            'card_name', 'card_number', 'card_quota',
            'paid_at', 'cancelled_at', 'failed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'transaction_id', 'user_username', 'imp_uid', 'pg_tid',
            'paid_at', 'cancelled_at', 'failed_at', 'created_at', 'updated_at'
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """결제 생성 요청 시리얼라이저"""
    
    provider = serializers.CharField(max_length=50, help_text='결제 제공업체 (iamport, toss, kakaopay 등)')
    payment_method = serializers.CharField(max_length=20, help_text='결제 수단 (card, bank, vbank 등)')
    amount = serializers.IntegerField(min_value=100, help_text='결제 금액 (원)')
    name = serializers.CharField(max_length=200, help_text='상품명')
    description = serializers.CharField(max_length=500, required=False, help_text='상품 설명')
    
    # 구매자 정보
    buyer_name = serializers.CharField(max_length=50, help_text='구매자명')
    buyer_email = serializers.EmailField(help_text='구매자 이메일')
    buyer_tel = serializers.CharField(max_length=20, required=False, help_text='구매자 연락처')
    buyer_addr = serializers.CharField(max_length=255, required=False, help_text='구매자 주소')
    buyer_postcode = serializers.CharField(max_length=10, required=False, help_text='구매자 우편번호')
    
    # 리다이렉트 URL
    success_url = serializers.URLField(required=False, help_text='결제 성공 시 리다이렉트 URL')
    cancel_url = serializers.URLField(required=False, help_text='결제 취소 시 리다이렉트 URL')
    fail_url = serializers.URLField(required=False, help_text='결제 실패 시 리다이렉트 URL')
    
    # 추가 옵션
    card_quota = serializers.IntegerField(required=False, help_text='카드 할부 개월수 (0=일시불)')
    vbank_due = serializers.DateTimeField(required=False, help_text='가상계좌 입금 기한')


class PaymentVerifySerializer(serializers.Serializer):
    """결제 검증 요청 시리얼라이저"""
    
    provider = serializers.CharField(max_length=50, help_text='결제 제공업체')
    imp_uid = serializers.CharField(max_length=100, required=False, help_text='결제사 거래번호')
    payment_key = serializers.CharField(max_length=100, required=False, help_text='결제 키 (토스페이먼츠)')
    merchant_uid = serializers.CharField(max_length=100, help_text='가맹점 주문번호')
    amount = serializers.IntegerField(help_text='결제 금액 검증용')


class PaymentCancelSerializer(serializers.Serializer):
    """결제 취소 요청 시리얼라이저"""
    
    reason = serializers.CharField(max_length=500, help_text='취소 사유')
    amount = serializers.IntegerField(required=False, help_text='부분 취소 금액 (전액 취소시 생략)')


class PaymentRefundSerializer(serializers.ModelSerializer):
    """환불 시리얼라이저"""
    
    transaction_merchant_uid = serializers.CharField(source='transaction.merchant_uid', read_only=True)
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    processed_by_username = serializers.CharField(source='processed_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = PaymentRefund
        fields = [
            'refund_id', 'transaction_merchant_uid',
            'amount', 'reason', 'reason_detail', 'status',
            'requested_by_username', 'processed_by_username',
            'requested_at', 'processed_at', 'completed_at'
        ]
        read_only_fields = [
            'refund_id', 'requested_by_username', 'processed_by_username',
            'requested_at', 'processed_at', 'completed_at'
        ]


class PaymentRefundCreateSerializer(serializers.Serializer):
    """환불 요청 생성 시리얼라이저"""
    
    transaction_id = serializers.UUIDField(help_text='원본 거래 ID')
    amount = serializers.IntegerField(min_value=100, help_text='환불 금액')
    reason = serializers.ChoiceField(
        choices=PaymentRefund.REASON_CHOICES,
        help_text='환불 사유'
    )
    reason_detail = serializers.CharField(
        max_length=1000, 
        required=False, 
        help_text='환불 사유 상세'
    )


class PaymentConfigSerializer(serializers.ModelSerializer):
    """결제 설정 시리얼라이저"""
    
    default_provider_name = serializers.CharField(source='default_provider.display_name', read_only=True)
    
    class Meta:
        model = PaymentConfig
        fields = [
            'site_name', 'company_name', 'business_number',
            'default_provider_name', 'min_payment_amount', 'max_payment_amount',
            'auto_refund_enabled', 'refund_deadline_days',
            'send_payment_notification', 'send_refund_notification',
            'admin_notification_email', 'send_admin_notification',
            'test_mode', 'webhook_verification_enabled'
        ]


class PaymentStatsSerializer(serializers.Serializer):
    """결제 통계 시리얼라이저"""
    
    period = serializers.CharField(help_text='통계 기간 (daily, weekly, monthly)')
    total_transactions = serializers.IntegerField(help_text='총 거래 수')
    total_amount = serializers.IntegerField(help_text='총 결제 금액')
    successful_transactions = serializers.IntegerField(help_text='성공한 거래 수')
    failed_transactions = serializers.IntegerField(help_text='실패한 거래 수')
    cancelled_transactions = serializers.IntegerField(help_text='취소된 거래 수')
    success_rate = serializers.FloatField(help_text='결제 성공률 (%)')
    
    # 결제 수단별 통계
    payment_method_stats = serializers.DictField(help_text='결제 수단별 통계')
    
    # 제공업체별 통계
    provider_stats = serializers.DictField(help_text='제공업체별 통계')
    
    # 일자별 통계 (주간/월간일 때)
    daily_stats = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text='일자별 상세 통계'
    )
