from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sources', views.MarketDataSourceViewSet)
router.register(r'prices', views.PriceDataViewSet)
router.register(r'news', views.NewsDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stocks/<int:stock_id>/prices/', views.StockPriceView.as_view(), name='stock_prices'),
    path('stocks/<int:stock_id>/chart/', views.StockChartView.as_view(), name='stock_chart'),
    path('indicators/<int:stock_id>/', views.TechnicalIndicatorView.as_view(), name='indicators'),
    path('market-status/', views.MarketStatusView.as_view(), name='market_status'),
]
