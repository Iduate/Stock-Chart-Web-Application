from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentProviderViewSet,
    PaymentMethodViewSet, 
    PaymentTransactionViewSet,
    PaymentRefundViewSet,
    PaymentCreateView,
    PaymentVerifyView,
    PaymentStatsView,
    payment_webhook
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'providers', PaymentProviderViewSet, basename='provider')
router.register(r'methods', PaymentMethodViewSet, basename='method')
router.register(r'transactions', PaymentTransactionViewSet, basename='transaction')
router.register(r'refunds', PaymentRefundViewSet, basename='refund')

app_name = 'korean_payments'

urlpatterns = [
    # ViewSet URLs
    path('api/', include(router.urls)),
    
    # Custom API URLs
    path('api/payment/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('api/payment/verify/', PaymentVerifyView.as_view(), name='payment-verify'),
    path('api/payment/stats/', PaymentStatsView.as_view(), name='payment-stats'),
    
    # Webhook URLs
    path('webhook/<str:provider_name>/', payment_webhook, name='payment-webhook'),
    
    # Provider specific webhook URLs
    path('webhook/iamport/', payment_webhook, {'provider_name': 'iamport'}, name='iamport-webhook'),
    path('webhook/toss/', payment_webhook, {'provider_name': 'toss'}, name='toss-webhook'),
    path('webhook/kakaopay/', payment_webhook, {'provider_name': 'kakaopay'}, name='kakaopay-webhook'),
    
    # Legacy/Compatibility URLs
    path('payment/create/', PaymentCreateView.as_view(), name='payment-create-legacy'),
    path('payment/verify/', PaymentVerifyView.as_view(), name='payment-verify-legacy'),
]
