from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ChartPrediction, Event, Stock, Market
from market_data.models import MarketData
from .serializers import ChartPredictionSerializer, EventSerializer
from market_data.serializers import MarketDataSerializer
from .prediction_engine import StockPredictionEngine
from django.db.models import Avg
import random
from datetime import datetime, timedelta
from decimal import Decimal

# 독립적인 API 뷰들 (ViewSet 외부)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_ai_prediction_api(request):
    """
    AI 기반 주식 예측 생성 (독립적인 API 뷰)
    """
    try:
        # 요청 데이터 검증
        symbol = request.data.get('symbol', '').upper()
        market_type = request.data.get('market', 'us_stock')
        prediction_days = int(request.data.get('prediction_days', 7))
        
        if not symbol:
            return Response(
                {'error': '심볼을 입력해주세요.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 예측 기간 제한 (1~30일)
        if not 1 <= prediction_days <= 30:
            return Response(
                {'error': '예측 기간은 1일에서 30일 사이여야 합니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Stock 객체 찾기 또는 생성
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            # 시장 객체 찾기 또는 생성
            market, created = Market.objects.get_or_create(
                code=market_type,
                defaults={
                    'name': f'{market_type.upper()} Market',
                    'market_type': market_type
                }
            )
            
            # 새로운 Stock 객체 생성
            stock = Stock.objects.create(
                symbol=symbol,
                name=f'{symbol} Stock',
                market=market
            )
        
        # AI 예측 엔진 초기화 및 예측 수행
        prediction_engine = StockPredictionEngine()
        prediction_result = prediction_engine.predict_price(
            symbol=symbol,
            market=market_type,
            prediction_days=prediction_days
        )
        
        # 예측 결과 저장 (익명 사용자도 허용)
        chart_prediction = ChartPrediction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            stock=stock,
            current_price=Decimal(str(prediction_result['current_price'])),
            predicted_price=Decimal(str(prediction_result['predicted_price'])),
            prediction_date=datetime.now(),
            target_date=datetime.fromisoformat(prediction_result['target_date'].replace('Z', '+00:00')),
            duration_days=prediction_days,
            status='pending',
            is_public=True
        )
        
        # 응답 데이터 구성
        response_data = {
            'prediction_id': chart_prediction.id,
            'symbol': symbol,
            'market': market_type,
            'current_price': float(prediction_result['current_price']),
            'predicted_price': float(prediction_result['predicted_price']),
            'price_change': prediction_result['price_change'],
            'price_change_percent': prediction_result['price_change_percent'],
            'prediction_days': prediction_days,
            'target_date': prediction_result['target_date'],
            'confidence_score': prediction_result['confidence_score'],
            'risk_level': prediction_result['risk_level'],
            'algorithms_used': prediction_result['algorithms_used'],
            'created_at': chart_prediction.created_at.isoformat()
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': f'입력값 오류: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'예측 생성 중 오류가 발생했습니다: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def available_symbols_api(request):
    """
    예측 가능한 심볼 목록 반환 (독립적인 API 뷰)
    """
    symbols = {
        'crypto': [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'market': 'crypto'},
            {'symbol': 'ETH', 'name': 'Ethereum', 'market': 'crypto'},
            {'symbol': 'ADA', 'name': 'Cardano', 'market': 'crypto'},
            {'symbol': 'DOT', 'name': 'Polkadot', 'market': 'crypto'},
            {'symbol': 'MATIC', 'name': 'Polygon', 'market': 'crypto'},
            {'symbol': 'SOL', 'name': 'Solana', 'market': 'crypto'},
            {'symbol': 'AVAX', 'name': 'Avalanche', 'market': 'crypto'},
            {'symbol': 'LINK', 'name': 'Chainlink', 'market': 'crypto'},
        ],
        'us_stock': [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'market': 'us_stock'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'market': 'us_stock'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'market': 'us_stock'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'market': 'us_stock'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'market': 'us_stock'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'market': 'us_stock'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'market': 'us_stock'},
            {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'market': 'us_stock'},
        ],
        'kr_stock': [
            {'symbol': '005930', 'name': '삼성전자', 'market': 'kr_stock'},
            {'symbol': '000660', 'name': 'SK하이닉스', 'market': 'kr_stock'},
            {'symbol': '035420', 'name': 'NAVER', 'market': 'kr_stock'},
            {'symbol': '005380', 'name': '현대차', 'market': 'kr_stock'},
            {'symbol': '207940', 'name': '삼성바이오로직스', 'market': 'kr_stock'},
            {'symbol': '006400', 'name': '삼성SDI', 'market': 'kr_stock'},
        ]
    }
    
    return Response(symbols, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def all_predictions_api(request):
    """
    모든 공개 예측 목록 반환 (독립적인 API 뷰)
    """
    try:
        # 모든 공개 예측 가져오기 (최신순)
        predictions = ChartPrediction.objects.filter(
            is_public=True
        ).select_related('stock', 'user').order_by('-created_at')
        
        # 예측 데이터 직렬화
        predictions_data = []
        for prediction in predictions:
            # 사용자 정보 (익명 처리)
            user_info = {
                'username': prediction.user.username if prediction.user else 'Anonymous',
                'is_authenticated': prediction.user is not None
            }
            
            # 예측 상태 계산
            from django.utils import timezone
            current_date = timezone.now()
            is_completed = current_date >= prediction.target_date
            
            prediction_data = {
                'id': prediction.id,
                'symbol': prediction.stock.symbol,
                'stock_name': prediction.stock.name,
                'market_type': prediction.stock.market.market_type if prediction.stock.market else 'unknown',
                'current_price': float(prediction.current_price),
                'predicted_price': float(prediction.predicted_price),
                'prediction_date': prediction.prediction_date.isoformat(),
                'target_date': prediction.target_date.isoformat(),
                'duration_days': prediction.duration_days,
                'status': prediction.status,
                'is_completed': is_completed,
                'user': user_info,
                'created_at': prediction.created_at.isoformat(),
                'views_count': prediction.views_count,
                'likes_count': prediction.likes_count,
                'comments_count': prediction.comments_count,
            }
            
            # 실제 가격과 정확도 (완료된 경우)
            if prediction.actual_price:
                prediction_data['actual_price'] = float(prediction.actual_price)
            if prediction.accuracy_percentage:
                prediction_data['accuracy_percentage'] = float(prediction.accuracy_percentage)
            if prediction.profit_rate:
                prediction_data['profit_rate'] = float(prediction.profit_rate)
                
            predictions_data.append(prediction_data)
        
        return Response({
            'predictions': predictions_data,
            'total_count': len(predictions_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'예측 목록을 가져오는 중 오류가 발생했습니다: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ChartPredictionViewSet(viewsets.ModelViewSet):
    """차트 예측 뷰셋"""
    serializer_class = ChartPredictionSerializer
    permission_classes = [AllowAny]  # Temporarily allow all for testing
    
    def get_permissions(self):
        """
        특정 액션에 대해 다른 권한 설정
        """
        if self.action in ['create_ai_prediction', 'available_symbols', 'create', 'list']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [AllowAny]  # Temporarily allow all
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ChartPrediction.objects.filter(user=self.request.user)
        else:
            return ChartPrediction.objects.filter(user__isnull=True)
    
    def perform_create(self, serializer):
        """
        Create a new prediction and automatically set it to public
        """
        # Save the prediction and automatically set is_public to True
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            user=user,
            is_public=True  # Always make predictions public
        )
    
    def create(self, request, *args, **kwargs):
        """
        Override create method to provide better error handling
        """
        try:
            print(f"DEBUG: Creating prediction with data: {request.data}")
            
            # Validate required fields
            required_fields = ['stock_symbol', 'current_price', 'predicted_price', 'target_date']
            missing_fields = [field for field in required_fields if not request.data.get(field)]
            
            if missing_fields:
                return Response(
                    {'error': f'Missing required fields: {", ".join(missing_fields)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                print(f"DEBUG: Prediction created successfully: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                print(f"DEBUG: Serializer validation errors: {serializer.errors}")
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            print(f"DEBUG: Exception in create method: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def create_ai_prediction(self, request):
        """
        AI 기반 주식 예측 생성
        """
        try:
            # 요청 데이터 검증
            symbol = request.data.get('symbol', '').upper()
            market_type = request.data.get('market', 'us_stock')
            prediction_days = int(request.data.get('prediction_days', 7))
            
            if not symbol:
                return Response(
                    {'error': '심볼을 입력해주세요.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 예측 기간 제한 (1~30일)
            if prediction_days < 1 or prediction_days > 30:
                return Response(
                    {'error': '예측 기간은 1일~30일 사이여야 합니다.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 시장과 종목 정보 조회 또는 생성
            market, created = Market.objects.get_or_create(
                market_type=market_type,
                defaults={
                    'name': market_type.replace('_', ' ').title(),
                    'code': market_type.upper()
                }
            )
            
            stock, created = Stock.objects.get_or_create(
                symbol=symbol,
                market=market,
                defaults={
                    'name': symbol,  # 기본값, 나중에 API로 실제 이름 조회 가능
                    'description': f'{symbol} stock/crypto'
                }
            )
            
            # AI 예측 엔진 실행
            prediction_engine = StockPredictionEngine()
            prediction_result = prediction_engine.predict_price(
                symbol=symbol,
                market=market_type,
                prediction_days=prediction_days
            )
            
            # 예측 결과 저장 (익명 사용자도 허용)
            chart_prediction = ChartPrediction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                stock=stock,
                current_price=Decimal(str(prediction_result['current_price'])),
                predicted_price=Decimal(str(prediction_result['predicted_price'])),
                prediction_date=datetime.now(),
                target_date=datetime.fromisoformat(prediction_result['target_date'].replace('Z', '+00:00')),
                duration_days=prediction_days,
                status='pending',
                is_public=True
            )
            
            # 응답 데이터 구성
            response_data = {
                'prediction_id': chart_prediction.id,
                'symbol': symbol,
                'market': market_type,
                'current_price': float(prediction_result['current_price']),
                'predicted_price': float(prediction_result['predicted_price']),
                'price_change': prediction_result['price_change'],
                'price_change_percent': prediction_result['price_change_percent'],
                'prediction_days': prediction_days,
                'target_date': prediction_result['target_date'],
                'confidence_score': prediction_result['confidence_score'],
                'risk_level': prediction_result['risk_level'],
                'algorithms_used': prediction_result['algorithms_used'],
                'created_at': chart_prediction.created_at.isoformat()
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': f'입력값 오류: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'예측 생성 중 오류가 발생했습니다: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def available_symbols(self, request):
        """
        예측 가능한 심볼 목록 반환
        """
        symbols = {
            'crypto': [
                {'symbol': 'BTC', 'name': 'Bitcoin', 'market': 'crypto'},
                {'symbol': 'ETH', 'name': 'Ethereum', 'market': 'crypto'},
                {'symbol': 'ADA', 'name': 'Cardano', 'market': 'crypto'},
                {'symbol': 'DOT', 'name': 'Polkadot', 'market': 'crypto'},
                {'symbol': 'MATIC', 'name': 'Polygon', 'market': 'crypto'},
                {'symbol': 'SOL', 'name': 'Solana', 'market': 'crypto'},
                {'symbol': 'AVAX', 'name': 'Avalanche', 'market': 'crypto'},
                {'symbol': 'LINK', 'name': 'Chainlink', 'market': 'crypto'},
                {'symbol': 'UNI', 'name': 'Uniswap', 'market': 'crypto'},
                {'symbol': 'DOGE', 'name': 'Dogecoin', 'market': 'crypto'},
            ],
            'us_stock': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'market': 'us_stock'},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'market': 'us_stock'},
                {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'market': 'us_stock'},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'market': 'us_stock'},
                {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'market': 'us_stock'},
                {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'market': 'us_stock'},
                {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'market': 'us_stock'},
                {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'market': 'us_stock'},
                {'symbol': 'AMD', 'name': 'Advanced Micro Devices', 'market': 'us_stock'},
                {'symbol': 'INTC', 'name': 'Intel Corporation', 'market': 'us_stock'},
            ],
            'kr_stock': [
                {'symbol': '005930', 'name': '삼성전자', 'market': 'kr_stock'},
                {'symbol': '000660', 'name': 'SK하이닉스', 'market': 'kr_stock'},
                {'symbol': '035420', 'name': 'NAVER', 'market': 'kr_stock'},
                {'symbol': '005490', 'name': 'POSCO홀딩스', 'market': 'kr_stock'},
                {'symbol': '051910', 'name': 'LG화학', 'market': 'kr_stock'},
            ]
        }
        
        return Response(symbols, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def precision_info(self, request):
        """
        심볼과 시장별 정밀도 정보 반환
        """
        from market_data.precision_handler import PrecisionHandler
        
        symbol = request.query_params.get('symbol', '').upper()
        market = request.query_params.get('market', 'us_stock')
        
        precision_info = PrecisionHandler.get_display_precision(symbol, market)
        
        return Response(precision_info, status=status.HTTP_200_OK)

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
