"""
소셜 로그인 인증 서비스
"""

import requests
import secrets
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from users.social_models import (
        SocialProvider, SocialAccount, SocialLoginAttempt,
        SocialAuthConfig, SocialLoginSession,
    )
    User = AbstractUser
else:
    from users.social_models import (
        SocialProvider, SocialAccount, SocialLoginAttempt,
        SocialAuthConfig, SocialLoginSession,
    )
    User = get_user_model()

logger = logging.getLogger(__name__)


class SocialAuthError(Exception):
    """소셜 인증 오류"""
    pass


class BaseSocialProvider:
    """기본 소셜 제공업체 클래스"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        try:
            self.provider = SocialProvider.objects.get(name=provider_name, is_active=True)
            self.config = SocialAuthConfig.objects.get(provider=self.provider)
        except (SocialProvider.DoesNotExist, SocialAuthConfig.DoesNotExist):
            raise SocialAuthError(f"소셜 제공업체 '{provider_name}' 설정을 찾을 수 없습니다.")
    
    def get_authorization_url(self, request, state_token: str = None) -> str:
        """인증 URL 생성"""
        if not state_token:
            state_token = SocialLoginAttempt.generate_state_token()
        
        # 로그인 시도 기록
        SocialLoginAttempt.objects.create(
            provider=self.provider,
            state_token=state_token,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        params = {
            'client_id': self.provider.client_id,
            'response_type': 'code',
            'scope': self.provider.scope,
            'state': state_token,
            'redirect_uri': self.get_redirect_uri(request)
        }
        
        # 제공업체별 추가 파라미터
        params.update(self.get_additional_auth_params())
        
        return f"{self.provider.authorization_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, state: str, request) -> Dict[str, Any]:
        """인증 코드를 토큰으로 교환"""
        try:
            # 상태 토큰 검증
            login_attempt = SocialLoginAttempt.objects.get(
                provider=self.provider,
                state_token=state,
                status='pending'
            )
            
            # 토큰 요청
            token_data = {
                'client_id': self.provider.client_id,
                'client_secret': self.provider.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.get_redirect_uri(request)
            }
            
            response = requests.post(
                self.provider.token_url,
                data=token_data,
                headers={'Accept': 'application/json'},
                timeout=30
            )
            
            if response.status_code != 200:
                raise SocialAuthError(f"토큰 요청 실패: {response.text}")
            
            token_response = response.json()
            
            if 'error' in token_response:
                raise SocialAuthError(f"토큰 오류: {token_response.get('error_description', token_response['error'])}")
            
            # 사용자 정보 조회
            user_info = self.get_user_info(token_response['access_token'])
            
            # 로그인 시도 업데이트
            login_attempt.social_id = user_info.get('id', '')
            login_attempt.extra_data = {
                'token_response': token_response,
                'user_info': user_info
            }
            login_attempt.save()
            
            return {
                'success': True,
                'token_data': token_response,
                'user_info': user_info,
                'login_attempt': login_attempt
            }
            
        except SocialLoginAttempt.DoesNotExist:
            raise SocialAuthError("유효하지 않은 상태 토큰입니다.")
        except Exception as e:
            logger.error(f"Social auth error for {self.provider_name}: {str(e)}")
            raise SocialAuthError(str(e))
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """사용자 정보 조회"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(
            self.provider.user_info_url,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise SocialAuthError(f"사용자 정보 조회 실패: {response.text}")
        
        return self.normalize_user_info(response.json())
    
    def normalize_user_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 정보 정규화 (제공업체별 구현 필요)"""
        return raw_data
    
    def get_additional_auth_params(self) -> Dict[str, str]:
        """추가 인증 파라미터 (제공업체별 구현)"""
        return {}
    
    def get_redirect_uri(self, request) -> str:
        """리다이렉트 URI 생성"""
        # Respect reverse proxy headers (Render/NGINX) for HTTPS
        xf_proto = request.META.get('HTTP_X_FORWARDED_PROTO')
        if xf_proto:
            scheme = 'https' if 'https' in xf_proto.split(',')[0].lower() else 'http'
        else:
            scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return f"{scheme}://{host}/api/auth/social/{self.provider_name}/callback/"
    
    def get_client_ip(self, request):
        """클라이언트 IP 주소 획득"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GoogleProvider(BaseSocialProvider):
    """Google 소셜 제공업체"""
    
    def __init__(self):
        super().__init__('google')
    
    def normalize_user_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': raw_data.get('sub', raw_data.get('id')),
            'email': raw_data.get('email'),
            'name': raw_data.get('name'),
            'first_name': raw_data.get('given_name'),
            'last_name': raw_data.get('family_name'),
            'profile_image': raw_data.get('picture'),
            'verified_email': raw_data.get('email_verified', False),
            'locale': raw_data.get('locale', 'ko')
        }


class FacebookProvider(BaseSocialProvider):
    """Facebook 소셜 제공업체"""
    
    def __init__(self):
        super().__init__('facebook')
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Facebook 사용자 정보 조회"""
        fields = 'id,name,email,first_name,last_name,picture,verified,locale'
        url = f"{self.provider.user_info_url}?fields={fields}&access_token={access_token}"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            raise SocialAuthError(f"사용자 정보 조회 실패: {response.text}")
        
        return self.normalize_user_info(response.json())
    
    def normalize_user_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': raw_data.get('id'),
            'email': raw_data.get('email'),
            'name': raw_data.get('name'),
            'first_name': raw_data.get('first_name'),
            'last_name': raw_data.get('last_name'),
            'profile_image': raw_data.get('picture', {}).get('data', {}).get('url'),
            'verified_email': raw_data.get('verified', False),
            'locale': raw_data.get('locale', 'ko_KR')
        }


class NaverProvider(BaseSocialProvider):
    """Naver 소셜 제공업체"""
    
    def __init__(self):
        super().__init__('naver')
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Naver 사용자 정보 조회"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(
            self.provider.user_info_url,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise SocialAuthError(f"사용자 정보 조회 실패: {response.text}")
        
        data = response.json()
        if data.get('resultcode') != '00':
            raise SocialAuthError(f"Naver API 오류: {data.get('message')}")
        
        return self.normalize_user_info(data.get('response', {}))
    
    def normalize_user_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': raw_data.get('id'),
            'email': raw_data.get('email'),
            'name': raw_data.get('name'),
            'first_name': raw_data.get('name'),  # Naver는 성/이름 구분 없음
            'last_name': '',
            'profile_image': raw_data.get('profile_image'),
            'verified_email': True,  # Naver는 기본적으로 인증된 이메일
            'locale': 'ko'
        }


class KakaoProvider(BaseSocialProvider):
    """Kakao 소셜 제공업체"""
    
    def __init__(self):
        super().__init__('kakao')
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Kakao 사용자 정보 조회"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(
            self.provider.user_info_url,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise SocialAuthError(f"사용자 정보 조회 실패: {response.text}")
        
        return self.normalize_user_info(response.json())
    
    def normalize_user_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        kakao_account = raw_data.get('kakao_account', {})
        profile = kakao_account.get('profile', {})
        
        return {
            'id': str(raw_data.get('id')),
            'email': kakao_account.get('email'),
            'name': profile.get('nickname'),
            'first_name': profile.get('nickname'),
            'last_name': '',
            'profile_image': profile.get('profile_image_url'),
            'verified_email': kakao_account.get('is_email_verified', False),
            'locale': 'ko'
        }


class AppleProvider(BaseSocialProvider):
    """Apple 소셜 제공업체"""
    
    def __init__(self):
        super().__init__('apple')
    
    def get_additional_auth_params(self) -> Dict[str, str]:
        return {
            'response_mode': 'form_post'
        }
    
    def normalize_user_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # Apple ID 토큰은 JWT 형태로 제공됨
        # 실제 구현 시 JWT 디코딩 필요
        return {
            'id': raw_data.get('sub'),
            'email': raw_data.get('email'),
            'name': raw_data.get('name'),
            'first_name': raw_data.get('given_name'),
            'last_name': raw_data.get('family_name'),
            'profile_image': '',
            'verified_email': raw_data.get('email_verified', True),
            'locale': 'ko'
        }


class SocialAuthManager:
    """소셜 인증 관리자"""
    
    providers = {
        'google': GoogleProvider,
        'facebook': FacebookProvider,
        'naver': NaverProvider,
        'kakao': KakaoProvider,
        'apple': AppleProvider,
    }
    
    @classmethod
    def get_provider(cls, provider_name: str) -> BaseSocialProvider:
        """소셜 제공업체 인스턴스 획득"""
        provider_class = cls.providers.get(provider_name)
        if not provider_class:
            raise SocialAuthError(f"지원하지 않는 소셜 제공업체: {provider_name}")
        
        return provider_class()
    
    @classmethod
    def authenticate_user(cls, login_attempt: 'SocialLoginAttempt') -> Tuple['User', bool]:
        """사용자 인증 및 생성"""
        provider = cls.get_provider(login_attempt.provider.name)
        user_info = login_attempt.extra_data.get('user_info', {})
        token_data = login_attempt.extra_data.get('token_data', {})
        
        social_id = user_info.get('id')
        email = user_info.get('email')
        
        if not social_id:
            raise SocialAuthError("소셜 ID를 찾을 수 없습니다.")
        
        # 기존 소셜 계정 확인
        try:
            social_account = SocialAccount.objects.get(
                provider=login_attempt.provider,
                social_id=social_id
            )
            user = social_account.user
            created = False
            
            # 토큰 정보 업데이트
            cls.update_social_account_tokens(social_account, token_data, user_info)
            
        except SocialAccount.DoesNotExist:
            # 이메일로 기존 사용자 확인
            user = None
            if email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    pass
            
            # 새 사용자 생성 또는 소셜 계정 연동
            if user:
                # 기존 사용자에 소셜 계정 연동
                social_account = cls.create_social_account(
                    user, login_attempt.provider, social_id, token_data, user_info
                )
                created = False
            else:
                # 새 사용자 생성
                if not provider.config.auto_create_user:
                    raise SocialAuthError("자동 사용자 생성이 비활성화되어 있습니다.")
                
                user = cls.create_user_from_social(user_info, provider.config)
                social_account = cls.create_social_account(
                    user, login_attempt.provider, social_id, token_data, user_info
                )
                created = True
        
        # 로그인 시도 완료 처리
        login_attempt.mark_completed('success', user)
        
        # 소셜 계정 마지막 로그인 업데이트
        social_account.update_last_login()
        
        return user, created
    
    @classmethod
    def create_user_from_social(cls, user_info: Dict[str, Any], config: 'SocialAuthConfig') -> 'User':
        """소셜 정보로 새 사용자 생성"""
        email = user_info.get('email')
        name = user_info.get('name', '')
        first_name = user_info.get('first_name', '')
        last_name = user_info.get('last_name', '')
        
        if not email:
            raise SocialAuthError("이메일 정보가 필요합니다.")
        
        # 사용자명 생성 (이메일 기반)
        username = email.split('@')[0]
        base_username = username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=config.default_user_type,
            language_preference=user_info.get('locale', 'ko')[:2]
        )
        
        # 프로필 이미지 URL 저장 (별도 필드가 있다면)
        if hasattr(user, 'profile_image_url') and user_info.get('profile_image'):
            user.profile_image_url = user_info['profile_image']
            user.save()
        
        return user
    
    @classmethod
    def create_social_account(cls, user: 'User', provider: 'SocialProvider', 
                            social_id: str, token_data: Dict[str, Any], 
                            user_info: Dict[str, Any]) -> 'SocialAccount':
        """소셜 계정 생성"""
        expires_at = None
        if 'expires_in' in token_data:
            expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
        
        social_account = SocialAccount.objects.create(
            user=user,
            provider=provider,
            social_id=social_id,
            email=user_info.get('email', ''),
            name=user_info.get('name', ''),
            profile_image_url=user_info.get('profile_image', ''),
            access_token=token_data.get('access_token', ''),
            refresh_token=token_data.get('refresh_token', ''),
            token_expires_at=expires_at,
            extra_data=user_info,
            is_verified=user_info.get('verified_email', False),
            is_primary=not user.social_accounts.exists()  # 첫 번째 소셜 계정을 주 계정으로 설정
        )
        
        return social_account
    
    @classmethod
    def update_social_account_tokens(cls, social_account: SocialAccount, 
                                   token_data: Dict[str, Any], 
                                   user_info: Dict[str, Any]):
        """소셜 계정 토큰 정보 업데이트"""
        social_account.access_token = token_data.get('access_token', social_account.access_token)
        social_account.refresh_token = token_data.get('refresh_token', social_account.refresh_token)
        
        if 'expires_in' in token_data:
            social_account.token_expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
        
        # 프로필 동기화 설정 확인
        try:
            config = SocialAuthConfig.objects.get(provider=social_account.provider)
            if config.sync_profile_data and config.sync_on_login:
                social_account.email = user_info.get('email', social_account.email)
                social_account.name = user_info.get('name', social_account.name)
                social_account.profile_image_url = user_info.get('profile_image', social_account.profile_image_url)
                social_account.extra_data = user_info
        except SocialAuthConfig.DoesNotExist:
            pass
        
        social_account.save()
    
    @classmethod
    def get_available_providers(cls) -> list:
        """사용 가능한 소셜 제공업체 목록"""
        return list(SocialProvider.objects.filter(is_active=True).values(
            'name', 'display_name', 'icon_url'
        ))
