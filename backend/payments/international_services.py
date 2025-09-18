"""
국제 결제 게이트웨이 서비스
PayPal, Stripe, Crypto 결제 지원
"""

import json
import requests
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PaymentGatewayError(Exception):
    """결제 게이트웨이 오류"""
    pass


class BasePaymentGateway:
    """기본 결제 게이트웨이 클래스"""
    
    def __init__(self):
        self.name = 'base'
        self.currency_map = {
            'KRW': 'USD',  # 기본적으로 USD로 변환
            'USD': 'USD',
            'EUR': 'EUR',
            'JPY': 'JPY'
        }
    
    def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """결제 생성"""
        raise NotImplementedError
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """결제 검증"""
        raise NotImplementedError
    
    def cancel_payment(self, payment_id: str, reason: str = '') -> Dict[str, Any]:
        """결제 취소"""
        raise NotImplementedError
    
    def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None, reason: str = '') -> Dict[str, Any]:
        """결제 환불"""
        raise NotImplementedError
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """환율 조회"""
        try:
            # 실제 환율 API 호출 (예: exchangerate-api.com)
            response = requests.get(
                f'https://api.exchangerate-api.com/v4/latest/{from_currency}',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                rate = data.get('rates', {}).get(to_currency, 1)
                return Decimal(str(rate))
            
        except Exception as e:
            logger.error(f"Exchange rate API error: {str(e)}")
        
        # 기본 환율 (실제 운영 시 더 정확한 값으로 설정)
        default_rates = {
            ('KRW', 'USD'): Decimal('0.00075'),
            ('USD', 'KRW'): Decimal('1333.33'),
            ('KRW', 'EUR'): Decimal('0.00068'),
            ('EUR', 'KRW'): Decimal('1470.59')
        }
        
        return default_rates.get((from_currency, to_currency), Decimal('1'))
    
    def convert_amount(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """금액 통화 변환"""
        if from_currency == to_currency:
            return amount
        
        rate = self.get_exchange_rate(from_currency, to_currency)
        converted = amount * rate
        
        # 소수점 2자리로 반올림
        return converted.quantize(Decimal('0.01'))


class StripeGateway(BasePaymentGateway):
    """Stripe 결제 게이트웨이"""
    
    def __init__(self):
        super().__init__()
        self.name = 'stripe'
        self.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        self.webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        self.base_url = 'https://api.stripe.com/v1'
        
        # Stripe 지원 통화
        self.supported_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD']
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Stripe API 요청"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, params=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Stripe API error: {str(e)}")
            raise PaymentGatewayError(f"Stripe API 오류: {str(e)}")
    
    def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Stripe 결제 생성"""
        try:
            # 금액을 USD로 변환
            amount_krw = Decimal(str(data['amount']))
            amount_usd = self.convert_amount(amount_krw, 'KRW', 'USD')
            
            # Stripe는 센트 단위로 처리
            amount_cents = int(amount_usd * 100)
            
            # Payment Intent 생성
            payment_data = {
                'amount': amount_cents,
                'currency': 'usd',
                'metadata[merchant_uid]': data.get('merchant_uid', ''),
                'metadata[buyer_name]': data.get('buyer_name', ''),
                'metadata[buyer_email]': data.get('buyer_email', ''),
                'description': data.get('description', ''),
                'receipt_email': data.get('buyer_email', ''),
                'automatic_payment_methods[enabled]': 'true'
            }
            
            result = self._make_request('POST', 'payment_intents', payment_data)
            
            return {
                'success': True,
                'payment_id': result['id'],
                'client_secret': result['client_secret'],
                'amount': amount_cents,
                'currency': 'USD',
                'status': result['status']
            }
            
        except Exception as e:
            logger.error(f"Stripe payment creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Stripe 결제 검증"""
        try:
            result = self._make_request('GET', f'payment_intents/{payment_id}')
            
            return {
                'success': True,
                'payment_id': result['id'],
                'amount': result['amount'],
                'currency': result['currency'],
                'status': result['status'],
                'paid': result['status'] == 'succeeded'
            }
            
        except Exception as e:
            logger.error(f"Stripe payment verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_payment(self, payment_id: str, reason: str = '') -> Dict[str, Any]:
        """Stripe 결제 취소"""
        try:
            cancel_data = {
                'cancellation_reason': reason or 'requested_by_customer'
            }
            
            result = self._make_request('POST', f'payment_intents/{payment_id}/cancel', cancel_data)
            
            return {
                'success': True,
                'payment_id': result['id'],
                'status': result['status'],
                'cancelled': result['status'] == 'canceled'
            }
            
        except Exception as e:
            logger.error(f"Stripe payment cancellation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None, reason: str = '') -> Dict[str, Any]:
        """Stripe 결제 환불"""
        try:
            refund_data = {
                'payment_intent': payment_id,
                'reason': reason or 'requested_by_customer'
            }
            
            if amount:
                # 센트 단위로 변환
                refund_data['amount'] = int(amount * 100)
            
            result = self._make_request('POST', 'refunds', refund_data)
            
            return {
                'success': True,
                'refund_id': result['id'],
                'amount': result['amount'],
                'status': result['status']
            }
            
        except Exception as e:
            logger.error(f"Stripe refund error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class EnhancedPayPalGateway(BasePaymentGateway):
    """개선된 PayPal 결제 게이트웨이"""
    
    def __init__(self):
        super().__init__()
        self.name = 'paypal'
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
        self.sandbox = getattr(settings, 'PAYPAL_SANDBOX', True)
        
        if self.sandbox:
            self.base_url = 'https://api-m.sandbox.paypal.com'
        else:
            self.base_url = 'https://api-m.paypal.com'
        
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """PayPal 액세스 토큰 획득"""
        if self.access_token and self.token_expires_at and timezone.now() < self.token_expires_at:
            return self.access_token
        
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US'
            }
            data = 'grant_type=client_credentials'
            
            response = requests.post(
                url, 
                headers=headers, 
                data=data,
                auth=(self.client_id, self.client_secret),
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            self.access_token = result['access_token']
            expires_in = result.get('expires_in', 3600)
            self.token_expires_at = timezone.now() + timedelta(seconds=expires_in - 300)
            
            return self.access_token
            
        except Exception as e:
            logger.error(f"PayPal token error: {str(e)}")
            raise PaymentGatewayError(f"PayPal 인증 오류: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """PayPal API 요청"""
        token = self._get_access_token()
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, params=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PayPal API error: {str(e)}")
            raise PaymentGatewayError(f"PayPal API 오류: {str(e)}")
    
    def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PayPal 결제 생성"""
        try:
            # 금액을 USD로 변환
            amount_krw = Decimal(str(data['amount']))
            amount_usd = self.convert_amount(amount_krw, 'KRW', 'USD')
            
            payment_data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'reference_id': data.get('merchant_uid', ''),
                    'description': data.get('description', ''),
                    'amount': {
                        'currency_code': 'USD',
                        'value': str(amount_usd)
                    },
                    'payee': {
                        'email_address': data.get('buyer_email', '')
                    }
                }],
                'payment_source': {
                    'paypal': {
                        'experience_context': {
                            'payment_method_preference': 'IMMEDIATE_PAYMENT_REQUIRED',
                            'brand_name': '주식차트 예측 플랫폼',
                            'locale': 'ko-KR',
                            'landing_page': 'LOGIN',
                            'shipping_preference': 'NO_SHIPPING',
                            'user_action': 'PAY_NOW',
                            'return_url': data.get('success_url', ''),
                            'cancel_url': data.get('cancel_url', '')
                        }
                    }
                }
            }
            
            result = self._make_request('POST', 'v2/checkout/orders', payment_data)
            
            # 승인 URL 찾기
            approval_url = None
            for link in result.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break
            
            return {
                'success': True,
                'payment_id': result['id'],
                'approval_url': approval_url,
                'amount': str(amount_usd),
                'currency': 'USD',
                'status': result['status']
            }
            
        except Exception as e:
            logger.error(f"PayPal payment creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """PayPal 결제 검증"""
        try:
            result = self._make_request('GET', f'v2/checkout/orders/{payment_id}')
            
            return {
                'success': True,
                'payment_id': result['id'],
                'status': result['status'],
                'paid': result['status'] == 'COMPLETED'
            }
            
        except Exception as e:
            logger.error(f"PayPal payment verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def capture_payment(self, payment_id: str) -> Dict[str, Any]:
        """PayPal 결제 캡처"""
        try:
            result = self._make_request('POST', f'v2/checkout/orders/{payment_id}/capture')
            
            return {
                'success': True,
                'payment_id': result['id'],
                'status': result['status'],
                'captured': result['status'] == 'COMPLETED'
            }
            
        except Exception as e:
            logger.error(f"PayPal payment capture error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class CryptoPaymentGateway(BasePaymentGateway):
    """암호화폐 결제 게이트웨이 (CoinGate)"""
    
    def __init__(self):
        super().__init__()
        self.name = 'crypto'
        self.api_key = getattr(settings, 'COINGATE_API_KEY', '')
        self.sandbox = getattr(settings, 'COINGATE_SANDBOX', True)
        
        if self.sandbox:
            self.base_url = 'https://api-sandbox.coingate.com/v2'
        else:
            self.base_url = 'https://api.coingate.com/v2'
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """CoinGate API 요청"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, params=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGate API error: {str(e)}")
            raise PaymentGatewayError(f"CoinGate API 오류: {str(e)}")
    
    def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """암호화폐 결제 생성"""
        try:
            # 금액을 USD로 변환
            amount_krw = Decimal(str(data['amount']))
            amount_usd = self.convert_amount(amount_krw, 'KRW', 'USD')
            
            payment_data = {
                'order_id': data.get('merchant_uid', ''),
                'price_amount': str(amount_usd),
                'price_currency': 'USD',
                'receive_currency': 'USD',
                'title': data.get('description', ''),
                'description': data.get('description', ''),
                'callback_url': data.get('webhook_url', ''),
                'cancel_url': data.get('cancel_url', ''),
                'success_url': data.get('success_url', ''),
                'buyer_email': data.get('buyer_email', '')
            }
            
            result = self._make_request('POST', 'orders', payment_data)
            
            return {
                'success': True,
                'payment_id': result['id'],
                'payment_url': result['payment_url'],
                'amount': str(amount_usd),
                'currency': 'USD',
                'status': result['status']
            }
            
        except Exception as e:
            logger.error(f"Crypto payment creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """암호화폐 결제 검증"""
        try:
            result = self._make_request('GET', f'orders/{payment_id}')
            
            return {
                'success': True,
                'payment_id': result['id'],
                'status': result['status'],
                'paid': result['status'] == 'paid'
            }
            
        except Exception as e:
            logger.error(f"Crypto payment verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class InternationalPaymentManager:
    """국제 결제 관리자"""
    
    def __init__(self):
        self.gateways = {
            'stripe': StripeGateway(),
            'paypal': EnhancedPayPalGateway(),
            'crypto': CryptoPaymentGateway()
        }
    
    def get_gateway(self, provider: str) -> BasePaymentGateway:
        """결제 게이트웨이 획득"""
        gateway = self.gateways.get(provider)
        if not gateway:
            raise PaymentGatewayError(f"지원하지 않는 결제 제공업체: {provider}")
        return gateway
    
    def create_payment(self, provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """결제 생성"""
        gateway = self.get_gateway(provider)
        return gateway.create_payment(data)
    
    def verify_payment(self, provider: str, payment_id: str) -> Dict[str, Any]:
        """결제 검증"""
        gateway = self.get_gateway(provider)
        return gateway.verify_payment(payment_id)
    
    def cancel_payment(self, provider: str, payment_id: str, reason: str = '') -> Dict[str, Any]:
        """결제 취소"""
        gateway = self.get_gateway(provider)
        return gateway.cancel_payment(payment_id, reason)
    
    def refund_payment(self, provider: str, payment_id: str, amount: Optional[Decimal] = None, reason: str = '') -> Dict[str, Any]:
        """결제 환불"""
        gateway = self.get_gateway(provider)
        return gateway.refund_payment(payment_id, amount, reason)
    
    def get_supported_providers(self) -> list:
        """지원되는 결제 제공업체 목록"""
        return list(self.gateways.keys())


# 전역 인스턴스
international_payment_manager = InternationalPaymentManager()
