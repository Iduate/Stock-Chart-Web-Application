from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .international_views import (
    InternationalPaymentViewSet, ExchangeRateViewSet,
    PaymentStatsView, PaymentWebhookView
)
from .views import MoonPayOnRampInitView, MoonPayOnRampCallbackView, paypal_webhook, MoonPayStatusView, MoonPayAvailabilityView

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
    
    # International payment stats
    path('stats/', PaymentStatsView.as_view(), name='payment-stats'),
    
    # Webhook endpoints
    path('webhook/paypal/', paypal_webhook, name='paypal_webhook'),
    path('webhook/<str:provider>/', PaymentWebhookView.as_view(), name='international-webhook'),

    # Fiat-to-crypto on-ramp (MoonPay)
    path('onramp/moonpay/init/', MoonPayOnRampInitView.as_view({'post': 'create'}), name='moonpay_onramp_init'),
    path('onramp/moonpay/callback/', MoonPayOnRampCallbackView.as_view({'get': 'list'}), name='moonpay_onramp_callback'),
    path('onramp/moonpay/status/', MoonPayStatusView.as_view(), name='moonpay_status'),
    path('onramp/moonpay/available/', MoonPayAvailabilityView.as_view(), name='moonpay_availability'),
]
