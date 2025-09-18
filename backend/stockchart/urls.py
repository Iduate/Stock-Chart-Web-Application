from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
from .static_serve import serve_static_with_mime, serve_frontend_file
from charts.views import get_rankings, get_events
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/status/', views.api_status, name='api_status'),
    path('api/auth/', include('users.urls')),
    path('api/charts/', include('charts.urls')),
    path('api/payments/', include('payment_system.urls')),
    # path('api/korean-payments/', include('korean_payments.urls')),  # 한국 결제 게이트웨이 API - Temporarily disabled
    path('api/market-data/', include('market_data.urls')),
    # path('api/affiliates/', include('affiliates.urls')),  # 새로 추가된 홍보파트너 API - Temporarily disabled for Railway deployment
    path('api/i18n/', include('i18n.urls')),  # 다국어 지원 API
    # Direct market endpoints for compatibility
    path('api/market/stocks/', views.market_stocks_redirect, name='market_stocks_redirect'),
    # 추가 API 엔드포인트
    path('api/rankings/<str:ranking_type>/', get_rankings, name='rankings'),
    path('api/events/', get_events, name='events'),
    
    # Multi-page HTML routes
    path('home.html', views.serve_html_page, {'page_name': 'home.html'}, name='home_page'),
    path('charts.html', views.serve_html_page, {'page_name': 'charts.html'}, name='charts_page'),
    path('prediction.html', views.serve_html_page, {'page_name': 'prediction.html'}, name='prediction_page'),
    path('my-predictions.html', views.serve_html_page, {'page_name': 'my-predictions.html'}, name='my_predictions_page'),
    path('ranking.html', views.serve_html_page, {'page_name': 'ranking.html'}, name='ranking_page'),
    path('events.html', views.serve_html_page, {'page_name': 'events.html'}, name='events_page'),
    path('subscription.html', views.serve_html_page, {'page_name': 'subscription.html'}, name='subscription_page'),
    path('payment.html', views.serve_html_page, {'page_name': 'payment.html'}, name='payment_page'),  # 결제 페이지 추가
    path('partners.html', views.serve_html_page, {'page_name': 'partners.html'}, name='partners_page'),  # 파트너 페이지 추가
    
    # 홈페이지는 마지막에 위치 (모든 static 파일 처리 후)
    path('', views.home, name='home'),
]

# Frontend 파일 직접 서빙 (최우선)
urlpatterns.insert(0, re_path(r'^(?P<path>(?:js|css|images)/.*\.(js|css|png|jpg|jpeg|gif|ico|svg))$', serve_frontend_file, name='serve_frontend'))
# 정적 파일 서빙 설정 - 커스텀 MIME 타입 핸들링
urlpatterns.insert(1, re_path(r'^static/(?P<path>.*)$', serve_static_with_mime, name='serve_static_custom'))

# 백업 정적 파일 서빙 (표준 방식)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 관리자 사이트 한국어 설정
admin.site.site_header = "주식차트 예측 플랫폼 관리자"
admin.site.site_title = "StockChart 관리자"
admin.site.index_title = "관리자 대시보드"
