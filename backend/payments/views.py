from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from payments.models import Payment, PaymentPlan, PaymentMethod
from payments.serializers import PaymentSerializer, PaymentPlanSerializer, CouponSerializer
from payments.models import Coupon
from payments.paypal_utils import create_paypal_order, capture_paypal_order
from decimal import Decimal
import uuid
import json
import logging
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from django.conf import settings

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
            # Ensure PayPal method exists even if seed migration didn't run
            payment_method, _ = PaymentMethod.objects.get_or_create(
                provider='paypal',
                defaults={
                    'name': 'PayPal',
                    'is_active': True,
                    'icon_url': 'https://www.paypalobjects.com/webstatic/icon/pp258.png',
                    'description': 'Pay with PayPal',
                }
            )
            
            # Create payment record
            # Capture referral context into payment callback_data for later attribution
            referral_ctx = {}
            try:
                # Ensure session exists to store referral id
                if not request.session.session_key:
                    request.session.save()
                referral_ctx = {
                    'referral_session': request.session.session_key,
                    'referral_partner_id': request.session.get('referral_partner'),
                    'referral_link_id': request.session.get('referral_link'),
                }
            except Exception:
                referral_ctx = {}

            payment = Payment.objects.create(
                user=request.user if (hasattr(request, 'user') and request.user and request.user.is_authenticated) else None,
                plan=plan,
                payment_method=payment_method,
                amount=plan.price_usd if currency == 'USD' else plan.price_krw,
                currency=currency,
                status='pending',
                transaction_id=str(uuid.uuid4()),
                external_payment_id=order_result['id'],
                payment_url=order_result['approval_url'],
                callback_data=referral_ctx,
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

            # Attribute affiliate commission if applicable
            if payment.status == 'completed':
                try:
                    self._attribute_affiliate_commission(request, payment)
                except Exception as e:
                    logger.error(f"Affiliate attribution failed: {e}")
            
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

    def _attribute_affiliate_commission(self, request, payment: Payment):
        """Record conversion and commission for affiliates if referral context exists.
        Looks at request.session and/or payment.callback_data recorded at order creation.
        """
        # Lazy import to avoid circulars
        try:
            from affiliates.models import AffiliatePartner, ReferralLink, ReferralClick, CommissionTransaction
        except Exception as e:
            logger.error(f"Affiliates models import failed: {e}")
            return

        # Gather context
        partner_id = None
        link_id = None
        session_id = None

        # First, try session
        try:
            partner_id = request.session.get('referral_partner')
            link_id = request.session.get('referral_link')
            session_id = request.session.session_key
        except Exception:
            pass

        # Fallback to payment.callback_data where we stored order-time context
        if not (partner_id and link_id):
            try:
                ctx = payment.callback_data if isinstance(payment.callback_data, dict) else {}
                partner_id = partner_id or ctx.get('referral_partner_id')
                link_id = link_id or ctx.get('referral_link_id')
                session_id = session_id or ctx.get('referral_session')
            except Exception:
                ctx = {}

        if not partner_id:
            # Nothing to attribute
            return

        try:
            partner = AffiliatePartner.objects.get(id=partner_id)
        except AffiliatePartner.DoesNotExist:
            return

        link = None
        if link_id:
            try:
                link = ReferralLink.objects.get(id=link_id, partner=partner)
            except ReferralLink.DoesNotExist:
                link = None

        # Update click/conversion record if we can find by session
        try:
            if session_id:
                click = ReferralClick.objects.filter(link__partner=partner, session_id=session_id).order_by('-clicked_at').first()
                if click and not click.converted:
                    click.converted = True
                    click.converted_at = timezone.now()
                    click.save()
        except Exception:
            pass

        # Increment link and partner stats
        if link:
            link.conversion_count = (link.conversion_count or 0) + 1
            link.save(update_fields=['conversion_count'])

        # Compute commission amount using partner settings
        amount = Decimal(str(payment.amount))
        commission_amount = Decimal('0')
        try:
            commission_amount = partner.calculate_commission(amount)
        except Exception:
            # fallback percentage 10%
            commission_amount = (amount * Decimal('0.10')).quantize(Decimal('0.01'))

        # Create commission transaction and update partner aggregates
        try:
            CommissionTransaction.objects.create(
                partner=partner,
                transaction_type='earned',
                amount=commission_amount,
                currency=payment.currency,
                reference_payment_id=str(payment.id),
                description=f'결제 {payment.id}로 발생한 수수료'
            )

            # Update aggregates
            partner.total_conversions = (partner.total_conversions or 0) + 1
            partner.total_commission_earned = (partner.total_commission_earned or Decimal('0')) + commission_amount
            # total_referrals could represent signups; keep as-is unless unset
            partner.save(update_fields=['total_conversions', 'total_commission_earned'])
        except Exception as e:
            logger.error(f"Failed creating commission transaction: {e}")


class MoonPayStatusView(APIView):
    """Lightweight endpoint for the frontend to detect MoonPay configuration."""
    permission_classes = [AllowAny]

    def get(self, request):
        configured = bool(getattr(settings, 'MOONPAY_API_KEY', '') and getattr(settings, 'MOONPAY_SECRET_KEY', ''))
        sandbox = bool(getattr(settings, 'MOONPAY_SANDBOX', True))
        return Response({
            'configured': configured,
            'sandbox': sandbox
        })


class MoonPayOnRampInitView(viewsets.ViewSet):
    """Create a signed MoonPay buy URL and return it to the frontend"""
    # AllowAny so external testers (e.g., boss) can start MoonPay without logging in.
    # If authenticated, we still attach the user to downstream records where relevant.
    permission_classes = [AllowAny]

    def create(self, request):
        if not settings.MOONPAY_API_KEY or not settings.MOONPAY_SECRET_KEY:
            return Response({'error': 'MoonPay is not configured.'}, status=500)

        base_url = 'https://buy-sandbox.moonpay.com' if settings.MOONPAY_SANDBOX else 'https://buy.moonpay.com'

        # Inputs
        crypto_currency_code = request.data.get('crypto', 'BTC')  # e.g., BTC or ETH
        fiat_currency_code = request.data.get('fiat', 'USD')
        fiat_amount = request.data.get('amount')  # optional
        wallet_address = request.data.get('wallet_address')  # optional; if omitted, MoonPay collects it

        # Required params
        params = {
            'apiKey': settings.MOONPAY_API_KEY,
            'currencyCode': crypto_currency_code,
            'baseCurrencyCode': fiat_currency_code,
            'redirectURL': request.build_absolute_uri('/payment-success.html'),
            'returnUrl': request.build_absolute_uri('/payment-success.html'),
            'cancelUrl': request.build_absolute_uri('/payment-cancel.html'),
        }
        if wallet_address:
            params['walletAddress'] = wallet_address
        if fiat_amount:
            params['baseCurrencyAmount'] = str(fiat_amount)

        # Sign the URL
        query = urlencode(sorted(params.items()))
        signature = hmac.new(
            settings.MOONPAY_SECRET_KEY.encode('utf-8'),
            query.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        signed_url = f"{base_url}?{query}&signature={urlencode({'signature': signature_b64})[10:]}"

        return Response({
            'url': signed_url
        })


class MoonPayOnRampCallbackView(viewsets.ViewSet):
    """Placeholder for any server-side callback handling if needed"""
    permission_classes = [AllowAny]

    def list(self, request):
        # MoonPay generally redirects back to the provided URLs; we can optionally record a marker
        try:
            status_param = request.GET.get('status', '')
            return Response({'ok': True, 'status': status_param})
        except Exception as e:
            logger.error(f"MoonPay callback error: {e}")
            return Response({'ok': False}, status=400)


class CouponViewSet(viewsets.ModelViewSet):
    """쿠폰 관리 ViewSet"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='validate')
    def validate_coupon(self, request):
        code = request.data.get('code', '').strip()
        if not code:
            return Response({'valid': False, 'message': '쿠폰 코드를 입력하세요.'}, status=400)
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({'valid': False, 'message': '유효하지 않은 쿠폰입니다.'}, status=404)

        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_until):
            return Response({'valid': False, 'message': '쿠폰 유효기간이 아닙니다.'}, status=400)

        if coupon.max_usage_count and coupon.used_count >= coupon.max_usage_count:
            return Response({'valid': False, 'message': '쿠폰 사용 가능 횟수를 초과했습니다.'}, status=400)

        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data
        })

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

                    # Affiliate attribution (webhook path)
                    try:
                        from affiliates.models import AffiliatePartner, ReferralLink, ReferralClick, CommissionTransaction
                        from decimal import Decimal
                        ctx = payment.callback_data if isinstance(payment.callback_data, dict) else {}
                        partner_id = ctx.get('referral_partner_id')
                        link_id = ctx.get('referral_link_id')
                        session_id = ctx.get('referral_session')
                        if partner_id:
                            try:
                                partner = AffiliatePartner.objects.get(id=partner_id)
                                link = None
                                if link_id:
                                    try:
                                        link = ReferralLink.objects.get(id=link_id, partner=partner)
                                    except ReferralLink.DoesNotExist:
                                        link = None
                                # Update click conversion if we have session
                                if session_id:
                                    click = ReferralClick.objects.filter(link__partner=partner, session_id=session_id).order_by('-clicked_at').first()
                                    if click and not click.converted:
                                        click.converted = True
                                        click.converted_at = timezone.now()
                                        click.save()
                                if link:
                                    link.conversion_count = (link.conversion_count or 0) + 1
                                    link.save(update_fields=['conversion_count'])
                                # Commission
                                amount = Decimal(str(payment.amount))
                                commission_amount = partner.calculate_commission(amount)
                                CommissionTransaction.objects.create(
                                    partner=partner,
                                    transaction_type='earned',
                                    amount=commission_amount,
                                    currency=payment.currency,
                                    reference_payment_id=str(payment.id),
                                    description=f'결제 {payment.id} (웹훅)로 발생한 수수료'
                                )
                                partner.total_conversions = (partner.total_conversions or 0) + 1
                                partner.total_commission_earned = (partner.total_commission_earned or Decimal('0')) + commission_amount
                                partner.save(update_fields=['total_conversions', 'total_commission_earned'])
                            except AffiliatePartner.DoesNotExist:
                                pass
                    except Exception as e:
                        logger.error(f"Webhook affiliate attribution error: {e}")
                except Payment.DoesNotExist:
                    logger.error(f"Payment not found for order: {order_id}")
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})
