from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Payment, PaymentPlan, PaymentMethod
from .serializers import PaymentSerializer, PaymentPlanSerializer
from .paypal_utils import create_paypal_order, capture_paypal_order
import uuid
import json
import logging

logger = logging.getLogger(__name__)

class PaymentPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """요금제 관리 ViewSet"""
    queryset = PaymentPlan.objects.filter(is_active=True)
    serializer_class = PaymentPlanSerializer
    permission_classes = [AllowAny]  # Anyone can view payment plans

class PaymentViewSet(viewsets.ModelViewSet):
    """결제 관리 ViewSet"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    def get_permissions(self):
        if self.action in ['create_paypal_order', 'capture_paypal_payment']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['POST'], url_path='create-paypal-order')
    def create_paypal_order(self, request):
        """PayPal 주문 생성"""
        plan_id = request.data.get('plan_id')
        currency = request.data.get('currency', 'USD')
        
        if not plan_id:
            return Response({
                'message': '요금제 ID가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
        except PaymentPlan.DoesNotExist:
            return Response({
                'message': '유효하지 않은 요금제입니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create PayPal order
        order_result = create_paypal_order(plan, currency)
        if not order_result:
            return Response({
                'message': 'PayPal 주문 생성에 실패했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Store the order in our system
        try:
            payment_method = PaymentMethod.objects.get(provider='paypal')
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user if request.user.is_authenticated else None,
                plan=plan,
                payment_method=payment_method,
                amount=plan.price_usd if currency == 'USD' else plan.price_krw,
                currency=currency,
                status='pending',
                transaction_id=str(uuid.uuid4()),
                external_payment_id=order_result['id'],
                payment_url=order_result['approval_url']
            )
            
            return Response({
                'payment_id': payment.id,
                'order_id': order_result['id'],
                'approval_url': order_result['approval_url'],
                'status': order_result['status'],
                'message': 'PayPal 주문이 생성되었습니다.'
            })
        except Exception as e:
            logger.error(f"Error storing PayPal order: {e}")
            return Response({
                'message': '결제 정보 저장 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['POST'], url_path='capture-paypal-payment')
    def capture_paypal_payment(self, request):
        """PayPal 결제 완료"""
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({
                'message': '주문 ID가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Capture the payment
        capture_result = capture_paypal_order(order_id)
        if not capture_result:
            return Response({
                'message': 'PayPal 결제 완료에 실패했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Update the payment record
        try:
            payment = Payment.objects.get(external_payment_id=order_id)
            payment.status = 'completed' if capture_result['status'] == 'COMPLETED' else 'failed'
            payment.completed_at = timezone.now()
            payment.callback_data = capture_result
            payment.save()
            
            # If payment is complete and user is authenticated, update user subscription
            if payment.status == 'completed' and payment.user:
                # Update user type and subscription status
                user = payment.user
                user.user_type = 'paid'
                user.subscription_status = 'active'
                user.subscription_expiry = timezone.now() + timezone.timedelta(days=payment.plan.duration_days)
                user.free_access_count = 0  # Reset free access count
                user.save()
                
                # Create or update subscription record
                from users.models import Subscription
                Subscription.objects.create(
                    user=user,
                    plan=payment.plan.plan_type,
                    status='active',
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=payment.plan.duration_days),
                    payment_id=str(payment.id),
                    amount=payment.amount,
                    currency=payment.currency
                )
            
            return Response({
                'payment_id': payment.id,
                'status': payment.status,
                'message': '결제가 완료되었습니다.'
            })
        except Payment.DoesNotExist:
            return Response({
                'message': '결제 정보를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating payment: {e}")
            return Response({
                'message': '결제 정보 업데이트 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def paypal_webhook(request):
    """PayPal webhook handler for payment notifications"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    try:
        # Parse webhook data
        data = json.loads(request.body)
        event_type = data.get('event_type')
        
        # Process different event types
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Handle successful payment
            resource = data.get('resource', {})
            order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
            
            if order_id:
                try:
                    payment = Payment.objects.get(external_payment_id=order_id)
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                    payment.callback_data = data
                    payment.save()
                    
                    # Create subscription if user exists
                    if payment.user:
                        from users.models import Subscription
                        
                        Subscription.objects.create(
                            user=payment.user,
                            payment=payment,
                            plan_name=payment.plan.name,
                            start_date=timezone.now(),
                            end_date=timezone.now() + timezone.timedelta(days=payment.plan.duration_days),
                            is_active=True
                        )
                except Payment.DoesNotExist:
                    logger.error(f"Payment not found for order: {order_id}")
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})
