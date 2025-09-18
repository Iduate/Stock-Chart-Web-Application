from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'partners', views.AffiliatePartnerViewSet, basename='affiliate-partners')
router.register(r'links', views.ReferralLinkViewSet, basename='referral-links')
router.register(r'commissions', views.CommissionTransactionViewSet, basename='commission-transactions')
router.register(r'materials', views.PartnerMaterialViewSet, basename='partner-materials')

urlpatterns = [
    path('', include(router.urls)),
    path('track/', views.ReferralTrackingView.as_view(), name='referral-tracking'),
]
