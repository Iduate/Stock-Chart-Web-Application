"""
Serializers for the payments app
"""
from rest_framework import serializers
from .models import PaymentPlan, Payment, PaymentMethod, Coupon

# Re-export international serializers so other modules can import from payments.serializers
try:
    from .international_serializers import (
        InternationalPaymentSerializer,
        InternationalPaymentCreateSerializer,
        ExchangeRateSerializer,
        PaymentWebhookSerializer,
    )
except Exception:
    # During partial imports (e.g., migrations) these modules may not be available;
    # ignore so local serializers below still load.
    pass

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['transaction_id', 'external_payment_id', 'status']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
