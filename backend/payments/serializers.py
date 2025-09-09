"""
Serializers for the payments app
"""
from rest_framework import serializers
from .models import PaymentPlan, Payment, PaymentMethod, Coupon

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
