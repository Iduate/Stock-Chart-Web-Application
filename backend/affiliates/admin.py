from django.contrib import admin
from .models import (
    AffiliatePartner, ReferralLink, ReferralClick, 
    CommissionTransaction, PartnerPerformance, PartnerMaterial
)


@admin.register(AffiliatePartner)
class AffiliatePartnerAdmin(admin.ModelAdmin):
    list_display = ['partner_code', 'user', 'company_name', 'status', 'total_referrals', 'total_commission_earned', 'applied_at']
    list_filter = ['status', 'commission_type', 'applied_at', 'approved_at']
    search_fields = ['partner_code', 'user__username', 'company_name', 'phone_number']
    readonly_fields = ['partner_code', 'total_referrals', 'total_conversions', 'total_commission_earned', 'total_commission_paid']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'partner_code', 'company_name', 'business_registration', 'phone_number', 'website')
        }),
        ('상태 및 수수료', {
            'fields': ('status', 'commission_type', 'commission_rate', 'fixed_commission')
        }),
        ('통계', {
            'fields': ('total_referrals', 'total_conversions', 'total_commission_earned', 'total_commission_paid'),
            'classes': ('collapse',)
        }),
        ('지급 설정', {
            'fields': ('minimum_payout', 'payout_method', 'bank_info'),
            'classes': ('collapse',)
        }),
        ('날짜', {
            'fields': ('applied_at', 'approved_at', 'last_payout_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_partners', 'suspend_partners']
    
    def approve_partners(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated}개 파트너가 승인되었습니다.')
    approve_partners.short_description = '선택된 파트너 승인'
    
    def suspend_partners(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated}개 파트너가 일시정지되었습니다.')
    suspend_partners.short_description = '선택된 파트너 일시정지'


@admin.register(ReferralLink)
class ReferralLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner', 'target_url', 'click_count', 'conversion_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'partner__status']
    search_fields = ['name', 'partner__partner_code', 'target_url']
    readonly_fields = ['link_id', 'click_count', 'conversion_count']


@admin.register(ReferralClick)
class ReferralClickAdmin(admin.ModelAdmin):
    list_display = ['link', 'ip_address', 'converted', 'clicked_at', 'converted_at']
    list_filter = ['converted', 'clicked_at', 'link__partner']
    search_fields = ['ip_address', 'link__name', 'link__partner__partner_code']
    readonly_fields = ['clicked_at', 'converted_at']


@admin.register(CommissionTransaction)
class CommissionTransactionAdmin(admin.ModelAdmin):
    list_display = ['partner', 'transaction_type', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'currency', 'created_at']
    search_fields = ['partner__partner_code', 'reference_payment_id', 'description']
    readonly_fields = ['created_at']
    
    actions = ['mark_completed', 'mark_failed']
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated}개 거래가 완료 처리되었습니다.')
    mark_completed.short_description = '선택된 거래 완료 처리'
    
    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated}개 거래가 실패 처리되었습니다.')
    mark_failed.short_description = '선택된 거래 실패 처리'


@admin.register(PartnerPerformance)
class PartnerPerformanceAdmin(admin.ModelAdmin):
    list_display = ['partner', 'year', 'month', 'total_clicks', 'conversions', 'conversion_rate', 'commission_earned']
    list_filter = ['year', 'month', 'partner__status']
    search_fields = ['partner__partner_code']
    readonly_fields = ['conversion_rate']


@admin.register(PartnerMaterial)
class PartnerMaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'material_type', 'width', 'height', 'download_count', 'is_active', 'created_at']
    list_filter = ['material_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['download_count']
