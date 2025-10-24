from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .international_views import (
    InternationalPaymentViewSet, ExchangeRateViewSet,
    PaymentStatsView, PaymentWebhookView
)
from .views import paypal_webhook
from .views import (
    TransakStatusView,
    TransakInitView,
    ChangeNOWStatusView,
    ChangeNOWInitView,
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
    
    # International payment stats
    path('stats/', PaymentStatsView.as_view(), name='payment-stats'),
    
    # Webhook endpoints
    path('webhook/paypal/', paypal_webhook, name='paypal_webhook'),
    path('webhook/<str:provider>/', PaymentWebhookView.as_view(), name='international-webhook'),
    # Transak
    # Transak on-ramp
    path('transak/status/', TransakStatusView.as_view(), name='transak_status'),
    path('transak/init/', TransakInitView.as_view({'post': 'create'}), name='transak_init'),
    # ChangeNOW
    path('changenow/status/', ChangeNOWStatusView.as_view(), name='changenow_status'),
    path('changenow/init/', ChangeNOWInitView.as_view({'post': 'create'}), name='changenow_init'),
]
