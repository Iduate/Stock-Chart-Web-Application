from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'predictions', views.ChartPredictionViewSet, basename='chartprediction')
router.register(r'markets', views.MarketViewSet)
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
