from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ChartPrediction, Event
from market_data.models import MarketData
from .serializers import ChartPredictionSerializer, EventSerializer
from market_data.serializers import MarketDataSerializer
from django.db.models import Avg
import random
from datetime import datetime, timedelta

class ChartPredictionViewSet(viewsets.ModelViewSet):
    """차트 예측 뷰셋"""
    serializer_class = ChartPredictionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChartPrediction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create a new prediction and automatically set it to public
        """
        # Save the prediction and automatically set is_public to True
        serializer.save(
            user=self.request.user,
            is_public=True  # Always make predictions public
        )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public_predictions(self, request):
        """
        공개 예측 목록 - 사용자 타입에 따라 접근 제한
        """
        # Check if user can access premium content
        from users.visit_tracker import VisitTracker
        tracker = VisitTracker(request)
        
        if not tracker.can_access_premium():
            return Response({
                'error': 'Free access limit reached',
                'payment_required': True
            }, status=402)  # 402 Payment Required
        
        # If the user is anonymous or a free user, increment their access count
        if not request.user.is_authenticated:
            tracker.increment_visit()
        elif request.user.user_type == 'free':
            request.user.increment_free_access()
        
        # Get public predictions
        predictions = ChartPrediction.objects.filter(is_public=True).order_by('-created_at')
        
        # If user is not paid/admin, limit the number of returned predictions
        if request.user.is_authenticated and request.user.user_type not in ['paid', 'admin']:
            predictions = predictions[:10]  # Limited access for free users
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def rankings(self, request):
        """
        수익률 랭킹 - 사용자 타입에 따라 접근 제한
        """
        # Check if user can access premium content
        from users.visit_tracker import VisitTracker
        tracker = VisitTracker(request)
        
        if not tracker.can_access_premium():
            return Response({
                'error': 'Free access limit reached',
                'payment_required': True
            }, status=402)  # 402 Payment Required
        
        # If the user is anonymous or a free user, increment their access count
        if not request.user.is_authenticated:
            tracker.increment_visit()
        elif request.user.user_type == 'free':
            request.user.increment_free_access()
        
        # Get completed predictions ranked by profit rate
        predictions = ChartPrediction.objects.filter(
            is_public=True,
            status='completed'
        ).order_by('-profit_rate')[:50]
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)

class MarketViewSet(viewsets.ReadOnlyModelViewSet):
    """시장 데이터 뷰셋"""
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    
    @action(detail=False, methods=['get'])
    def realtime(self, request):
        """실시간 시장 데이터"""
        symbol = request.query_params.get('symbol')
        if symbol:
            try:
                market_data = MarketData.objects.filter(symbol=symbol).latest('timestamp')
                serializer = self.get_serializer(market_data)
                return Response(serializer.data)
            except MarketData.DoesNotExist:
                return Response({'error': '심볼을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': '심볼이 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """이벤트 뷰셋"""
    queryset = Event.objects.filter(status='active')
    serializer_class = EventSerializer
    
    @action(detail=True, methods=['post'])
    def participate(self, request, pk=None):
        """이벤트 참여"""
        event = self.get_object()
        if event.status == 'active' and request.user.is_authenticated:
            # 이벤트 참여 로직 구현
            return Response({'message': '이벤트에 참여했습니다'})
        return Response({'error': '이벤트 참여 불가'}, status=status.HTTP_400_BAD_REQUEST)


# 독립적인 API 엔드포인트들

@api_view(['GET'])
@permission_classes([AllowAny])
def get_rankings(request, ranking_type):
    """랭킹 조회 API"""
    try:
        # 샘플 랭킹 데이터 생성 (실제로는 DB에서 조회)
        sample_users = [
            {'username': 'TradingMaster', 'profit_rate': 45.2, 'predictions': 28, 'accuracy': 78.5},
            {'username': 'StockGuru', 'profit_rate': 38.7, 'predictions': 35, 'accuracy': 82.1},
            {'username': 'CryptoKing', 'profit_rate': 33.4, 'predictions': 42, 'accuracy': 75.3},
            {'username': 'MarketPro', 'profit_rate': 29.8, 'predictions': 31, 'accuracy': 80.6},
            {'username': 'InvestorAce', 'profit_rate': 25.1, 'predictions': 26, 'accuracy': 77.8},
            {'username': 'ChartWizard', 'profit_rate': 22.3, 'predictions': 38, 'accuracy': 71.2},
            {'username': 'BullTrader', 'profit_rate': 19.7, 'predictions': 33, 'accuracy': 74.5},
            {'username': 'SmartInvestor', 'profit_rate': 17.2, 'predictions': 29, 'accuracy': 79.3},
            {'username': 'ProfitHunter', 'profit_rate': 15.8, 'predictions': 25, 'accuracy': 76.0},
            {'username': 'MarketNinja', 'profit_rate': 13.5, 'predictions': 31, 'accuracy': 72.4},
        ]
        
        if ranking_type == 'accuracy':
            # 정확도순 정렬
            rankings = sorted(sample_users, key=lambda x: x['accuracy'], reverse=True)
        elif ranking_type == 'profit':
            # 수익률순 정렬 (이미 정렬됨)
            rankings = sample_users
        else:
            # 기본값: 수익률순
            rankings = sample_users
            
        # 순위 추가
        for i, user in enumerate(rankings, 1):
            user['rank'] = i
            
        return Response(rankings, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': '랭킹 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_events(request):
    """이벤트 목록 조회 API"""
    try:
        # 샘플 이벤트 데이터 생성 (실제로는 DB에서 조회)
        sample_events = [
            {
                'id': 1,
                'title': '9월 트레이딩 챌린지',
                'description': '이번 달 가장 높은 수익률을 기록한 사용자에게 100만원 상금을 드립니다!',
                'prize': '상금 100만원',
                'participants': 156,
                'start_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
                'status': 'active'
            },
            {
                'id': 2,
                'title': 'AI 예측 정확도 대회',
                'description': '가장 정확한 주식 예측을 한 사용자를 찾습니다. 정확도 85% 이상 달성시 특별 보상!',
                'prize': '애플워치 울트라',
                'participants': 89,
                'start_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d'),
                'status': 'active'
            },
            {
                'id': 3,
                'title': '신규 회원 환영 이벤트',
                'description': '처음 예측에 참여하는 신규 회원에게 무료 프리미엄 기능 1개월 제공!',
                'prize': '프리미엄 멤버십 1개월',
                'participants': 234,
                'start_date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
                'status': 'active'
            },
            {
                'id': 4,
                'title': '크립토 트레이딩 마스터',
                'description': '암호화폐 예측에서 연속 10회 성공한 사용자에게 특별 보상을 드립니다.',
                'prize': '비트코인 0.01 BTC',
                'participants': 67,
                'start_date': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=40)).strftime('%Y-%m-%d'),
                'status': 'active'
            }
        ]
        
        return Response(sample_events, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': '이벤트 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_charts(request):
    """차트 목록 조회 (심플 엔드포인트)"""
    print(f"DEBUG: get_charts called - User: {request.user}, Authenticated: {request.user.is_authenticated}")
    print(f"DEBUG: TEMPORARY - Returning sample chart data for testing")
    try:
        # 샘플 차트 데이터 반환
        sample_charts = [
            {
                'id': 1,
                'user': {'username': '투자왕'},
                'stock_name': '애플',
                'stock_symbol': 'AAPL',
                'predicted_price': 185.50,
                'current_price': 182.30,
                'target_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'created_at': datetime.now().strftime('%Y-%m-%d'),
                'status': 'pending',
                'profit_rate': 0,
                'accuracy': 85.5
            },
            {
                'id': 2,
                'user': {'username': '애플매니아'},
                'stock_name': '구글',
                'stock_symbol': 'GOOGL',
                'predicted_price': 145.75,
                'current_price': 142.20,
                'target_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
                'created_at': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'status': 'pending',
                'profit_rate': 1.75,
                'accuracy': 92.1
            },
            {
                'id': 3,
                'user': {'username': '테슬라킹'},
                'stock_name': '테슬라',
                'stock_symbol': 'TSLA',
                'predicted_price': 245.00,
                'current_price': 238.80,
                'target_date': (datetime.now() + timedelta(days=21)).strftime('%Y-%m-%d'),
                'created_at': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'status': 'completed',
                'profit_rate': 12.8,
                'accuracy': 94.2
            },
            {
                'id': 4,
                'user': {'username': '구글러'},
                'stock_name': '마이크로소프트',
                'stock_symbol': 'MSFT',
                'predicted_price': 378.90,
                'current_price': 375.20,
                'target_date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
                'created_at': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'status': 'pending',
                'profit_rate': 2.5,
                'accuracy': 88.7
            }
        ]
        
        return Response(sample_charts, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': '차트 조회 중 오류가 발생했습니다'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
