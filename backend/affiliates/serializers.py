from rest_framework import serializers
from .models import (
    AffiliatePartner, ReferralLink, ReferralClick,
    CommissionTransaction, PartnerPerformance, PartnerMaterial
)


class AffiliatePartnerSerializer(serializers.ModelSerializer):
    referral_link = serializers.SerializerMethodField()
    commission_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = AffiliatePartner
        fields = [
            'id', 'partner_code', 'company_name', 'status',
            'commission_type', 'commission_rate', 'fixed_commission',
            'total_referrals', 'total_conversions', 'total_commission_earned',
            'total_commission_paid', 'minimum_payout', 'applied_at',
            'referral_link', 'commission_balance'
        ]
        read_only_fields = [
            'partner_code', 'total_referrals', 'total_conversions',
            'total_commission_earned', 'total_commission_paid'
        ]
    
    def get_referral_link(self, obj):
        return obj.get_referral_link()
    
    def get_commission_balance(self, obj):
        return obj.total_commission_earned - obj.total_commission_paid


class AffiliateApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliatePartner
        fields = [
            'company_name', 'business_registration', 'phone_number',
            'website', 'social_media', 'bank_info'
        ]


class ReferralLinkSerializer(serializers.ModelSerializer):
    full_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReferralLink
        fields = [
            'id', 'name', 'target_url', 'utm_source', 'utm_medium',
            'utm_campaign', 'click_count', 'conversion_count',
            'is_active', 'created_at', 'full_url'
        ]
        read_only_fields = ['click_count', 'conversion_count']
    
    def get_full_url(self, obj):
        return obj.get_full_url()


class CommissionTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'currency',
            'description', 'status', 'created_at', 'processed_at'
        ]


class PartnerPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerPerformance
        fields = [
            'year', 'month', 'total_clicks', 'unique_clicks',
            'conversions', 'revenue_generated', 'commission_earned',
            'conversion_rate'
        ]


class PartnerMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerMaterial
        fields = [
            'id', 'name', 'material_type', 'description',
            'file_url', 'thumbnail_url', 'content',
            'width', 'height', 'download_count', 'is_active'
        ]
