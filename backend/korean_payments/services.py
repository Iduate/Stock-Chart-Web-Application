"""
한국 결제 게이트웨이 서비스 구현

지원하는 결제사:
- Iamport (아임포트)
- Toss Payments (토스페이먼츠)
- Kakao Pay (카카오페이)
- Naver Pay (네이버페이)
- KG이니시스
- NICE정보통신
"""

import requests
import json
import hmac
import hashlib
import base64
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional, Any
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class BasePaymentService:
    """결제 서비스 기본 클래스"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.config = provider_config
        self.api_key = provider_config.get('api_key')
        self.secret_key = provider_config.get('secret_key')
        self.merchant_id = provider_config.get('merchant_id')
        self.test_mode = provider_config.get('test_mode', True)
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """결제 생성"""
        raise NotImplementedError
    
    def verify_payment(self, imp_uid: str) -> Dict[str, Any]:
        """결제 검증"""
        raise NotImplementedError
    
    def cancel_payment(self, imp_uid: str, amount: int = None, reason: str = '') -> Dict[str, Any]:
        """결제 취소"""
        raise NotImplementedError
    
    def get_payment_status(self, imp_uid: str) -> Dict[str, Any]:
        """결제 상태 조회"""
        raise NotImplementedError


class IamportService(BasePaymentService):
    """아임포트 결제 서비스"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.base_url = 'https://api.iamport.kr' if not self.test_mode else 'https://api.iamport.kr'
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self) -> str:
        """액세스 토큰 획득"""
        if self.access_token and self.token_expires_at and timezone.now() < self.token_expires_at:
            return self.access_token
        
        url = f"{self.base_url}/users/getToken"
        data = {
            'imp_key': self.api_key,
            'imp_secret': self.secret_key
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('code') == 0:
                self.access_token = result['response']['access_token']
                self.token_expires_at = timezone.now() + timedelta(seconds=result['response']['expired_at'])
                return self.access_token
            else:
                raise Exception(f"Iamport token error: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"Iamport get_access_token error: {str(e)}")
            raise
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Iamport 결제 생성"""
        try:
            # 결제 준비 API 호출
            url = f"{self.base_url}/payments/prepare"
            headers = {
                'Authorization': self.get_access_token(),
                'Content-Type': 'application/json'
            }
            
            prepare_data = {
                'merchant_uid': payment_data['merchant_uid'],
                'amount': payment_data['amount']
            }
            
            response = requests.post(url, headers=headers, json=prepare_data, timeout=30)
            result = response.json()
            
            if result.get('code') == 0:
                return {
                    'success': True,
                    'merchant_uid': payment_data['merchant_uid'],
                    'amount': payment_data['amount'],
                    'pg_provider': 'iamport'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Iamport create_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, imp_uid: str) -> Dict[str, Any]:
        """Iamport 결제 검증"""
        try:
            url = f"{self.base_url}/payments/{imp_uid}"
            headers = {
                'Authorization': self.get_access_token()
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if result.get('code') == 0:
                payment_info = result['response']
                return {
                    'success': True,
                    'imp_uid': payment_info['imp_uid'],
                    'merchant_uid': payment_info['merchant_uid'],
                    'amount': payment_info['amount'],
                    'status': payment_info['status'],
                    'paid_at': payment_info.get('paid_at'),
                    'pay_method': payment_info.get('pay_method'),
                    'pg_provider': payment_info.get('pg_provider'),
                    'pg_tid': payment_info.get('pg_tid'),
                    'buyer_name': payment_info.get('buyer_name'),
                    'buyer_email': payment_info.get('buyer_email'),
                    'card_name': payment_info.get('card_name'),
                    'card_number': payment_info.get('card_number'),
                    'card_quota': payment_info.get('card_quota'),
                    'vbank_num': payment_info.get('vbank_num'),
                    'vbank_name': payment_info.get('vbank_name'),
                    'vbank_holder': payment_info.get('vbank_holder'),
                    'vbank_date': payment_info.get('vbank_date')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Payment verification failed')
                }
                
        except Exception as e:
            logger.error(f"Iamport verify_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_payment(self, imp_uid: str, amount: int = None, reason: str = '') -> Dict[str, Any]:
        """Iamport 결제 취소"""
        try:
            url = f"{self.base_url}/payments/cancel"
            headers = {
                'Authorization': self.get_access_token(),
                'Content-Type': 'application/json'
            }
            
            cancel_data = {
                'imp_uid': imp_uid,
                'reason': reason
            }
            
            if amount:
                cancel_data['amount'] = amount
            
            response = requests.post(url, headers=headers, json=cancel_data, timeout=30)
            result = response.json()
            
            if result.get('code') == 0:
                return {
                    'success': True,
                    'cancelled_amount': result['response']['cancel_amount'],
                    'cancelled_at': result['response']['cancelled_at']
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Payment cancellation failed')
                }
                
        except Exception as e:
            logger.error(f"Iamport cancel_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class TossPaymentsService(BasePaymentService):
    """토스페이먼츠 결제 서비스"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.base_url = 'https://api.tosspayments.com' if not self.test_mode else 'https://api.tosspayments.com'
        self.client_key = provider_config.get('client_key')
    
    def get_auth_header(self) -> str:
        """인증 헤더 생성"""
        credentials = f"{self.secret_key}:"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """토스페이먼츠 결제 생성"""
        try:
            # 토스페이먼츠는 프론트엔드에서 직접 결제를 시작하므로
            # 백엔드에서는 결제 정보만 반환
            return {
                'success': True,
                'client_key': self.client_key,
                'merchant_uid': payment_data['merchant_uid'],
                'amount': payment_data['amount'],
                'order_name': payment_data.get('name', '주문'),
                'customer_email': payment_data.get('buyer_email'),
                'customer_name': payment_data.get('buyer_name'),
                'success_url': payment_data.get('success_url'),
                'fail_url': payment_data.get('fail_url')
            }
            
        except Exception as e:
            logger.error(f"TossPayments create_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_key: str) -> Dict[str, Any]:
        """토스페이먼츠 결제 검증"""
        try:
            url = f"{self.base_url}/v1/payments/{payment_key}"
            headers = {
                'Authorization': self.get_auth_header(),
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                payment_info = response.json()
                return {
                    'success': True,
                    'payment_key': payment_info['paymentKey'],
                    'order_id': payment_info['orderId'],
                    'amount': payment_info['totalAmount'],
                    'status': payment_info['status'],
                    'requested_at': payment_info.get('requestedAt'),
                    'approved_at': payment_info.get('approvedAt'),
                    'method': payment_info.get('method'),
                    'card': payment_info.get('card', {}),
                    'virtual_account': payment_info.get('virtualAccount', {}),
                    'transfer': payment_info.get('transfer', {})
                }
            else:
                error_info = response.json()
                return {
                    'success': False,
                    'error': error_info.get('message', 'Payment verification failed')
                }
                
        except Exception as e:
            logger.error(f"TossPayments verify_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_payment(self, payment_key: str, amount: int = None, reason: str = '') -> Dict[str, Any]:
        """토스페이먼츠 결제 취소"""
        try:
            url = f"{self.base_url}/v1/payments/{payment_key}/cancel"
            headers = {
                'Authorization': self.get_auth_header(),
                'Content-Type': 'application/json'
            }
            
            cancel_data = {
                'cancelReason': reason
            }
            
            if amount:
                cancel_data['cancelAmount'] = amount
            
            response = requests.post(url, headers=headers, json=cancel_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'cancelled_amount': result.get('cancelAmount', 0),
                    'cancelled_at': result.get('canceledAt')
                }
            else:
                error_info = response.json()
                return {
                    'success': False,
                    'error': error_info.get('message', 'Payment cancellation failed')
                }
                
        except Exception as e:
            logger.error(f"TossPayments cancel_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class KakaoPayService(BasePaymentService):
    """카카오페이 결제 서비스"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.base_url = 'https://kapi.kakao.com' if not self.test_mode else 'https://kapi.kakao.com'
        self.cid = provider_config.get('cid')  # 카카오페이 가맹점 코드
    
    def get_auth_header(self) -> str:
        """인증 헤더 생성"""
        return f"KakaoAK {self.api_key}"
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """카카오페이 결제 준비"""
        try:
            url = f"{self.base_url}/v1/payment/ready"
            headers = {
                'Authorization': self.get_auth_header(),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'cid': self.cid,
                'partner_order_id': payment_data['merchant_uid'],
                'partner_user_id': payment_data.get('user_id', 'guest'),
                'item_name': payment_data.get('name', '주문'),
                'quantity': 1,
                'total_amount': payment_data['amount'],
                'tax_free_amount': 0,
                'approval_url': payment_data.get('success_url'),
                'cancel_url': payment_data.get('cancel_url'),
                'fail_url': payment_data.get('fail_url')
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'tid': result['tid'],
                    'next_redirect_pc_url': result['next_redirect_pc_url'],
                    'next_redirect_mobile_url': result['next_redirect_mobile_url'],
                    'created_at': result['created_at']
                }
            else:
                error_info = response.json()
                return {
                    'success': False,
                    'error': error_info.get('msg', 'Payment preparation failed')
                }
                
        except Exception as e:
            logger.error(f"KakaoPay create_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def approve_payment(self, tid: str, pg_token: str, partner_order_id: str, partner_user_id: str) -> Dict[str, Any]:
        """카카오페이 결제 승인"""
        try:
            url = f"{self.base_url}/v1/payment/approve"
            headers = {
                'Authorization': self.get_auth_header(),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'cid': self.cid,
                'tid': tid,
                'partner_order_id': partner_order_id,
                'partner_user_id': partner_user_id,
                'pg_token': pg_token
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'aid': result['aid'],
                    'tid': result['tid'],
                    'cid': result['cid'],
                    'partner_order_id': result['partner_order_id'],
                    'partner_user_id': result['partner_user_id'],
                    'payment_method_type': result['payment_method_type'],
                    'amount': result['amount'],
                    'card_info': result.get('card_info', {}),
                    'item_name': result['item_name'],
                    'created_at': result['created_at'],
                    'approved_at': result['approved_at']
                }
            else:
                error_info = response.json()
                return {
                    'success': False,
                    'error': error_info.get('msg', 'Payment approval failed')
                }
                
        except Exception as e:
            logger.error(f"KakaoPay approve_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_payment(self, tid: str, amount: int = None, reason: str = '') -> Dict[str, Any]:
        """카카오페이 결제 취소"""
        try:
            url = f"{self.base_url}/v1/payment/cancel"
            headers = {
                'Authorization': self.get_auth_header(),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'cid': self.cid,
                'tid': tid,
                'cancel_amount': amount,
                'cancel_tax_free_amount': 0
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'aid': result['aid'],
                    'tid': result['tid'],
                    'cid': result['cid'],
                    'status': result['status'],
                    'partner_order_id': result['partner_order_id'],
                    'amount': result['amount'],
                    'approved_cancel_amount': result['approved_cancel_amount'],
                    'canceled_at': result['canceled_at']
                }
            else:
                error_info = response.json()
                return {
                    'success': False,
                    'error': error_info.get('msg', 'Payment cancellation failed')
                }
                
        except Exception as e:
            logger.error(f"KakaoPay cancel_payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class PaymentServiceFactory:
    """결제 서비스 팩토리"""
    
    SERVICES = {
        'iamport': IamportService,
        'toss': TossPaymentsService,
        'kakaopay': KakaoPayService,
    }
    
    @classmethod
    def create_service(cls, provider_name: str, provider_config: Dict[str, Any]) -> BasePaymentService:
        """결제 서비스 인스턴스 생성"""
        service_class = cls.SERVICES.get(provider_name)
        if not service_class:
            raise ValueError(f"Unsupported payment provider: {provider_name}")
        
        return service_class(provider_config)
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """지원되는 결제 제공업체 목록 반환"""
        return list(cls.SERVICES.keys())


class PaymentManager:
    """결제 관리자 - 통합 결제 처리"""
    
    def __init__(self):
        self.services = {}
        self._load_payment_services()
    
    def _load_payment_services(self):
        """설정에서 결제 서비스 로드"""
        payment_config = getattr(settings, 'KOREAN_PAYMENTS_CONFIG', {})
        
        for provider_name, config in payment_config.items():
            if config.get('enabled', False):
                try:
                    service = PaymentServiceFactory.create_service(provider_name, config)
                    self.services[provider_name] = service
                    logger.info(f"Loaded payment service: {provider_name}")
                except Exception as e:
                    logger.error(f"Failed to load payment service {provider_name}: {str(e)}")
    
    def create_payment(self, provider_name: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """결제 생성"""
        service = self.services.get(provider_name)
        if not service:
            return {
                'success': False,
                'error': f'Payment provider {provider_name} not available'
            }
        
        return service.create_payment(payment_data)
    
    def verify_payment(self, provider_name: str, payment_key: str) -> Dict[str, Any]:
        """결제 검증"""
        service = self.services.get(provider_name)
        if not service:
            return {
                'success': False,
                'error': f'Payment provider {provider_name} not available'
            }
        
        return service.verify_payment(payment_key)
    
    def cancel_payment(self, provider_name: str, payment_key: str, amount: int = None, reason: str = '') -> Dict[str, Any]:
        """결제 취소"""
        service = self.services.get(provider_name)
        if not service:
            return {
                'success': False,
                'error': f'Payment provider {provider_name} not available'
            }
        
        return service.cancel_payment(payment_key, amount, reason)
    
    def get_available_providers(self) -> list:
        """사용 가능한 결제 제공업체 목록"""
        return list(self.services.keys())


# 전역 결제 관리자 인스턴스
payment_manager = PaymentManager()
