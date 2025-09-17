from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'predictions', views.ChartPredictionViewSet, basename='chartprediction')
router.register(r'markets', views.MarketViewSet)
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    # Simple endpoints first (before router)
    path('charts/', views.get_charts, name='get_charts'),
    path('rankings/', views.get_rankings, name='get_rankings'),
    path('events/', views.get_events, name='get_events'),
    
    # 독립적인 AI 예측 API 엔드포인트들
    path('predictions/create_ai_prediction/', views.create_ai_prediction_api, name='create_ai_prediction_api'),
    path('predictions/available_symbols/', views.available_symbols_api, name='available_symbols_api'),
    path('predictions/all/', views.all_predictions_api, name='all_predictions_api'),
    
    # DRF router endpoints
    path('', include(router.urls)),
]
