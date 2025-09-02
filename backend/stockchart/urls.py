from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
from charts.views import get_rankings, get_events
import os

urlpatterns = [
    path('', views.home, name='home'),
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
]

# 개발 환경에서 미디어 파일 및 정적 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # frontend 디렉토리의 정적 파일들을 직접 서빙
    frontend_static_dirs = [
        os.path.join(settings.BASE_DIR.parent, 'frontend'),
    ]
    
    for static_dir in frontend_static_dirs:
        if os.path.exists(static_dir):
            urlpatterns += static(settings.STATIC_URL, document_root=static_dir)

# 관리자 사이트 한국어 설정
admin.site.site_header = "주식차트 예측 플랫폼 관리자"
admin.site.site_title = "StockChart 관리자"
admin.site.index_title = "관리자 대시보드"
