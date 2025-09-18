"""
국제 결제 API 뷰
"""

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from decimal import Decimal
import logging

from .models import (
    InternationalPayment, ExchangeRate, PaymentWebhook,
    PaymentMethod, PaymentPlan
)
from .serializers import (
    InternationalPaymentSerializer, InternationalPaymentCreateSerializer,
    ExchangeRateSerializer, PaymentWebhookSerializer
)
from .international_services import international_payment_manager

logger = logging.getLogger(__name__)


class InternationalPaymentViewSet(viewsets.ModelViewSet):
    """국제 결제 ViewSet"""
    
    serializer_class = InternationalPaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """사용자별 결제 내역 조회"""
        if self.request.user.is_staff:
            return InternationalPayment.objects.all().order_by('-created_at')
        return InternationalPayment.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """국제 결제 생성"""
        serializer = InternationalPaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # 결제 생성
                payment_data = {
                    'merchant_uid': f"INT_{timezone.now().strftime('%Y%m%d%H%M%S')}_{request.user.id}",
                    'amount': data['amount'],
                    'description': data['product_name'],
                    'buyer_name': data['buyer_name'],
                    'buyer_email': data['buyer_email'],
                    'success_url': data.get('success_url', ''),
                    'cancel_url': data.get('cancel_url', ''),
                    'webhook_url': f"{request.build_absolute_uri('/')[:-1]}/api/payments/webhook/{data['provider']}/"
                }
                
                # 게이트웨이 결제 생성
                gateway_result = international_payment_manager.create_payment(
                    data['provider'], 
                    payment_data
                )
                
                if not gateway_result['success']:
                    return Response(
                        {'error': gateway_result.get('error', '결제 생성 실패')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 환율 정보 가져오기
                exchange_rate = Decimal('1')
                amount_converted = Decimal(str(data['amount']))
                currency_converted = 'USD'
                
                if data.get('currency') != 'KRW':
                    try:
                        rate_obj = ExchangeRate.objects.get(
                            from_currency='KRW',
                            to_currency=data.get('currency', 'USD'),
                            is_active=True
                        )
                        exchange_rate = rate_obj.rate
                        amount_converted = Decimal(str(data['amount'])) * exchange_rate
                        currency_converted = data.get('currency', 'USD')
                    except ExchangeRate.DoesNotExist:
                        # 기본 환율 사용
                        gateway = international_payment_manager.get_gateway(data['provider'])
                        exchange_rate = gateway.get_exchange_rate('KRW', 'USD')
                        amount_converted = Decimal(str(data['amount'])) * exchange_rate
                
                # DB에 결제 정보 저장
                international_payment = InternationalPayment.objects.create(
                    user=request.user,
                    provider=data['provider'],
                    payment_id=gateway_result.get('payment_id', ''),
                    merchant_uid=payment_data['merchant_uid'],
                    amount_original=data['amount'],
                    currency_original='KRW',
                    amount_converted=amount_converted,
                    currency_converted=currency_converted,
                    exchange_rate=exchange_rate,
                    buyer_name=data['buyer_name'],
                    buyer_email=data['buyer_email'],
                    buyer_country=data.get('country', ''),
                    product_name=data['product_name'],
                    product_description=data.get('product_description', ''),
                    payment_url=gateway_result.get('payment_url', '') or gateway_result.get('approval_url', ''),
                    client_secret=gateway_result.get('client_secret', ''),
                    gateway_response=gateway_result,
                    metadata=data.get('metadata', {})
                )
                
                serializer = InternationalPaymentSerializer(international_payment)
                
                response_data = serializer.data
                response_data.update({
                    'payment_url': international_payment.payment_url,
                    'client_secret': international_payment.client_secret
                })
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"International payment creation error: {str(e)}")
            return Response(
                {'error': '결제 생성 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """결제 검증"""
        payment = self.get_object()
        
        # 권한 확인
        if not request.user.is_staff and payment.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # 게이트웨이에서 결제 상태 확인
            verify_result = international_payment_manager.verify_payment(
                payment.provider,
                payment.payment_id
            )
            
            if verify_result['success']:
                # 결제 상태 업데이트
                if verify_result.get('paid'):
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                else:
                    payment.status = 'processing'
                
                payment.gateway_response.update(verify_result)
                payment.save()
                
                return Response({
                    'success': True,
                    'status': payment.status,
                    'verified': verify_result.get('paid', False)
                })
            else:
                return Response(
                    {'error': verify_result.get('error', '결제 검증 실패')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return Response(
                {'error': '결제 검증 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """결제 취소"""
        payment = self.get_object()
        
        # 권한 확인
        if not request.user.is_staff and payment.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 취소 가능 상태 확인
        if payment.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Payment cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reason = request.data.get('reason', 'Cancelled by user')
            
            cancel_result = international_payment_manager.cancel_payment(
                payment.provider,
                payment.payment_id,
                reason
            )
            
            if cancel_result['success']:
                payment.status = 'cancelled'
                payment.gateway_response.update(cancel_result)
                payment.save()
                
                return Response({
                    'success': True,
                    'message': 'Payment cancelled successfully'
                })
            else:
                return Response(
                    {'error': cancel_result.get('error', '결제 취소 실패')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Payment cancellation error: {str(e)}")
            return Response(
                {'error': '결제 취소 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """결제 환불"""
        payment = self.get_object()
        
        # 권한 확인 (관리자만)
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 환불 가능 상태 확인
        if payment.status != 'completed':
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = request.data.get('amount')
            reason = request.data.get('reason', 'Refund requested')
            
            if amount:
                amount = Decimal(str(amount))
                if amount > payment.amount_converted:
                    return Response(
                        {'error': 'Refund amount exceeds payment amount'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            refund_result = international_payment_manager.refund_payment(
                payment.provider,
                payment.payment_id,
                amount,
                reason
            )
            
            if refund_result['success']:
                payment.status = 'refunded'
                payment.gateway_response.update(refund_result)
                payment.save()
                
                return Response({
                    'success': True,
                    'message': 'Payment refunded successfully',
                    'refund_id': refund_result.get('refund_id', '')
                })
            else:
                return Response(
                    {'error': refund_result.get('error', '환불 처리 실패')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Payment refund error: {str(e)}")
            return Response(
                {'error': '환불 처리 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExchangeRateViewSet(viewsets.ReadOnlyModelViewSet):
    """환율 API"""
    
    queryset = ExchangeRate.objects.filter(is_active=True).order_by('from_currency', 'to_currency')
    serializer_class = ExchangeRateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def current_rates(self, request):
        """현재 환율 조회"""
        base_currency = request.query_params.get('base', 'KRW')
        target_currencies = request.query_params.get('targets', 'USD,EUR,JPY').split(',')
        
        rates = {}
        for currency in target_currencies:
            try:
                rate = ExchangeRate.objects.get(
                    from_currency=base_currency,
                    to_currency=currency,
                    is_active=True
                )
                rates[currency] = {
                    'rate': rate.rate,
                    'updated_at': rate.updated_at.isoformat()
                }
            except ExchangeRate.DoesNotExist:
                rates[currency] = None
        
        return Response({
            'base_currency': base_currency,
            'rates': rates,
            'timestamp': timezone.now().isoformat()
        })


class PaymentStatsView(APIView):
    """결제 통계 API"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """결제 통계 조회"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 기본 통계
        total_payments = InternationalPayment.objects.count()
        completed_payments = InternationalPayment.objects.filter(status='completed').count()
        pending_payments = InternationalPayment.objects.filter(status='pending').count()
        failed_payments = InternationalPayment.objects.filter(status='failed').count()
        
        # 제공업체별 통계
        provider_stats = {}
        for provider, _ in InternationalPayment.PROVIDER_CHOICES:
            provider_payments = InternationalPayment.objects.filter(provider=provider)
            provider_stats[provider] = {
                'total': provider_payments.count(),
                'completed': provider_payments.filter(status='completed').count(),
                'total_amount': sum(p.amount_converted for p in provider_payments.filter(status='completed'))
            }
        
        # 통화별 통계
        currency_stats = {}
        for currency, _ in InternationalPayment.CURRENCY_CHOICES:
            currency_payments = InternationalPayment.objects.filter(
                currency_converted=currency,
                status='completed'
            )
            if currency_payments.exists():
                currency_stats[currency] = {
                    'count': currency_payments.count(),
                    'total_amount': sum(p.amount_converted for p in currency_payments)
                }
        
        return Response({
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'pending_payments': pending_payments,
            'failed_payments': failed_payments,
            'success_rate': (completed_payments / total_payments * 100) if total_payments > 0 else 0,
            'provider_stats': provider_stats,
            'currency_stats': currency_stats
        })


class PaymentWebhookView(APIView):
    """결제 웹훅 처리"""
    
    authentication_classes = []  # 웹훅은 인증 없이 처리
    permission_classes = []
    
    def post(self, request, provider):
        """웹훅 데이터 처리"""
        try:
            # 웹훅 로그 저장
            webhook = PaymentWebhook.objects.create(
                provider=provider,
                event_type=request.data.get('type', request.data.get('event_type', 'unknown')),
                payment_id=request.data.get('payment_id', request.data.get('id', '')),
                raw_data=request.data
            )
            
            # 제공업체별 웹훅 처리
            if provider == 'stripe':
                self.process_stripe_webhook(webhook)
            elif provider == 'paypal':
                self.process_paypal_webhook(webhook)
            elif provider == 'crypto':
                self.process_crypto_webhook(webhook)
            
            return Response({'success': True})
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return Response({'error': 'Webhook processing failed'}, status=500)
    
    def process_stripe_webhook(self, webhook):
        """Stripe 웹훅 처리"""
        try:
            event_type = webhook.event_type
            payment_id = webhook.raw_data.get('data', {}).get('object', {}).get('id', '')
            
            if payment_id:
                payment = InternationalPayment.objects.filter(payment_id=payment_id).first()
                if payment:
                    if event_type == 'payment_intent.succeeded':
                        payment.status = 'completed'
                        payment.completed_at = timezone.now()
                    elif event_type == 'payment_intent.payment_failed':
                        payment.status = 'failed'
                        payment.failed_at = timezone.now()
                    
                    payment.save()
                    webhook.processed = True
                    webhook.processed_at = timezone.now()
            
            webhook.save()
            
        except Exception as e:
            webhook.error_message = str(e)
            webhook.save()
    
    def process_paypal_webhook(self, webhook):
        """PayPal 웹훅 처리"""
        # PayPal 웹훅 처리 로직
        pass
    
    def process_crypto_webhook(self, webhook):
        """암호화폐 웹훅 처리"""
        # 암호화폐 웹훅 처리 로직
        pass
