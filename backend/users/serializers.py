from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, Subscription

# 소셜 인증 시리얼라이저 임포트
try:
    from .social_serializers import (
        SocialAccountSerializer,
        SocialProviderSerializer,
        SocialLoginSessionSerializer
    )
except ImportError:
    # 소셜 인증 모듈이 없는 경우 스킵
    pass

class UserSerializer(serializers.ModelSerializer):
    """사용자 시리얼라이저"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'subscription_status', 'free_access_count',
            'total_profit', 'prediction_accuracy', 'referral_code',
            'phone_number', 'language_preference', 'created_at',
            'password', 'password_confirm'
        ]
        read_only_fields = [
            'id', 'user_type', 'subscription_status', 'free_access_count',
            'total_profit', 'prediction_accuracy', 'referral_code', 'created_at'
        ]
    
    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 시리얼라이저"""
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_info', 'avatar', 'bio', 'website',
            'location', 'birth_date'
        ]
        read_only_fields = ['id', 'user']

class SubscriptionSerializer(serializers.ModelSerializer):
    """구독 시리얼라이저"""
    user_info = UserSerializer(source='user', read_only=True)
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_info', 'plan', 'plan_display',
            'status', 'status_display', 'start_date', 'end_date',
            'payment_id', 'amount', 'currency', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
