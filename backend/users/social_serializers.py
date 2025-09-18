"""
소셜 인증 시리얼라이저
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .social_models import (
    SocialProvider, SocialAccount, SocialLoginAttempt,
    SocialConnectRequest, SocialAuthConfig, SocialLoginSession
)

User = get_user_model()


class SocialProviderSerializer(serializers.ModelSerializer):
    """소셜 제공업체 시리얼라이저"""
    
    class Meta:
        model = SocialProvider
        fields = [
            'id', 'name', 'display_name', 'icon_url', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SocialAccountSerializer(serializers.ModelSerializer):
    """소셜 계정 시리얼라이저"""
    provider = SocialProviderSerializer(read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_display_name = serializers.CharField(source='provider.display_name', read_only=True)
    
    class Meta:
        model = SocialAccount
        fields = [
            'id', 'provider', 'provider_name', 'provider_display_name',
            'social_id', 'email', 'name', 'profile_image_url',
            'is_verified', 'is_primary', 'is_active',
            'last_login_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'provider', 'provider_name', 'provider_display_name',
            'social_id', 'email', 'name', 'profile_image_url',
            'is_verified', 'last_login_at', 'created_at', 'updated_at'
        ]


class SocialLoginAttemptSerializer(serializers.ModelSerializer):
    """소셜 로그인 시도 시리얼라이저"""
    provider = SocialProviderSerializer(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SocialLoginAttempt
        fields = [
            'id', 'provider', 'user', 'user_username',
            'social_id', 'state_token', 'status',
            'ip_address', 'user_agent', 'extra_data',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'provider', 'user', 'user_username',
            'social_id', 'state_token', 'status',
            'ip_address', 'user_agent', 'extra_data',
            'created_at', 'completed_at'
        ]


class SocialConnectRequestSerializer(serializers.ModelSerializer):
    """소셜 계정 연결 요청 시리얼라이저"""
    provider = SocialProviderSerializer(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SocialConnectRequest
        fields = [
            'id', 'user', 'user_username', 'provider',
            'request_token', 'status', 'ip_address', 'user_agent',
            'created_at', 'completed_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_username', 'provider',
            'request_token', 'status', 'ip_address', 'user_agent',
            'created_at', 'completed_at', 'expires_at'
        ]


class SocialAuthConfigSerializer(serializers.ModelSerializer):
    """소셜 인증 설정 시리얼라이저"""
    provider = SocialProviderSerializer(read_only=True)
    
    class Meta:
        model = SocialAuthConfig
        fields = [
            'id', 'provider', 'auto_create_user', 'require_email_verification',
            'default_user_type', 'sync_profile_data', 'sync_on_login',
            'additional_scopes', 'custom_redirect_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'provider', 'created_at', 'updated_at']


class SocialLoginSessionSerializer(serializers.ModelSerializer):
    """소셜 로그인 세션 시리얼라이저"""
    provider = SocialProviderSerializer(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    login_attempt = SocialLoginAttemptSerializer(read_only=True)
    
    class Meta:
        model = SocialLoginSession
        fields = [
            'id', 'user', 'user_username', 'provider', 'login_attempt',
            'session_id', 'ip_address', 'user_agent', 'is_mobile',
            'is_active', 'created_at', 'last_accessed_at', 'logged_out_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_username', 'provider', 'login_attempt',
            'session_id', 'ip_address', 'user_agent', 'is_mobile',
            'is_active', 'created_at', 'last_accessed_at', 'logged_out_at'
        ]


# 입력용 시리얼라이저들

class SocialLoginInitiateSerializer(serializers.Serializer):
    """소셜 로그인 시작 시리얼라이저"""
    provider = serializers.CharField(max_length=50)
    redirect_url = serializers.URLField(required=False)
    
    def validate_provider(self, value):
        """제공업체 유효성 검사"""
        if not SocialProvider.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("지원하지 않는 소셜 제공업체입니다.")
        return value


class SocialLoginCallbackSerializer(serializers.Serializer):
    """소셜 로그인 콜백 시리얼라이저"""
    code = serializers.CharField(max_length=500)
    state = serializers.CharField(max_length=100)
    error = serializers.CharField(max_length=100, required=False)
    error_description = serializers.CharField(max_length=500, required=False)


class SocialAccountDisconnectSerializer(serializers.Serializer):
    """소셜 계정 연결 해제 시리얼라이저"""
    provider = serializers.CharField(max_length=50)
    social_id = serializers.CharField(max_length=100, required=False)
    
    def validate_provider(self, value):
        """제공업체 유효성 검사"""
        if not SocialProvider.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("지원하지 않는 소셜 제공업체입니다.")
        return value


class SocialAccountConnectSerializer(serializers.Serializer):
    """소셜 계정 연결 시리얼라이저"""
    provider = serializers.CharField(max_length=50)
    
    def validate_provider(self, value):
        """제공업체 유효성 검사"""
        if not SocialProvider.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("지원하지 않는 소셜 제공업체입니다.")
        return value


class RefreshSocialTokenSerializer(serializers.Serializer):
    """소셜 토큰 갱신 시리얼라이저"""
    provider = serializers.CharField(max_length=50)
    
    def validate_provider(self, value):
        """제공업체 유효성 검사"""
        if not SocialProvider.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("지원하지 않는 소셜 제공업체입니다.")
        return value


class SocialLogoutSerializer(serializers.Serializer):
    """소셜 로그아웃 시리얼라이저"""
    session_id = serializers.UUIDField(required=False)
    logout_all_sessions = serializers.BooleanField(default=False)


# 응답용 시리얼라이저들

class SocialAuthResponseSerializer(serializers.Serializer):
    """소셜 인증 응답 시리얼라이저"""
    success = serializers.BooleanField()
    user_created = serializers.BooleanField()
    user = serializers.DictField()
    tokens = serializers.DictField()
    social_account = serializers.DictField()
    session_id = serializers.UUIDField()


class SocialProviderListResponseSerializer(serializers.Serializer):
    """소셜 제공업체 목록 응답 시리얼라이저"""
    providers = SocialProviderSerializer(many=True)
    total_count = serializers.IntegerField()


class SocialAccountListResponseSerializer(serializers.Serializer):
    """소셜 계정 목록 응답 시리얼라이저"""
    social_accounts = SocialAccountSerializer(many=True)
    total_count = serializers.IntegerField()


class SocialAuthStatsSerializer(serializers.Serializer):
    """소셜 인증 통계 시리얼라이저"""
    total_social_accounts = serializers.IntegerField()
    accounts_by_provider = serializers.ListField()
    recent_logins = serializers.IntegerField()
    failed_logins = serializers.IntegerField()
    active_sessions = serializers.IntegerField()


# 관리자용 시리얼라이저들

class AdminSocialProviderSerializer(serializers.ModelSerializer):
    """관리자용 소셜 제공업체 시리얼라이저"""
    
    class Meta:
        model = SocialProvider
        fields = [
            'id', 'name', 'display_name', 'client_id', 'client_secret',
            'authorization_url', 'token_url', 'user_info_url', 'scope',
            'icon_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'client_secret': {'write_only': True}
        }


class AdminSocialAuthConfigSerializer(serializers.ModelSerializer):
    """관리자용 소셜 인증 설정 시리얼라이저"""
    provider = AdminSocialProviderSerializer(read_only=True)
    
    class Meta:
        model = SocialAuthConfig
        fields = [
            'id', 'provider', 'auto_create_user', 'require_email_verification',
            'default_user_type', 'sync_profile_data', 'sync_on_login',
            'additional_scopes', 'custom_redirect_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'provider', 'created_at', 'updated_at']


class AdminSocialAccountSerializer(serializers.ModelSerializer):
    """관리자용 소셜 계정 시리얼라이저"""
    provider = SocialProviderSerializer(read_only=True)
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialAccount
        fields = [
            'id', 'user', 'user_info', 'provider', 'social_id',
            'email', 'name', 'profile_image_url', 'is_verified',
            'is_primary', 'is_active', 'token_expires_at',
            'last_login_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_info', 'provider', 'social_id',
            'email', 'name', 'profile_image_url', 'token_expires_at',
            'last_login_at', 'created_at', 'updated_at'
        ]
    
    def get_user_info(self, obj):
        """사용자 기본 정보 반환"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'is_active': obj.user.is_active,
            'date_joined': obj.user.date_joined.isoformat()
        }
