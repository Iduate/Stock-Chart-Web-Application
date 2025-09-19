from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'market_data'

urlpatterns = [
    # 실시간 데이터
    path('quote/<str:symbol>/', views.get_real_time_quote, name='real_time_quote'),
    path('historical/<str:symbol>/', views.get_historical_data, name='historical_data'),
    
    # 암호화폐 & 외환
    path('crypto/<str:symbol>/', views.get_crypto_data, name='crypto_data'),
    path('coingecko/<str:symbol>/', views.get_coingecko_data, name='coingecko_data'),
    path('forex/<str:from_symbol>/<str:to_symbol>/', views.get_forex_data, name='forex_data'),
    
    # 시장 정보
    path('indices/', views.get_market_indices, name='market_indices'),
    path('search/', views.search_symbols, name='search_symbols'),
    
    # 인기 종목
    path('popular/stocks/', views.get_popular_stocks, name='popular_stocks'),
    path('popular/cryptos/', views.get_top_cryptos, name='top_cryptos'),
    
    # Market stocks endpoint (for /api/market/stocks/)
    path('stocks/', views.get_popular_stocks, name='market_stocks'),
    
    # 데이터 저장
    path('save/', views.save_market_data, name='save_market_data'),
    
    # 새로운 강화된 API 엔드포인트 (Finnhub & Polygon)
    path('enhanced/<str:symbol>/', views.get_enhanced_data, name='enhanced_data'),
    path('polygon/historical/<str:symbol>/', views.get_polygon_historical, name='polygon_historical'),
    path('finnhub/crypto/<str:symbol>/', views.get_finnhub_crypto, name='finnhub_crypto'),
    
    # Tiingo API 엔드포인트
    path('tiingo/quote/<str:symbol>/', views.get_tiingo_quote, name='tiingo_quote'),
    path('tiingo/historical/<str:symbol>/', views.get_tiingo_historical, name='tiingo_historical'),
    # Simplified Tiingo endpoint for frontend compatibility
    path('tiingo/<str:symbol>/', views.get_tiingo_quote, name='tiingo_simple'),
    
    # Marketstack API 엔드포인트
    path('marketstack/quote/<str:symbol>/', views.get_marketstack_quote, name='marketstack_quote'),
    path('marketstack/historical/<str:symbol>/', views.get_marketstack_historical, name='marketstack_historical'),
    # Simplified Marketstack endpoint for frontend compatibility
    path('marketstack/<str:symbol>/', views.get_marketstack_quote, name='marketstack_simple'),
    path('finnhub/forex/<str:from_currency>/<str:to_currency>/', views.get_finnhub_forex, name='finnhub_forex'),
    path('news/', views.get_market_news, name='market_news'),
    path('company/<str:symbol>/', views.get_company_profile, name='company_profile'),
    
    # 관심 종목 관리
    path('watchlist/', views.get_watchlist, name='get_watchlist'),
    path('watchlist/add/', views.add_to_watchlist, name='add_watchlist'),
    
    # API Health Monitoring
    path('health/', views.get_comprehensive_api_status, name='api_health'),
    path('performance/', views.get_api_performance_metrics, name='api_performance'),
]
