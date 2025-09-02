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
    
    # DRF router endpoints
    path('', include(router.urls)),
]
