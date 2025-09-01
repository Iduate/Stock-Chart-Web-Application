from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('api/status/', views.api_status, name='api_status'),
    path('api/auth/', include('users.urls')),
    path('api/charts/', include('charts.urls')),
    path('api/payments/', include('payment_system.urls')),
    path('api/market/', include('market_data.urls')),
]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 관리자 사이트 한국어 설정
admin.site.site_header = "주식차트 예측 플랫폼 관리자"
admin.site.site_title = "StockChart 관리자"
admin.site.index_title = "관리자 대시보드"
