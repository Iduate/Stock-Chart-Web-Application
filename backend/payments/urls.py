from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.PaymentPlanViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'coupons', views.CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('paypal/create/', views.PayPalCreatePaymentView.as_view(), name='paypal_create'),
    path('paypal/execute/', views.PayPalExecutePaymentView.as_view(), name='paypal_execute'),
    path('crypto/create/', views.CryptoPaymentView.as_view(), name='crypto_create'),
    path('webhook/paypal/', views.PayPalWebhookView.as_view(), name='paypal_webhook'),
    path('webhook/crypto/', views.CryptoWebhookView.as_view(), name='crypto_webhook'),
]
