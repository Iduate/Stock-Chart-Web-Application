from rest_framework import serializers
from .models import ChartPrediction, Event

class ChartPredictionSerializer(serializers.ModelSerializer):
    """차트 예측 시리얼라이저"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ChartPrediction
        fields = [
            'id', 'stock', 'stock_name', 'current_price', 'predicted_price', 
            'prediction_date', 'target_date', 'duration_days',
            'actual_price', 'accuracy_percentage', 'profit_rate', 'status', 
            'status_name', 'is_public', 'views_count', 'likes_count',
            'comments_count', 'created_at', 'updated_at', 'user_name'
        ]
        read_only_fields = ['actual_price', 'accuracy_percentage', 'profit_rate', 'status']

class EventSerializer(serializers.ModelSerializer):
    """이벤트 시리얼라이저"""
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date',
            'prize_description', 'status', 'status_name', 'max_participants',
            'participants_count', 'created_at'
        ]
