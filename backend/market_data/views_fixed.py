from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .services import market_service
from .models import MarketData, PriceHistory
from .serializers import MarketDataSerializer, PriceHistorySerializer
import json
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 없이 접근 허용
def get_real_time_quote(request, symbol):
    """실시간 시세 조회 API"""
    try:
        market = request.GET.get('market', 'us_stock')
        data = market_service.get_real_time_quote(symbol, market)
        
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
        
        data = market_service.get_historical_data(symbol, period, interval, market)
        
        if data:
            return Response({'data': data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'과거 데이터를 찾을 수 없습니다: {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"과거 데이터 조회 오류: {e}")
        return Response(
            {'error': '과거 데이터 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_crypto_data(request, symbol):
    """암호화폐 데이터 조회 API"""
    try:
        vs_currency = request.GET.get('vs_currency', 'USD')
        data = market_service.get_crypto_data(symbol, vs_currency)
        
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
        data = market_service.get_forex_data(from_symbol, to_symbol)
        
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
        data = market_service.get_market_indices()
        
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
        
        data = market_service.search_symbols(query)
        
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
            data = market_service.get_real_time_quote(symbol, 'us_stock')
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
            data = market_service.get_crypto_data(symbol, 'USD')
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
        enhanced_data = market_service.get_enhanced_real_time_data(symbol.upper())
        
        if enhanced_data:
            return Response(enhanced_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': f'강화 데이터를 찾을 수 없습니다: {symbol}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"강화 데이터 조회 오류: {e}")
        return Response(
            {'error': '강화 데이터 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_polygon_historical(request, symbol):
    """Polygon API 과거 데이터"""
    try:
        period = request.GET.get('period', '1Y')
        data = market_service.get_polygon_historical_data(symbol.upper(), period)
        
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
        crypto_data = market_service.get_finnhub_crypto_price(symbol.upper())
        
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
        forex_data = market_service.get_finnhub_forex_rate(from_currency.upper(), to_currency.upper())
        
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
        
        news = market_service.get_market_news(symbol, limit)
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
        profile = market_service.get_company_profile(symbol.upper())
        
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
            quote = market_service.get_real_time_quote(symbol)
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
