"""
소셜 인증 URL 설정
"""

from django.urls import path, include
from .social_views import (
    SocialAuthInitiateView,
    SocialAuthCallbackView,
    SocialAccountListView,
    SocialAccountDisconnectView,
    SocialAccountConnectView,
    social_providers_list,
    refresh_social_token,
    social_logout,
    social_auth_stats
)

app_name = 'social_auth'

urlpatterns = [
    # 소셜 로그인 플로우
    path('social/<str:provider_name>/login/', 
         SocialAuthInitiateView.as_view(), 
         name='social_login_initiate'),
    
    path('social/<str:provider_name>/callback/', 
         SocialAuthCallbackView.as_view(), 
         name='social_login_callback'),
    
    # 소셜 계정 관리
    path('social/accounts/', 
         SocialAccountListView.as_view(), 
         name='social_accounts_list'),
    
    path('social/accounts/disconnect/', 
         SocialAccountDisconnectView.as_view(), 
         name='social_account_disconnect'),
    
    path('social/accounts/connect/', 
         SocialAccountConnectView.as_view(), 
         name='social_account_connect'),
    
    # 유틸리티 엔드포인트
    path('social/providers/', 
         social_providers_list, 
         name='social_providers_list'),
    
    path('social/token/refresh/', 
         refresh_social_token, 
         name='refresh_social_token'),
    
    path('social/logout/', 
         social_logout, 
         name='social_logout'),
    
    # 관리자용
    path('social/stats/', 
         social_auth_stats, 
         name='social_auth_stats'),
]
