"""
소셜 인증 관리자 설정
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .social_models import (
    SocialProvider, SocialAccount, SocialLoginAttempt,
    SocialConnectRequest, SocialAuthConfig, SocialLoginSession
)


@admin.register(SocialProvider)
class SocialProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'display_name', 'is_active', 'accounts_count', 
        'created_at', 'icon_preview'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'display_name']
    readonly_fields = ['created_at', 'updated_at', 'accounts_count']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'display_name', 'icon_url', 'is_active')
        }),
        ('OAuth 설정', {
            'fields': ('client_id', 'client_secret', 'authorization_url', 
                      'token_url', 'user_info_url', 'scope')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('통계', {
            'fields': ('accounts_count',),
            'classes': ('collapse',)
        })
    )
    
    def accounts_count(self, obj):
        """연결된 계정 수"""
        count = obj.social_accounts.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:users_socialaccount_changelist')
            return format_html(
                '<a href="{}?provider__id__exact={}">{} 개</a>',
                url, obj.id, count
            )
        return '0 개'
    accounts_count.short_description = '연결된 계정'
    
    def icon_preview(self, obj):
        """아이콘 미리보기"""
        if obj.icon_url:
            return format_html(
                '<img src="{}" width="32" height="32" style="border-radius: 4px;" />',
                obj.icon_url
            )
        return '-'
    icon_preview.short_description = '아이콘'


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'provider', 'social_id', 'email', 'name',
        'is_verified', 'is_primary', 'last_login_at'
    ]
    list_filter = [
        'provider', 'is_verified', 'is_primary',
        'last_login_at', 'created_at'
    ]
    search_fields = ['user__username', 'user__email', 'social_id', 'email', 'name']
    readonly_fields = [
        'user', 'provider', 'social_id', 'email', 'name',
        'profile_image_url', 'access_token_preview', 'refresh_token_preview',
        'token_expires_at', 'extra_data', 'created_at', 'updated_at',
        'last_login_at'
    ]
    
    fieldsets = (
        ('사용자 정보', {
            'fields': ('user', 'provider', 'social_id')
        }),
        ('프로필 정보', {
            'fields': ('email', 'name', 'profile_image_url', 'is_verified')
        }),
        ('계정 설정', {
            'fields': ('is_primary',)
        }),
        ('토큰 정보', {
            'fields': ('access_token_preview', 'refresh_token_preview', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('추가 데이터', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at', 'last_login_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['set_as_primary']
    
    def user_link(self, obj):
        """사용자 링크"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = '사용자'
    
    def access_token_preview(self, obj):
        """액세스 토큰 미리보기"""
        if obj.access_token:
            return f"{obj.access_token[:20]}..." if len(obj.access_token) > 20 else obj.access_token
        return '-'
    access_token_preview.short_description = '액세스 토큰'
    
    def refresh_token_preview(self, obj):
        """리프레시 토큰 미리보기"""
        if obj.refresh_token:
            return f"{obj.refresh_token[:20]}..." if len(obj.refresh_token) > 20 else obj.refresh_token
        return '-'
    refresh_token_preview.short_description = '리프레시 토큰'
    
    def set_as_primary(self, request, queryset):
        """주 계정으로 설정"""
        for account in queryset:
            account.set_as_primary()
        self.message_user(request, f'{queryset.count()}개의 계정이 주 계정으로 설정되었습니다.')
    set_as_primary.short_description = '주 계정으로 설정'


@admin.register(SocialLoginAttempt)
class SocialLoginAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'provider', 'social_id', 'status',
        'ip_address', 'created_at', 'completed_at'
    ]
    list_filter = [
        'provider', 'status', 'created_at', 'completed_at'
    ]
    search_fields = ['user__username', 'social_id', 'ip_address', 'state_token']
    readonly_fields = [
        'provider', 'user', 'social_id', 'state_token', 'status',
        'ip_address', 'user_agent', 'extra_data',
        'created_at', 'completed_at'
    ]
    
    fieldsets = (
        ('로그인 정보', {
            'fields': ('provider', 'user', 'social_id', 'status')
        }),
        ('세션 정보', {
            'fields': ('state_token', 'ip_address', 'user_agent')
        }),
        ('추가 데이터', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'completed_at')
        })
    )
    
    def user_link(self, obj):
        """사용자 링크"""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = '사용자'
    
    def has_add_permission(self, request):
        return False


@admin.register(SocialConnectRequest)
class SocialConnectRequestAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'provider', 'status',
        'created_at', 'expires_at'
    ]
    list_filter = ['provider', 'status', 'created_at', 'expires_at']
    search_fields = ['user__username', 'verification_token']
    readonly_fields = [
        'user', 'provider', 'verification_token', 'status',
        'created_at', 'expires_at', 'processed_at'
    ]
    
    fieldsets = (
        ('연결 요청 정보', {
            'fields': ('user', 'provider', 'verification_token', 'status')
        }),
        ('소셜 정보', {
            'fields': ('social_id', 'social_email', 'social_name')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'expires_at', 'processed_at')
        })
    )
    
    def user_link(self, obj):
        """사용자 링크"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = '사용자'
    
    def has_add_permission(self, request):
        return False


@admin.register(SocialAuthConfig)
class SocialAuthConfigAdmin(admin.ModelAdmin):
    list_display = [
        'provider', 'auto_create_user', 'require_email_verification',
        'default_user_type', 'sync_profile_data', 'sync_on_login'
    ]
    list_filter = [
        'auto_create_user', 'require_email_verification',
        'default_user_type', 'sync_profile_data', 'sync_on_login'
    ]
    search_fields = ['provider__name', 'provider__display_name']
    readonly_fields = ['provider', 'created_at', 'updated_at']
    
    fieldsets = (
        ('제공업체', {
            'fields': ('provider',)
        }),
        ('사용자 생성 설정', {
            'fields': ('auto_create_user', 'require_email_verification', 'default_user_type')
        }),
        ('프로필 동기화', {
            'fields': ('sync_profile_data', 'sync_on_login')
        }),
        ('추가 설정', {
            'fields': ('additional_scopes', 'custom_redirect_url')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(SocialLoginSession)
class SocialLoginSessionAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'provider', 'session_id_short', 'ip_address',
        'is_active', 'created_at', 'last_accessed_at'
    ]
    list_filter = [
        'provider', 'is_active',
        'created_at', 'last_accessed_at'
    ]
    search_fields = ['user__username', 'session_key', 'ip_address']
    readonly_fields = [
        'user', 'provider', 'session_key',
        'ip_address', 'user_agent', 'is_active',
        'created_at', 'last_accessed_at'
    ]
    
    fieldsets = (
        ('세션 정보', {
            'fields': ('user', 'provider', 'session_key', 'is_active')
        }),
        ('액세스 정보', {
            'fields': ('access_token', 'refresh_token', 'expires_at')
        }),
        ('접속 정보', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'last_accessed_at')
        })
    )
    
    actions = ['end_sessions']
    
    def user_link(self, obj):
        """사용자 링크"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = '사용자'
    
    def session_id_short(self, obj):
        """세션 ID 축약"""
        return str(obj.session_key)[:8] + '...'
    session_id_short.short_description = '세션 ID'
    
    def end_sessions(self, request, queryset):
        """세션 종료"""
        for session in queryset:
            session.deactivate()
        self.message_user(request, f'{queryset.count()}개의 세션이 종료되었습니다.')
    end_sessions.short_description = '선택된 세션 종료'
    
    def has_add_permission(self, request):
        return False


# 커스텀 관리자 액션

def export_social_accounts_csv(modeladmin, request, queryset):
    """소셜 계정 CSV 내보내기"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="social_accounts.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'User ID', 'Username', 'Email', 'Provider', 'Social ID',
        'Is Verified', 'Is Primary', 'Created At', 'Last Login'
    ])
    
    for account in queryset:
        writer.writerow([
            account.user.id,
            account.user.username,
            account.email,
            account.provider.name,
            account.social_id,
            account.is_verified,
            account.is_primary,
            account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            account.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if account.last_login_at else ''
        ])
    
    return response

export_social_accounts_csv.short_description = 'CSV로 내보내기'

# 액션을 SocialAccount 관리자에 추가
SocialAccountAdmin.actions.append(export_social_accounts_csv)
