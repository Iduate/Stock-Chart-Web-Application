from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router 설정
router = DefaultRouter()
router.register(r'languages', views.LanguageViewSet, basename='language')
router.register(r'translations', views.TranslationViewSet, basename='translation')
router.register(r'translation-requests', views.TranslationRequestViewSet, basename='translation-request')

app_name = 'i18n'

urlpatterns = [
    # DRF API 엔드포인트
    path('api/', include(router.urls)),
    
    # 사용자 언어 설정
    path('api/user/language-preference/', views.UserLanguagePreferenceView.as_view(), name='user-language-preference'),
    
    # 언어 감지
    path('api/detect-language/', views.LanguageDetectionView.as_view(), name='detect-language'),
    
    # 자동 번역
    path('api/auto-translate/', views.AutoTranslationView.as_view(), name='auto-translate'),
]
