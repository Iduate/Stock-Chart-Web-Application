from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    AffiliatePartner, ReferralLink, ReferralClick,
    CommissionTransaction, PartnerPerformance, PartnerMaterial
)
from .serializers import (
    AffiliatePartnerSerializer, AffiliateApplicationSerializer,
    ReferralLinkSerializer, CommissionTransactionSerializer,
    PartnerPerformanceSerializer, PartnerMaterialSerializer
)


class AffiliatePartnerViewSet(viewsets.ModelViewSet):
    """홍보파트너 ViewSet"""
    serializer_class = AffiliatePartnerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return AffiliatePartner.objects.all()
        try:
            return AffiliatePartner.objects.filter(user=self.request.user)
        except:
            return AffiliatePartner.objects.none()
    
    @action(detail=False, methods=['post'], url_path='apply')
    def apply_for_partnership(self, request):
        """파트너 신청"""
        if hasattr(request.user, 'affiliate_partner'):
            return Response({
                'message': '이미 파트너 신청을 하셨습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AffiliateApplicationSerializer(data=request.data)
        if serializer.is_valid():
            partner = AffiliatePartner.objects.create(
                user=request.user,
                **serializer.validated_data
            )
            return Response({
                'message': '파트너 신청이 완료되었습니다. 승인을 기다려주세요.',
                'partner_code': partner.partner_code
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """파트너 대시보드 데이터"""
        try:
            partner = request.user.affiliate_partner
        except:
            return Response({
                'message': '파트너 정보를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 최근 30일 통계
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_clicks = ReferralClick.objects.filter(
            link__partner=partner,
            clicked_at__gte=thirty_days_ago
        ).count()
        
        recent_conversions = ReferralClick.objects.filter(
            link__partner=partner,
            converted=True,
            converted_at__gte=thirty_days_ago
        ).count()
        
        # 이번달 수수료
        now = timezone.now()
        this_month_commission = CommissionTransaction.objects.filter(
            partner=partner,
            transaction_type='earned',
            created_at__year=now.year,
            created_at__month=now.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # 미지급 수수료
        pending_commission = partner.total_commission_earned - partner.total_commission_paid
        
        return Response({
            'partner_info': AffiliatePartnerSerializer(partner).data,
            'recent_stats': {
                'clicks_30days': recent_clicks,
                'conversions_30days': recent_conversions,
                'conversion_rate': (recent_conversions / recent_clicks * 100) if recent_clicks > 0 else 0,
                'this_month_commission': this_month_commission,
                'pending_commission': pending_commission
            }
        })
    
    @action(detail=False, methods=['get'], url_path='performance')
    def performance_stats(self, request):
        """성과 통계"""
        try:
            partner = request.user.affiliate_partner
        except:
            return Response({
                'message': '파트너 정보를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 월별 성과 데이터 (최근 12개월)
        performances = PartnerPerformance.objects.filter(
            partner=partner
        ).order_by('-year', '-month')[:12]
        
        serializer = PartnerPerformanceSerializer(performances, many=True)
        return Response(serializer.data)


class ReferralLinkViewSet(viewsets.ModelViewSet):
    """추천 링크 ViewSet"""
    serializer_class = ReferralLinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            partner = self.request.user.affiliate_partner
            return ReferralLink.objects.filter(partner=partner)
        except:
            return ReferralLink.objects.none()
    
    def perform_create(self, serializer):
        partner = self.request.user.affiliate_partner
        serializer.save(partner=partner)


class CommissionTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """수수료 거래 내역 ViewSet"""
    serializer_class = CommissionTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            partner = self.request.user.affiliate_partner
            return CommissionTransaction.objects.filter(partner=partner)
        except:
            return CommissionTransaction.objects.none()
    
    @action(detail=False, methods=['post'], url_path='request-payout')
    def request_payout(self, request):
        """수수료 지급 요청"""
        try:
            partner = request.user.affiliate_partner
        except:
            return Response({
                'message': '파트너 정보를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if partner.status != 'active':
            return Response({
                'message': '활성 상태인 파트너만 지급 요청이 가능합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pending_amount = partner.total_commission_earned - partner.total_commission_paid
        
        if pending_amount < partner.minimum_payout:
            return Response({
                'message': f'최소 지급액 {partner.minimum_payout}원 이상부터 요청 가능합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 지급 요청 거래 생성
        transaction = CommissionTransaction.objects.create(
            partner=partner,
            transaction_type='paid',
            amount=pending_amount,
            description='수수료 지급 요청',
            status='pending'
        )
        
        return Response({
            'message': '지급 요청이 완료되었습니다.',
            'transaction_id': transaction.id,
            'amount': pending_amount
        })


class PartnerMaterialViewSet(viewsets.ReadOnlyModelViewSet):
    """홍보 자료 ViewSet"""
    serializer_class = PartnerMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PartnerMaterial.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'], url_path='download')
    def download_material(self, request, pk=None):
        """홍보 자료 다운로드"""
        material = self.get_object()
        material.download_count += 1
        material.save()
        
        return Response({
            'download_url': material.file_url,
            'download_count': material.download_count
        })


# 추천 링크 클릭 추적을 위한 별도 뷰
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View


@method_decorator(csrf_exempt, name='dispatch')
class ReferralTrackingView(View):
    """추천 링크 클릭 추적"""
    
    def get(self, request):
        ref_code = request.GET.get('ref')
        link_id = request.GET.get('link_id')
        target_url = request.GET.get('target', '/')
        
        if not ref_code:
            return redirect(target_url)
        
        try:
            # 파트너 찾기
            partner = AffiliatePartner.objects.get(partner_code=ref_code, status='active')
            
            # 링크 찾기
            if link_id:
                link = ReferralLink.objects.get(link_id=link_id, partner=partner, is_active=True)
            else:
                # 기본 링크 생성 또는 찾기
                link, created = ReferralLink.objects.get_or_create(
                    partner=partner,
                    name='기본 추천 링크',
                    target_url=target_url,
                    defaults={'utm_source': 'direct'}
                )
            
            # 클릭 추적
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referer = request.META.get('HTTP_REFERER', '')
            
            ReferralClick.objects.create(
                link=link,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
                session_id=request.session.session_key or ''
            )
            
            # 링크 클릭수 증가
            link.click_count += 1
            link.save()
            
            # 세션에 추천 정보 저장 (전환 추적용)
            request.session['referral_partner'] = partner.id
            request.session['referral_link'] = link.id
            
            # 타겟 URL로 리다이렉트
            return redirect(target_url)
            
        except (AffiliatePartner.DoesNotExist, ReferralLink.DoesNotExist):
            # 유효하지 않은 추천 코드인 경우 그냥 리다이렉트
            return redirect(target_url)
    
    def get_client_ip(self, request):
        """클라이언트 IP 주소 가져오기"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
