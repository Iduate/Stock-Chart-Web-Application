from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import (
    PaymentProvider, PaymentMethod, PaymentTransaction, 
    PaymentRefund, PaymentWebhook, PaymentConfig
)
from .serializers import (
    PaymentProviderSerializer, PaymentMethodSerializer,
    PaymentTransactionSerializer, PaymentCreateSerializer,
    PaymentVerifySerializer, PaymentCancelSerializer,
    PaymentRefundSerializer, PaymentRefundCreateSerializer,
    PaymentConfigSerializer, PaymentStatsSerializer
)
from .services import payment_manager
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PaymentProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """결제 제공업체 API"""
    
    queryset = PaymentProvider.objects.filter(is_active=True)
    serializer_class = PaymentProviderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def korean_providers(self, request):
        """한국 결제 제공업체 목록"""
        providers = self.queryset.filter(is_korean=True)
        serializer = self.get_serializer(providers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def international_providers(self, request):
        """국제 결제 제공업체 목록"""
        providers = self.queryset.filter(is_korean=False)
        serializer = self.get_serializer(providers, many=True)
        return Response(serializer.data)


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """결제 수단 API"""
    
    queryset = PaymentMethod.objects.filter(is_active=True).order_by('display_order')
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """결제 제공업체별 지원 결제 수단 필터링"""
        queryset = self.queryset
        provider = self.request.query_params.get('provider', None)
        
        if provider:
            try:
                provider_obj = PaymentProvider.objects.get(name=provider, is_active=True)
                queryset = queryset.filter(providers=provider_obj)
            except PaymentProvider.DoesNotExist:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def korean_methods(self, request):
        """한국 결제 수단 목록"""
        methods = self.get_queryset().filter(is_korean=True)
        serializer = self.get_serializer(methods, many=True)
        return Response(serializer.data)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """결제 거래 API"""
    
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """사용자별 결제 거래 조회"""
        if self.request.user.is_staff:
            return PaymentTransaction.objects.all().order_by('-created_at')
        return PaymentTransaction.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """결제 취소"""
        transaction_obj = self.get_object()
        
        # 권한 확인
        if not request.user.is_staff and transaction_obj.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 취소 가능 상태 확인
        if transaction_obj.status != 'paid':
            return Response(
                {'error': 'Only paid transactions can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PaymentCancelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 결제 취소 처리
        cancel_result = payment_manager.cancel_payment(
            provider_name=transaction_obj.provider.name,
            payment_key=transaction_obj.imp_uid,
            amount=serializer.validated_data.get('amount'),
            reason=serializer.validated_data['reason']
        )
        
        if cancel_result['success']:
            # 거래 상태 업데이트
            transaction_obj.status = 'cancelled'
            transaction_obj.cancelled_at = timezone.now()
            transaction_obj.save()
            
            logger.info(f"Payment cancelled: {transaction_obj.merchant_uid}")
            
            return Response({
                'message': 'Payment cancelled successfully',
                'cancelled_amount': cancel_result.get('cancelled_amount', transaction_obj.final_amount)
            })
        else:
            return Response(
                {'error': cancel_result.get('error', 'Payment cancellation failed')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCreateView(APIView):
    """결제 생성 API"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """결제 요청 생성"""
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # 결제 제공업체 및 수단 확인
                try:
                    provider = PaymentProvider.objects.get(
                        name=data['provider'], 
                        is_active=True
                    )
                    payment_method = PaymentMethod.objects.get(
                        code=data['payment_method'], 
                        is_active=True
                    )
                except (PaymentProvider.DoesNotExist, PaymentMethod.DoesNotExist):
                    return Response(
                        {'error': 'Invalid payment provider or method'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 결제 거래 생성
                payment_transaction = PaymentTransaction.objects.create(
                    user=request.user,
                    provider=provider,
                    payment_method=payment_method,
                    amount=data['amount'],
                    name=data['name'],
                    description=data.get('description', ''),
                    buyer_name=data['buyer_name'],
                    buyer_email=data['buyer_email'],
                    buyer_tel=data.get('buyer_tel', ''),
                    buyer_addr=data.get('buyer_addr', ''),
                    buyer_postcode=data.get('buyer_postcode', '')
                )
                
                # 결제 서비스 호출
                payment_data = {
                    'merchant_uid': payment_transaction.merchant_uid,
                    'amount': data['amount'],
                    'name': data['name'],
                    'description': data.get('description', ''),
                    'buyer_name': data['buyer_name'],
                    'buyer_email': data['buyer_email'],
                    'buyer_tel': data.get('buyer_tel', ''),
                    'success_url': data.get('success_url', ''),
                    'cancel_url': data.get('cancel_url', ''),
                    'fail_url': data.get('fail_url', ''),
                    'user_id': str(request.user.id),
                    'card_quota': data.get('card_quota', 0)
                }
                
                result = payment_manager.create_payment(data['provider'], payment_data)
                
                if result['success']:
                    # 결제 준비 완료
                    payment_transaction.status = 'ready'
                    payment_transaction.save()
                    
                    logger.info(f"Payment created: {payment_transaction.merchant_uid}")
                    
                    return Response({
                        'success': True,
                        'transaction_id': payment_transaction.transaction_id,
                        'merchant_uid': payment_transaction.merchant_uid,
                        **result
                    })
                else:
                    return Response(
                        {'error': result.get('error', 'Payment creation failed')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
        except Exception as e:
            logger.error(f"Payment creation error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentVerifyView(APIView):
    """결제 검증 API"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """결제 검증"""
        serializer = PaymentVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # 거래 조회
            payment_transaction = get_object_or_404(
                PaymentTransaction,
                merchant_uid=data['merchant_uid'],
                user=request.user
            )
            
            # 결제 검증
            payment_key = data.get('imp_uid') or data.get('payment_key')
            if not payment_key:
                return Response(
                    {'error': 'Payment key (imp_uid or payment_key) is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            verify_result = payment_manager.verify_payment(
                provider_name=data['provider'],
                payment_key=payment_key
            )
            
            if verify_result['success']:
                # 결제 금액 검증
                if verify_result.get('amount') != data['amount']:
                    return Response(
                        {'error': 'Payment amount mismatch'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 거래 정보 업데이트
                with transaction.atomic():
                    payment_transaction.imp_uid = payment_key
                    payment_transaction.pg_tid = verify_result.get('pg_tid', '')
                    payment_transaction.pg_provider = verify_result.get('pg_provider', '')
                    payment_transaction.status = 'paid'
                    payment_transaction.paid_at = timezone.now()
                    
                    # 카드 정보 저장
                    if verify_result.get('card_name'):
                        payment_transaction.card_name = verify_result['card_name']
                        payment_transaction.card_number = verify_result.get('card_number', '')
                        payment_transaction.card_quota = verify_result.get('card_quota', 0)
                    
                    # 가상계좌 정보 저장
                    if verify_result.get('vbank_num'):
                        payment_transaction.vbank_num = verify_result['vbank_num']
                        payment_transaction.vbank_name = verify_result.get('vbank_name', '')
                        payment_transaction.vbank_holder = verify_result.get('vbank_holder', '')
                    
                    payment_transaction.save()
                
                logger.info(f"Payment verified: {payment_transaction.merchant_uid}")
                
                return Response({
                    'success': True,
                    'message': 'Payment verified successfully',
                    'transaction_id': payment_transaction.transaction_id,
                    'status': payment_transaction.status
                })
            else:
                return Response(
                    {'error': verify_result.get('error', 'Payment verification failed')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except PaymentTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentRefundViewSet(viewsets.ModelViewSet):
    """환불 관리 API"""
    
    serializer_class = PaymentRefundSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """사용자별 환불 내역 조회"""
        if self.request.user.is_staff:
            return PaymentRefund.objects.all().order_by('-requested_at')
        return PaymentRefund.objects.filter(
            requested_by=self.request.user
        ).order_by('-requested_at')
    
    def create(self, request, *args, **kwargs):
        """환불 요청 생성"""
        serializer = PaymentRefundCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # 원본 거래 조회
            payment_transaction = get_object_or_404(
                PaymentTransaction,
                transaction_id=data['transaction_id'],
                user=request.user,
                status='paid'
            )
            
            # 환불 가능 금액 확인
            already_refunded = PaymentRefund.objects.filter(
                transaction=payment_transaction,
                status__in=['completed', 'processing']
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            
            available_amount = payment_transaction.final_amount - already_refunded
            
            if data['amount'] > available_amount:
                return Response(
                    {'error': f'Refund amount exceeds available amount: {available_amount}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 환불 요청 생성
            refund = PaymentRefund.objects.create(
                transaction=payment_transaction,
                amount=data['amount'],
                reason=data['reason'],
                reason_detail=data.get('reason_detail', ''),
                requested_by=request.user
            )
            
            logger.info(f"Refund requested: {refund.refund_id}")
            
            return Response({
                'success': True,
                'refund_id': refund.refund_id,
                'message': 'Refund request submitted successfully'
            })
            
        except Exception as e:
            logger.error(f"Refund request error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        
        period = request.query_params.get('period', 'daily')
        
        # 기간 설정
        now = timezone.now()
        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start_date = now - timedelta(days=7)
        elif period == 'monthly':
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=1)
        
        # 기본 통계
        transactions = PaymentTransaction.objects.filter(created_at__gte=start_date)
        
        total_transactions = transactions.count()
        successful_transactions = transactions.filter(status='paid').count()
        failed_transactions = transactions.filter(status='failed').count()
        cancelled_transactions = transactions.filter(status='cancelled').count()
        
        total_amount = sum(t.final_amount for t in transactions.filter(status='paid'))
        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # 결제 수단별 통계
        payment_method_stats = {}
        for method in PaymentMethod.objects.filter(is_active=True):
            method_transactions = transactions.filter(payment_method=method, status='paid')
            payment_method_stats[method.name] = {
                'count': method_transactions.count(),
                'amount': sum(t.final_amount for t in method_transactions)
            }
        
        # 제공업체별 통계
        provider_stats = {}
        for provider in PaymentProvider.objects.filter(is_active=True):
            provider_transactions = transactions.filter(provider=provider, status='paid')
            provider_stats[provider.display_name] = {
                'count': provider_transactions.count(),
                'amount': sum(t.final_amount for t in provider_transactions)
            }
        
        stats_data = {
            'period': period,
            'total_transactions': total_transactions,
            'total_amount': total_amount,
            'successful_transactions': successful_transactions,
            'failed_transactions': failed_transactions,
            'cancelled_transactions': cancelled_transactions,
            'success_rate': round(success_rate, 2),
            'payment_method_stats': payment_method_stats,
            'provider_stats': provider_stats
        }
        
        return Response(stats_data)


@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook(request, provider_name):
    """결제 웹훅 처리"""
    try:
        # 웹훅 데이터 파싱
        webhook_data = json.loads(request.body.decode('utf-8'))
        headers = dict(request.META)
        
        # 웹훅 로그 저장
        try:
            provider = PaymentProvider.objects.get(name=provider_name)
            webhook = PaymentWebhook.objects.create(
                provider=provider,
                event_type=webhook_data.get('event_type', 'unknown'),
                imp_uid=webhook_data.get('imp_uid', ''),
                merchant_uid=webhook_data.get('merchant_uid', ''),
                raw_data=webhook_data,
                headers=headers
            )
        except PaymentProvider.DoesNotExist:
            logger.error(f"Unknown payment provider in webhook: {provider_name}")
            return JsonResponse({'error': 'Unknown provider'}, status=400)
        
        # 웹훅 처리 로직 (각 제공업체별로 다름)
        if provider_name == 'iamport':
            process_iamport_webhook(webhook)
        elif provider_name == 'toss':
            process_toss_webhook(webhook)
        elif provider_name == 'kakaopay':
            process_kakaopay_webhook(webhook)
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def process_iamport_webhook(webhook):
    """아임포트 웹훅 처리"""
    try:
        data = webhook.raw_data
        merchant_uid = data.get('merchant_uid')
        
        if merchant_uid:
            try:
                payment_transaction = PaymentTransaction.objects.get(
                    merchant_uid=merchant_uid
                )
                
                # 결제 상태에 따른 처리
                event_type = data.get('status')
                if event_type == 'paid':
                    payment_transaction.status = 'paid'
                    payment_transaction.paid_at = timezone.now()
                elif event_type == 'cancelled':
                    payment_transaction.status = 'cancelled'
                    payment_transaction.cancelled_at = timezone.now()
                elif event_type == 'failed':
                    payment_transaction.status = 'failed'
                    payment_transaction.failed_at = timezone.now()
                
                payment_transaction.save()
                webhook.is_processed = True
                webhook.processed_at = timezone.now()
                webhook.transaction = payment_transaction
                
            except PaymentTransaction.DoesNotExist:
                webhook.error_message = f"Transaction not found: {merchant_uid}"
        
        webhook.save()
        
    except Exception as e:
        webhook.error_message = str(e)
        webhook.save()
        logger.error(f"Iamport webhook processing error: {str(e)}")


def process_toss_webhook(webhook):
    """토스페이먼츠 웹훅 처리"""
    # 토스페이먼츠 웹훅 처리 로직
    pass


def process_kakaopay_webhook(webhook):
    """카카오페이 웹훅 처리"""
    # 카카오페이 웹훅 처리 로직
    pass
