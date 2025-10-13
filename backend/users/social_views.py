"""
소셜 로그인 인증 뷰
"""

from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import json
import logging

from .social_services import SocialAuthManager, SocialAuthError
from .social_models import (
    SocialProvider, SocialAccount, SocialLoginAttempt, 
    SocialLoginSession, SocialConnectRequest
)
from .serializers import SocialAccountSerializer

logger = logging.getLogger(__name__)


class SocialAuthInitiateView(APIView):
    """소셜 로그인 시작"""
    permission_classes = [AllowAny]
    
    def get(self, request, provider_name):
        try:
            provider = SocialAuthManager.get_provider(provider_name)
            
            # 상태 토큰 생성
            state_token = SocialLoginAttempt.generate_state_token()
            
            # 세션에 정보 저장
            request.session[f'social_auth_state_{provider_name}'] = state_token
            request.session[f'social_auth_provider_{provider_name}'] = provider_name
            
            # 인증 URL 생성
            auth_url = provider.get_authorization_url(request, state_token)
            
            # 옵션: ?redirect=true 시 즉시 리다이렉트 (프런트엔드 단순 링크 대응)
            redirect_flag = request.GET.get('redirect') or request.GET.get('redirect_to_provider')
            if isinstance(redirect_flag, str):
                redirect_flag = redirect_flag.lower() in ('1', 'true', 'yes', 'y')
            if redirect_flag:
                return redirect(auth_url)
            
            return Response({
                'auth_url': auth_url,
                'state_token': state_token,
                'provider': provider_name
            })
            
        except SocialAuthError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Social auth initiate error: {str(e)}")
            return Response({
                'error': '소셜 로그인 초기화 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialAuthCallbackView(APIView):
    """소셜 로그인 콜백"""
    permission_classes = [AllowAny]
    
    def get(self, request, provider_name):
        return self._handle_callback(request, provider_name)
    
    def post(self, request, provider_name):
        return self._handle_callback(request, provider_name)
    
    def _handle_callback(self, request, provider_name):
        try:
            # 파라미터 획득
            if request.method == 'GET':
                code = request.GET.get('code')
                state = request.GET.get('state')
                error = request.GET.get('error')
            else:
                code = request.data.get('code')
                state = request.data.get('state')
                error = request.data.get('error')
            
            if error:
                return self._handle_auth_error(error, provider_name)
            
            if not code or not state:
                return Response({
                    'error': '필수 파라미터가 누락되었습니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 상태 토큰 검증
            session_state = request.session.get(f'social_auth_state_{provider_name}')
            if not session_state or session_state != state:
                return Response({
                    'error': '유효하지 않은 상태 토큰입니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 소셜 제공업체로 인증 처리
            provider = SocialAuthManager.get_provider(provider_name)
            auth_result = provider.exchange_code_for_token(code, state, request)
            
            if not auth_result['success']:
                return Response({
                    'error': '토큰 교환에 실패했습니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 사용자 인증
            user, created = SocialAuthManager.authenticate_user(auth_result['login_attempt'])
            
            # 소셜 로그인 세션 생성
            social_session = SocialLoginSession.objects.create(
                user=user,
                provider=SocialProvider.objects.get(name=provider_name),
                login_attempt=auth_result['login_attempt'],
                ip_address=provider.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_mobile=self._is_mobile_request(request)
            )
            
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # 세션 정리
            self._cleanup_session(request, provider_name)
            
            # 응답 데이터 구성
            response_data = {
                'success': True,
                'user_created': created,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': getattr(user, 'user_type', 'regular'),
                    'language_preference': getattr(user, 'language_preference', 'ko')
                },
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                },
                'social_account': {
                    'provider': provider_name,
                    'social_id': auth_result['user_info'].get('id'),
                    'email': auth_result['user_info'].get('email'),
                    'name': auth_result['user_info'].get('name'),
                    'profile_image': auth_result['user_info'].get('profile_image')
                },
                'session_id': social_session.session_id
            }
            
            # 프론트엔드로 리다이렉트 (웹에서 호출된 경우)
            if request.GET.get('redirect_to_frontend', '').lower() == 'true':
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                redirect_url = f"{frontend_url}/auth/social/success?"
                redirect_url += f"token={access_token}&refresh={refresh_token}&provider={provider_name}"
                if created:
                    redirect_url += "&created=true"
                return redirect(redirect_url)
            
            return Response(response_data)
            
        except SocialAuthError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Social auth callback error for {provider_name}: {str(e)}")
            return Response({
                'error': '소셜 로그인 처리 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _handle_auth_error(self, error, provider_name):
        """인증 오류 처리"""
        error_messages = {
            'access_denied': '사용자가 권한을 거부했습니다.',
            'unauthorized_client': '클라이언트 인증에 실패했습니다.',
            'invalid_request': '잘못된 요청입니다.',
            'unsupported_response_type': '지원하지 않는 응답 타입입니다.',
            'invalid_scope': '유효하지 않은 스코프입니다.',
            'server_error': '서버 오류가 발생했습니다.',
            'temporarily_unavailable': '일시적으로 사용할 수 없습니다.'
        }
        
        message = error_messages.get(error, f'소셜 로그인 오류: {error}')
        
        return Response({
            'error': message,
            'error_code': error,
            'provider': provider_name
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _is_mobile_request(self, request):
        """모바일 요청 확인"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_patterns = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
        return any(pattern in user_agent for pattern in mobile_patterns)
    
    def _cleanup_session(self, request, provider_name):
        """세션 정리"""
        keys_to_remove = [
            f'social_auth_state_{provider_name}',
            f'social_auth_provider_{provider_name}'
        ]
        for key in keys_to_remove:
            request.session.pop(key, None)


class SocialAccountListView(APIView):
    """사용자의 소셜 계정 목록"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            social_accounts = SocialAccount.objects.filter(
                user=request.user,
                is_active=True
            ).select_related('provider')
            
            serializer = SocialAccountSerializer(social_accounts, many=True)
            
            return Response({
                'social_accounts': serializer.data,
                'total_count': social_accounts.count()
            })
            
        except Exception as e:
            logger.error(f"Social account list error: {str(e)}")
            return Response({
                'error': '소셜 계정 목록 조회 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialAccountDisconnectView(APIView):
    """소셜 계정 연결 해제"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            provider_name = request.data.get('provider')
            social_id = request.data.get('social_id')
            
            if not provider_name:
                return Response({
                    'error': '제공업체 이름이 필요합니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                provider = SocialProvider.objects.get(name=provider_name)
                social_account = SocialAccount.objects.get(
                    user=request.user,
                    provider=provider,
                    social_id=social_id if social_id else None
                )
            except (SocialProvider.DoesNotExist, SocialAccount.DoesNotExist):
                return Response({
                    'error': '연결된 소셜 계정을 찾을 수 없습니다.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 마지막 소셜 계정인 경우 확인
            user_social_accounts = SocialAccount.objects.filter(
                user=request.user,
                is_active=True
            ).count()
            
            if user_social_accounts == 1 and not request.user.has_usable_password():
                return Response({
                    'error': '마지막 로그인 방법은 해제할 수 없습니다. 먼저 비밀번호를 설정해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 소셜 계정 비활성화 (완전 삭제하지 않음)
            social_account.disconnect()
            
            return Response({
                'message': '소셜 계정 연결이 해제되었습니다.',
                'provider': provider_name
            })
            
        except Exception as e:
            logger.error(f"Social account disconnect error: {str(e)}")
            return Response({
                'error': '소셜 계정 연결 해제 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialAccountConnectView(APIView):
    """기존 계정에 소셜 계정 연결"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            provider_name = request.data.get('provider')
            
            if not provider_name:
                return Response({
                    'error': '제공업체 이름이 필요합니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 연결 요청 생성
            connect_request = SocialConnectRequest.objects.create(
                user=request.user,
                provider=SocialProvider.objects.get(name=provider_name),
                ip_address=SocialAuthManager.get_provider(provider_name).get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # 인증 URL 생성
            provider = SocialAuthManager.get_provider(provider_name)
            auth_url = provider.get_authorization_url(
                request, 
                connect_request.request_token
            )
            
            return Response({
                'auth_url': auth_url,
                'request_token': connect_request.request_token,
                'provider': provider_name,
                'connect_request_id': connect_request.id
            })
            
        except SocialProvider.DoesNotExist:
            return Response({
                'error': '지원하지 않는 소셜 제공업체입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Social account connect error: {str(e)}")
            return Response({
                'error': '소셜 계정 연결 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def social_providers_list(request):
    """사용 가능한 소셜 제공업체 목록"""
    try:
        providers = SocialAuthManager.get_available_providers()
        
        return Response({
            'providers': providers,
            'total_count': len(providers)
        })
        
    except Exception as e:
        logger.error(f"Social providers list error: {str(e)}")
        return Response({
            'error': '소셜 제공업체 목록 조회 중 오류가 발생했습니다.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_social_token(request):
    """소셜 액세스 토큰 갱신"""
    try:
        provider_name = request.data.get('provider')
        
        if not provider_name:
            return Response({
                'error': '제공업체 이름이 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            provider = SocialProvider.objects.get(name=provider_name)
            social_account = SocialAccount.objects.get(
                user=request.user,
                provider=provider,
                is_active=True
            )
        except (SocialProvider.DoesNotExist, SocialAccount.DoesNotExist):
            return Response({
                'error': '연결된 소셜 계정을 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 토큰 갱신 시도
        if social_account.refresh_access_token():
            return Response({
                'message': '토큰이 성공적으로 갱신되었습니다.',
                'token_expires_at': social_account.token_expires_at.isoformat() if social_account.token_expires_at else None
            })
        else:
            return Response({
                'error': '토큰 갱신에 실패했습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Social token refresh error: {str(e)}")
        return Response({
            'error': '토큰 갱신 중 오류가 발생했습니다.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def social_logout(request):
    """소셜 로그인 세션 종료"""
    try:
        session_id = request.data.get('session_id')
        
        if session_id:
            try:
                social_session = SocialLoginSession.objects.get(
                    session_id=session_id,
                    user=request.user,
                    is_active=True
                )
                social_session.end_session()
            except SocialLoginSession.DoesNotExist:
                pass
        
        # 모든 활성 소셜 세션 종료
        SocialLoginSession.objects.filter(
            user=request.user,
            is_active=True
        ).update(
            is_active=False,
            logged_out_at=timezone.now()
        )
        
        # Django 세션 로그아웃
        logout(request)
        
        return Response({
            'message': '로그아웃되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"Social logout error: {str(e)}")
        return Response({
            'error': '로그아웃 중 오류가 발생했습니다.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 관리자용 뷰들

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def social_auth_stats(request):
    """소셜 인증 통계 (관리자용)"""
    if not request.user.is_staff:
        return Response({
            'error': '권한이 없습니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # 최근 30일 통계
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        stats = {
            'total_social_accounts': SocialAccount.objects.filter(is_active=True).count(),
            'accounts_by_provider': list(
                SocialAccount.objects.filter(is_active=True)
                .values('provider__name', 'provider__display_name')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'recent_logins': SocialLoginAttempt.objects.filter(
                created_at__gte=thirty_days_ago,
                status='success'
            ).count(),
            'failed_logins': SocialLoginAttempt.objects.filter(
                created_at__gte=thirty_days_ago,
                status='failed'
            ).count(),
            'active_sessions': SocialLoginSession.objects.filter(
                is_active=True
            ).count()
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Social auth stats error: {str(e)}")
        return Response({
            'error': '통계 조회 중 오류가 발생했습니다.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
