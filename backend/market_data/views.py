from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .services import get_market_service
from .models import MarketData, PriceHistory, MarketAlert
from .serializers import MarketDataSerializer, PriceHistorySerializer, MarketAlertSerializer
from .precision_handler import PrecisionHandler
import json
import logging
import time
import requests
from django.conf import settings
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_market_alert(request):
    """Create a market price alert.

    Expected JSON body:
    - symbol: str (required)
    - market: str (optional, default 'crypto')
    - alert_type: str (optional, default 'price_up')
    - trigger_price: number/str (required)
    - message: str (optional)
    """
    try:
        data = request.data if hasattr(request, 'data') and request.data else json.loads(request.body or '{}')
        symbol = (data.get('symbol') or '').strip().upper()
        market = (data.get('market') or 'crypto').strip()
        alert_type = (data.get('alert_type') or 'price_up').strip()
        trigger_price = data.get('trigger_price')

        if not symbol or trigger_price is None:
            return Response({'error': 'symbol and trigger_price are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trigger_price_dec = Decimal(str(trigger_price))
        except (InvalidOperation, ValueError, TypeError):
            return Response({'error': 'trigger_price must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

        # For initial creation, default current_price to trigger_price; can be updated by background jobs later
        current_price = trigger_price_dec
        message = data.get('message') or f"{symbol} 가격 알림 {trigger_price_dec} 설정"

        alert = MarketAlert.objects.create(
            symbol=symbol,
            market=market,
            alert_type=alert_type,
            trigger_price=trigger_price_dec,
            current_price=current_price,
            message=message,
            is_triggered=False,
        )

        serializer = MarketAlertSerializer(alert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.exception(f"Failed to create market alert: {e}")
        return Response({'error': '알림 생성 중 오류가 발생했습니다', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_crypto_data(request, symbol):
    """암호화폐 데이터 조회 API - 실제 API 데이터만 사용"""
    try:
        vs_currency = request.GET.get('vs_currency', 'USD')
        logger.info(f"Crypto data requested for {symbol} vs {vs_currency}")
        
        # 메인 서비스에서 데이터 조회 (이미 폴백 시스템 포함)
        data = get_market_service().get_crypto_data(symbol, vs_currency)
        
        if data:
            logger.info(f"Successfully retrieved crypto data for {symbol} from {data.get('source', 'unknown')}")
            return Response(data, status=status.HTTP_200_OK)
        
        # 모든 API가 실패한 경우 명확한 에러 메시지 반환
        logger.error(f"All crypto APIs failed for {symbol}")
        return Response(
            {
                'error': f'암호화폐 데이터를 찾을 수 없습니다: {symbol}',
                'message': 'All available crypto APIs are currently unavailable or the symbol is not supported',
                'symbol': symbol,
                'supported_symbols': ['BTC', 'ETH', 'ADA', 'BNB', 'DOT', 'MATIC', 'SOL', 'LTC', 'XRP', 'DOGE']
            }, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
    except Exception as e:
        logger.error(f"암호화폐 데이터 조회 오류 {symbol}: {e}")
        return Response(
            {
                'error': '암호화폐 데이터 조회 중 오류가 발생했습니다',
                'message': str(e),
                'symbol': symbol
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_coingecko_data(request, symbol):
    """CoinGecko API를 우선 사용하는 데이터 조회"""
    try:
        period = request.GET.get('period', '30')
        vs_currency = request.GET.get('vs_currency', 'usd')
        
        logger.info(f"CoinGecko data requested for {symbol} (period: {period}, currency: {vs_currency})")
        
        # CoinGecko를 주요 소스로 사용
        data = get_market_service().get_coingecko_primary_data(symbol, period, vs_currency)
        
        if data and len(data) > 0:
            logger.info(f"Successfully retrieved {len(data)} CoinGecko data points for {symbol}")
            return Response({
                'data': data,
                'source': 'coingecko',
                'symbol': symbol.upper(),
                'period': period,
                'vs_currency': vs_currency,
                'count': len(data)
            }, status=status.HTTP_200_OK)
        
        # CoinGecko 실패 시 에러 메시지
        logger.warning(f"CoinGecko data not available for {symbol}")
        return Response(
            {
                'error': f'CoinGecko 데이터를 찾을 수 없습니다: {symbol}',
                'message': 'Symbol not supported by CoinGecko or API temporarily unavailable',
                'symbol': symbol,
                'supported_crypto': ['BTC', 'ETH', 'ADA', 'BNB', 'DOT', 'MATIC', 'SOL', 'LTC', 'XRP', 'DOGE'],
                'supported_stocks': ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
            }, 
            status=status.HTTP_404_NOT_FOUND
        )
        
    except Exception as e:
        logger.error(f"CoinGecko 데이터 조회 오류 {symbol}: {e}")
        return Response(
            {
                'error': 'CoinGecko 데이터 조회 중 오류가 발생했습니다',
                'message': str(e),
                'symbol': symbol
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 없이 접근 허용
def get_real_time_quote(request, symbol):
    """실시간 시세 조회 API"""
    try:
        market = request.GET.get('market', 'us_stock')
        data = get_market_service().get_real_time_quote(symbol, market)
        
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'시세 데이터를 찾을 수 없습니다: {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"실시간 시세 조회 오류: {e}")
        return Response(
            {'error': '시세 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_historical_data(request, symbol):
    """과거 데이터 조회 API"""
    try:
        period = request.GET.get('period', '1month')
        interval = request.GET.get('interval', '1day')
        market = request.GET.get('market', 'us_stock')
        
        data = get_market_service().get_historical_data(symbol, period, interval, market)
        
        if data:
            return Response({'data': data}, status=status.HTTP_200_OK)
        else:
            logger.error(f"No data available for {symbol} from any API")
            return Response(
                {'error': f'No data available for {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"과거 데이터 조회 오류: {e}")
        return Response(
            {'error': '데이터 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_crypto_data(request, symbol):
    """암호화폐 데이터 조회 API"""
    try:
        vs_currency = request.GET.get('vs_currency', 'USD')
        data = get_market_service().get_crypto_data(symbol, vs_currency)
        
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'암호화폐 데이터를 찾을 수 없습니다: {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"암호화폐 데이터 조회 오류: {e}")
        return Response(
            {'error': '암호화폐 데이터 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_forex_data(request, from_symbol, to_symbol):
    """외환 데이터 조회 API"""
    try:
        data = get_market_service().get_forex_data(from_symbol, to_symbol)
        
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'외환 데이터를 찾을 수 없습니다: {from_symbol}/{to_symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"외환 데이터 조회 오류: {e}")
        return Response(
            {'error': '외환 데이터 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_market_indices(request):
    """시장 지수 조회 API"""
    try:
        data = get_market_service().get_market_indices()
        
        if data:
            return Response({'indices': data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': '시장 지수 데이터를 찾을 수 없습니다'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"시장 지수 조회 오류: {e}")
        return Response(
            {'error': '시장 지수 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_symbols(request):
    """심볼 검색 API"""
    try:
        query = request.GET.get('q', '')
        if not query:
            return Response(
                {'error': '검색어를 입력해주세요'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = get_market_service().search_symbols(query)
        
        return Response({'results': data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"심볼 검색 오류: {e}")
        return Response(
            {'error': '심볼 검색 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_popular_stocks(request):
    """인기 주식 목록 API"""
    try:
        # 인기 주식 목록 (실제로는 DB에서 조회하거나 별도 로직 구현)
        popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        
        results = []
        for symbol in popular_symbols:
            data = get_market_service().get_real_time_quote(symbol, 'us_stock')
            if data:
                results.append(data)
        
        return Response({'stocks': results}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"인기 주식 조회 오류: {e}")
        return Response(
            {'error': '인기 주식 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_top_cryptos(request):
    """상위 암호화폐 목록 API"""
    try:
        # 상위 암호화폐 목록
        top_cryptos = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'AVAX']
        
        results = []
        for symbol in top_cryptos:
            data = get_market_service().get_crypto_data(symbol, 'USD')
            if data:
                results.append(data)
        
        return Response({'cryptos': results}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"상위 암호화폐 조회 오류: {e}")
        return Response(
            {'error': '상위 암호화폐 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_market_data(request):
    """시장 데이터 저장 API"""
    try:
        serializer = MarketDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"시장 데이터 저장 오류: {e}")
        return Response(
            {'error': '시장 데이터 저장 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 새로운 강화된 API 엔드포인트들 (Finnhub & Polygon)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_enhanced_data(request, symbol):
    """통합 강화 데이터 - 4개 API 활용"""
    try:
        enhanced_data = get_market_service().get_enhanced_real_time_data(symbol.upper())
        
        if enhanced_data:
            return Response(enhanced_data, status=status.HTTP_200_OK)
        else:
            # Provide fallback sample data
            logger.info(f"Enhanced APIs failed for {symbol}, generating sample data")
            sample_data = generate_sample_historical_data(symbol)
            return Response(sample_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"강화 데이터 조회 오류: {e}")
        # Provide fallback sample data on error
        sample_data = generate_sample_historical_data(symbol)
        return Response(sample_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_polygon_historical(request, symbol):
    """Polygon API 과거 데이터"""
    try:
        period = request.GET.get('period', '1Y')
        data = get_market_service().get_polygon_historical_data(symbol.upper(), period)
        
        if data:
            return Response({
                'symbol': symbol,
                'period': period,
                'data': data,
                'source': 'polygon'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'Polygon 과거 데이터를 찾을 수 없습니다: {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Polygon 과거 데이터 조회 오류: {e}")
        return Response(
            {'error': 'Polygon 과거 데이터 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_finnhub_crypto(request, symbol):
    """Finnhub 암호화폐 데이터"""
    try:
        crypto_data = get_market_service().get_finnhub_crypto_price(symbol.upper())
        
        if crypto_data:
            return Response(crypto_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'Finnhub 암호화폐 데이터를 찾을 수 없습니다: {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Finnhub 암호화폐 조회 오류: {e}")
        return Response(
            {'error': 'Finnhub 암호화폐 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_finnhub_forex(request, from_currency, to_currency):
    """Finnhub 외환 환율"""
    try:
        forex_data = get_market_service().get_finnhub_forex_rate(from_currency.upper(), to_currency.upper())
        
        if forex_data:
            return Response(forex_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'Finnhub 외환 환율을 찾을 수 없습니다: {from_currency}/{to_currency}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Finnhub 외환 환율 조회 오류: {e}")
        return Response(
            {'error': 'Finnhub 외환 환율 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_market_news(request):
    """Finnhub 시장 뉴스"""
    try:
        symbol = request.GET.get('symbol', None)
        limit = int(request.GET.get('limit', 10))
        
        news = get_market_service().get_market_news(symbol, limit)
        return Response({
            'symbol': symbol,
            'news': news
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"시장 뉴스 조회 오류: {e}")
        return Response(
            {'error': '시장 뉴스 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_company_profile(request, symbol):
    """Finnhub 회사 프로필"""
    try:
        profile = get_market_service().get_company_profile(symbol.upper())
        
        if profile:
            return Response(profile, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'회사 프로필을 찾을 수 없습니다: {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"회사 프로필 조회 오류: {e}")
        return Response(
            {'error': '회사 프로필 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_watchlist(request):
    """관심 종목 목록"""
    try:
        # 여기서는 간단한 더미 데이터 반환 (실제로는 사용자별 관심 종목)
        watchlist_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        watchlist_data = []
        
        for symbol in watchlist_symbols:
            quote = get_market_service().get_real_time_quote(symbol)
            if quote:
                watchlist_data.append(quote)
        
        return Response({
            'watchlist': watchlist_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"관심 종목 조회 오류: {e}")
        return Response(
            {'error': '관심 종목 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def add_to_watchlist(request):
    """관심 종목 추가"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            symbol = data.get('symbol', '').upper()
            
            if not symbol:
                return Response(
                    {'error': 'Symbol is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 실제로는 사용자별 관심 종목 DB에 저장
            return Response({
                'success': True,
                'message': f'{symbol} added to watchlist'
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"관심 종목 추가 오류: {e}")
        return Response(
            {'error': '관심 종목 추가 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tiingo_quote(request, symbol):
    """Tiingo API를 사용한 실시간 시세 조회"""
    try:
        data = get_market_service()._get_tiingo_quote(symbol)
        
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'Tiingo에서 {symbol} 데이터를 찾을 수 없습니다'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Tiingo 시세 조회 오류: {e}")
        return Response(
            {'error': 'Tiingo 시세 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tiingo_historical(request, symbol):
    """Tiingo API를 사용한 히스토리컬 데이터 조회"""
    try:
        period = request.GET.get('period', '1year')
        
        data = get_market_service()._get_tiingo_historical(symbol, period)
        
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            # Provide fallback sample data
            logger.info(f"Tiingo API failed for {symbol}, generating sample data")
            sample_data = generate_sample_historical_data(symbol)
            return Response(sample_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Tiingo 히스토리컬 데이터 조회 오류: {e}")
        # Provide fallback sample data on error
        sample_data = generate_sample_historical_data(symbol)
        return Response(sample_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_marketstack_quote(request, symbol):
    """Marketstack API를 사용한 실시간 시세 조회"""
    try:
        data = get_market_service()._get_marketstack_quote(symbol)
        
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'Marketstack에서 {symbol} 데이터를 찾을 수 없습니다'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Marketstack 시세 조회 오류: {e}")
        return Response(
            {'error': 'Marketstack 시세 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_marketstack_historical(request, symbol):
    """Marketstack API를 사용한 히스토리컬 데이터 조회"""
    try:
        period = request.GET.get('period', '1year')
        
        data = get_market_service()._get_marketstack_historical(symbol, period)
        
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            # Provide fallback sample data
            logger.info(f"Marketstack API failed for {symbol}, generating sample data")
            sample_data = generate_sample_historical_data(symbol)
            return Response(sample_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Marketstack 히스토리컬 데이터 조회 오류: {e}")
        # Provide fallback sample data on error
        sample_data = generate_sample_historical_data(symbol)
        return Response(sample_data, status=status.HTTP_200_OK)


def generate_sample_historical_data(symbol):
    """Generate sample historical data for chart display when APIs fail"""
    from datetime import datetime, timedelta
    import random
    
    # Base prices for common symbols
    base_prices = {
        'AAPL': 175.0,
        'GOOGL': 140.0,
        'MSFT': 350.0,
        'AMZN': 145.0,
        'TSLA': 250.0,
        'META': 320.0,
        'NVDA': 450.0,
        'BTC': 43000.0,
        'ETH': 2600.0,
    }
    
    base_price = base_prices.get(symbol.upper(), 150.0)
    data = []
    current_date = datetime.now() - timedelta(days=90)  # 3 months of data
    current_price = base_price
    
    for i in range(90):
        # Generate realistic price movement
        daily_change = random.uniform(-0.05, 0.05)  # ±5% daily change
        current_price *= (1 + daily_change)
        current_price = max(current_price, base_price * 0.5)  # Don't go below 50%
        current_price = min(current_price, base_price * 2.0)   # Don't go above 200%
        
        data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'time': current_date.strftime('%Y-%m-%d'),
            'close': float(PrecisionHandler.format_price(current_price, symbol, 'us_stock')),
            'price': float(PrecisionHandler.format_price(current_price, symbol, 'us_stock')),
            'value': float(PrecisionHandler.format_price(current_price, symbol, 'us_stock')),
            'open': float(PrecisionHandler.format_price(current_price * random.uniform(0.99, 1.01), symbol, 'us_stock')),
            'high': float(PrecisionHandler.format_price(current_price * random.uniform(1.0, 1.03), symbol, 'us_stock')),
            'low': float(PrecisionHandler.format_price(current_price * random.uniform(0.97, 1.0), symbol, 'us_stock')),
            'volume': random.randint(1000000, 10000000)
        })
        
        current_date += timedelta(days=1)
    
    return data


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comprehensive_api_status(request):
    """Comprehensive API health check with response times and detailed status"""
    try:
        api_tests = {}
        
        # Test each API with real endpoints
        api_configs = {
            'finnhub': {
                'url': 'https://finnhub.io/api/v1/quote?symbol=AAPL',
                'headers': {'X-Finnhub-Token': getattr(settings, 'FINNHUB_API_KEY', '')},
                'test_symbol': 'AAPL'
            },
            'alpha_vantage': {
                'url': 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL',
                'params': {'apikey': getattr(settings, 'ALPHA_VANTAGE_API_KEY', '')},
                'test_symbol': 'AAPL'
            },
            'twelve_data': {
                'url': 'https://api.twelvedata.com/quote?symbol=AAPL',
                'params': {'apikey': getattr(settings, 'TWELVE_DATA_API_KEY', '')},
                'test_symbol': 'AAPL'
            },
            'coingecko': {
                'url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                'headers': {},
                'test_symbol': 'BTC'
            },
            'tiingo': {
                'url': 'https://api.tiingo.com/tiingo/daily/AAPL/prices',
                'headers': {'Authorization': f'Token {getattr(settings, "TIINGO_API_KEY", "")}'},
                'test_symbol': 'AAPL'
            },
            'marketstack': {
                'url': 'https://api.marketstack.com/v1/eod/latest?symbols=AAPL',
                'params': {'access_key': getattr(settings, 'MARKETSTACK_API_KEY', '')},
                'test_symbol': 'AAPL'
            }
        }
        
        for api_name, config in api_configs.items():
            start_time = time.time()
            try:
                # Test API with timeout
                response = requests.get(
                    config['url'],
                    headers=config.get('headers', {}),
                    params=config.get('params', {}),
                    timeout=10
                )
                response_time = round((time.time() - start_time) * 1000, 2)
                
                api_tests[api_name] = {
                    'status': 'online' if response.status_code == 200 else 'error',
                    'response_time_ms': response_time,
                    'status_code': response.status_code,
                    'has_api_key': bool(config.get('headers', {}).get('X-Finnhub-Token') or 
                                       config.get('headers', {}).get('Authorization') or
                                       config.get('params', {}).get('apikey') or
                                       config.get('params', {}).get('access_key') or
                                       api_name == 'coingecko'),
                    'test_symbol': config['test_symbol'],
                    'last_tested': timezone.now().isoformat()
                }
                
                # Additional error checking for specific response content
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if api_name == 'alpha_vantage' and 'Error Message' in str(data):
                            api_tests[api_name]['status'] = 'api_limit'
                        elif api_name == 'twelve_data' and 'status' in data and data['status'] == 'error':
                            api_tests[api_name]['status'] = 'api_error'
                        elif api_name == 'finnhub' and 'error' in data:
                            api_tests[api_name]['status'] = 'api_error'
                    except:
                        pass
                        
            except requests.exceptions.Timeout:
                api_tests[api_name] = {
                    'status': 'timeout',
                    'response_time_ms': 10000,
                    'error': 'Request timed out after 10 seconds',
                    'has_api_key': bool(config.get('headers', {}) or config.get('params', {})),
                    'test_symbol': config['test_symbol'],
                    'last_tested': timezone.now().isoformat()
                }
            except requests.exceptions.ConnectionError:
                api_tests[api_name] = {
                    'status': 'offline',
                    'response_time_ms': round((time.time() - start_time) * 1000, 2),
                    'error': 'Connection failed',
                    'has_api_key': bool(config.get('headers', {}) or config.get('params', {})),
                    'test_symbol': config['test_symbol'],
                    'last_tested': timezone.now().isoformat()
                }
            except Exception as e:
                api_tests[api_name] = {
                    'status': 'error',
                    'response_time_ms': round((time.time() - start_time) * 1000, 2),
                    'error': str(e),
                    'has_api_key': bool(config.get('headers', {}) or config.get('params', {})),
                    'test_symbol': config['test_symbol'],
                    'last_tested': timezone.now().isoformat()
                }
        
        # Calculate overall health
        online_apis = sum(1 for api in api_tests.values() if api['status'] == 'online')
        total_apis = len(api_tests)
        health_percentage = round((online_apis / total_apis) * 100, 1)
        
        # Average response time for online APIs
        online_response_times = [api['response_time_ms'] for api in api_tests.values() 
                               if api['status'] == 'online']
        avg_response_time = round(sum(online_response_times) / len(online_response_times), 2) if online_response_times else 0
        
        return Response({
            'overall_status': 'healthy' if health_percentage >= 66 else 'degraded' if health_percentage >= 33 else 'critical',
            'health_percentage': health_percentage,
            'online_apis': f"{online_apis}/{total_apis}",
            'average_response_time_ms': avg_response_time,
            'api_details': api_tests,
            'recommendations': _get_api_recommendations(api_tests),
            'last_updated': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return Response({
            'overall_status': 'error',
            'error': 'Health check system error',
            'message': str(e),
            'last_updated': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_api_recommendations(api_tests):
    """Generate recommendations based on API test results"""
    recommendations = []
    
    for api_name, result in api_tests.items():
        if result['status'] == 'offline':
            recommendations.append(f"{api_name}: Check internet connectivity or service status")
        elif result['status'] == 'timeout':
            recommendations.append(f"{api_name}: Experiencing slow response times, consider increasing timeout")
        elif result['status'] == 'api_limit':
            recommendations.append(f"{api_name}: API rate limit reached, implement caching or upgrade plan")
        elif result['status'] == 'error' and not result.get('has_api_key'):
            recommendations.append(f"{api_name}: API key missing or invalid")
        elif result['status'] == 'online' and result.get('response_time_ms', 0) > 5000:
            recommendations.append(f"{api_name}: Slow response time ({result['response_time_ms']}ms)")
    
    if not recommendations:
        recommendations.append("All APIs are functioning normally")
    
    return recommendations


@api_view(['GET'])
@permission_classes([AllowAny])
def get_api_performance_metrics(request):
    """Get API performance metrics and optimization suggestions"""
    try:
        service = get_market_service()
        
        # Test different types of requests
        performance_tests = {
            'stock_quote': _test_stock_quote_performance(),
            'crypto_data': _test_crypto_data_performance(),
            'historical_data': _test_historical_data_performance()
        }
        
        return Response({
            'performance_tests': performance_tests,
            'optimization_suggestions': _get_optimization_suggestions(performance_tests),
            'cache_status': _get_cache_status(),
            'last_updated': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        return Response({
            'error': 'Performance metrics error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _test_stock_quote_performance():
    """Test stock quote API performance"""
    test_symbols = ['AAPL', 'GOOGL', 'MSFT']
    results = {}
    
    for symbol in test_symbols:
        start_time = time.time()
        try:
            service = get_market_service()
            data = service.get_real_time_quote(symbol, 'us_stock')
            response_time = round((time.time() - start_time) * 1000, 2)
            
            results[symbol] = {
                'success': bool(data),
                'response_time_ms': response_time,
                'data_source': data.get('source') if data else None
            }
        except Exception as e:
            results[symbol] = {
                'success': False,
                'response_time_ms': round((time.time() - start_time) * 1000, 2),
                'error': str(e)
            }
    
    return results


def _test_crypto_data_performance():
    """Test crypto data API performance"""
    test_symbols = ['BTC', 'ETH']
    results = {}
    
    for symbol in test_symbols:
        start_time = time.time()
        try:
            service = get_market_service()
            data = service.get_coingecko_primary_data(symbol, '7', 'usd')
            response_time = round((time.time() - start_time) * 1000, 2)
            
            results[symbol] = {
                'success': bool(data and len(data) > 0),
                'response_time_ms': response_time,
                'data_points': len(data) if data else 0
            }
        except Exception as e:
            results[symbol] = {
                'success': False,
                'response_time_ms': round((time.time() - start_time) * 1000, 2),
                'error': str(e)
            }
    
    return results


def _test_historical_data_performance():
    """Test historical data API performance"""
    start_time = time.time()
    try:
        service = get_market_service()
        data = service.get_historical_data('AAPL', '1month', '1day', 'us_stock')
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'success': bool(data and len(data) > 0),
            'response_time_ms': response_time,
            'data_points': len(data) if data else 0,
            'symbol': 'AAPL'
        }
    except Exception as e:
        return {
            'success': False,
            'response_time_ms': round((time.time() - start_time) * 1000, 2),
            'error': str(e),
            'symbol': 'AAPL'
        }


def _get_optimization_suggestions(performance_tests):
    """Generate optimization suggestions based on performance tests"""
    suggestions = []
    
    # Check stock quote performance
    stock_times = [result.get('response_time_ms', 0) for result in performance_tests.get('stock_quote', {}).values()]
    if stock_times and max(stock_times) > 3000:
        suggestions.append("Stock quote APIs are slow - consider implementing caching")
    
    # Check crypto performance
    crypto_test = performance_tests.get('crypto_data', {})
    if any(not result.get('success', False) for result in crypto_test.values()):
        suggestions.append("Crypto APIs experiencing issues - implement fallback strategies")
    
    # Check historical data
    historical_test = performance_tests.get('historical_data', {})
    if historical_test.get('response_time_ms', 0) > 5000:
        suggestions.append("Historical data queries are slow - implement background processing")
    
    if not suggestions:
        suggestions.append("All APIs are performing well")
    
    return suggestions


def _get_cache_status():
    """Get cache performance status"""
    try:
        # Test cache performance
        start_time = time.time()
        cache.set('test_key', 'test_value', 60)
        cached_value = cache.get('test_key')
        cache_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'cache_working': cached_value == 'test_value',
            'cache_response_time_ms': cache_time,
            'cache_backend': str(cache.__class__.__name__)
        }
    except Exception as e:
        return {
            'cache_working': False,
            'error': str(e),
            'cache_backend': 'unknown'
        }
