from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChartPrediction, Event
from market_data.models import MarketData
from .serializers import ChartPredictionSerializer, EventSerializer
from market_data.serializers import MarketDataSerializer

class ChartPredictionViewSet(viewsets.ModelViewSet):
    """차트 예측 뷰셋"""
    serializer_class = ChartPredictionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChartPrediction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def public_predictions(self, request):
        """공개 예측 목록"""
        predictions = ChartPrediction.objects.filter(is_public=True).order_by('-created_at')
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def rankings(self, request):
        """수익률 랭킹"""
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
