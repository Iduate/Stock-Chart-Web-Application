from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
from charts.views import get_rankings, get_events
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/status/', views.api_status, name='api_status'),
    path('api/auth/', include('users.urls')),
    path('api/charts/', include('charts.urls')),
    path('api/payments/', include('payment_system.urls')),
    path('api/market-data/', include('market_data.urls')),
    # Direct market endpoints for compatibility
    path('api/market/stocks/', views.market_stocks_redirect, name='market_stocks_redirect'),
    # 추가 API 엔드포인트
    path('api/rankings/<str:ranking_type>/', get_rankings, name='rankings'),
    path('api/events/', get_events, name='events'),
    # 홈페이지는 마지막에 위치 (모든 static 파일 처리 후)
    path('', views.home, name='home'),
]

# 정적 파일 서빙 설정 (개발 및 프로덕션 모두)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Railway에서 정적 파일이 제대로 서빙되도록 추가 설정
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]

# 관리자 사이트 한국어 설정
admin.site.site_header = "주식차트 예측 플랫폼 관리자"
admin.site.site_title = "StockChart 관리자"
admin.site.index_title = "관리자 대시보드"
