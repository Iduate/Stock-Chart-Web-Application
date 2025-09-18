from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import User, UserProfile, Subscription

# 소셜 인증 관리자 임포트
try:
    from .social_admin import *
except ImportError:
    # 소셜 인증 모듈이 없는 경우 스킵
    pass

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """사용자 관리자"""
    
    list_display = ('username', 'email', 'user_type', 'subscription_status', 'free_access_count', 'total_profit', 'created_at')
    list_filter = ('user_type', 'subscription_status', 'social_provider', 'language_preference', 'created_at')
    search_fields = ('username', 'email', 'referral_code')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('개인 정보'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('권한'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('중요한 날짜'), {'fields': ('last_login', 'date_joined')}),
        (_('사용자 설정'), {
            'fields': ('user_type', 'subscription_status', 'free_access_count', 'referral_code', 'referred_by')
        }),
        (_('통계'), {
            'fields': ('total_profit', 'prediction_accuracy')
        }),
        (_('소셜 로그인'), {
            'fields': ('social_provider', 'social_id')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """사용자 프로필 관리자"""
    
    list_display = ('user', 'location', 'birth_date')
    search_fields = ('user__username', 'user__email', 'location')
    list_filter = ('location',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """구독 관리자"""
    
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'amount')
    list_filter = ('plan', 'status', 'currency', 'created_at')
    search_fields = ('user__username', 'user__email', 'payment_id')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
