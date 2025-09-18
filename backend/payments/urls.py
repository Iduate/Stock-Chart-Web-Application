from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .international_views import (
    InternationalPaymentViewSet, ExchangeRateViewSet,
    PaymentStatsView, PaymentWebhookView
)

router = DefaultRouter()
router.register(r'plans', views.PaymentPlanViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'coupons', views.CouponViewSet)

# International payments router
international_router = DefaultRouter()
international_router.register(r'international', InternationalPaymentViewSet, basename='international-payment')
international_router.register(r'exchange-rates', ExchangeRateViewSet, basename='exchange-rate')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(international_router.urls)),
    
    # Legacy payment endpoints
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('paypal/create/', views.PayPalCreatePaymentView.as_view(), name='paypal_create'),
    path('paypal/execute/', views.PayPalExecutePaymentView.as_view(), name='paypal_execute'),
    path('crypto/create/', views.CryptoPaymentView.as_view(), name='crypto_create'),
    
    # International payment stats
    path('stats/', PaymentStatsView.as_view(), name='payment-stats'),
    
    # Webhook endpoints
    path('webhook/paypal/', views.PayPalWebhookView.as_view(), name='paypal_webhook'),
    path('webhook/crypto/', views.CryptoWebhookView.as_view(), name='crypto_webhook'),
    path('webhook/<str:provider>/', PaymentWebhookView.as_view(), name='international-webhook'),
]
