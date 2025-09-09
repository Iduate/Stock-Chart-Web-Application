from rest_framework import serializers
from .models import ChartPrediction, Event, Stock, Market
from django.utils import timezone
from datetime import datetime

class ChartPredictionSerializer(serializers.ModelSerializer):
    """차트 예측 시리얼라이저"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    
    # Allow frontend to send stock data directly
    stock_symbol = serializers.CharField(write_only=True, required=False)
    reasoning = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    confidence = serializers.IntegerField(min_value=1, max_value=100, required=False)
    
    class Meta:
        model = ChartPrediction
        fields = [
            'id', 'stock', 'stock_name', 'stock_symbol', 'current_price', 'predicted_price', 
            'prediction_date', 'target_date', 'duration_days', 'reasoning', 'confidence',
            'actual_price', 'accuracy_percentage', 'profit_rate', 'status', 
            'status_name', 'is_public', 'views_count', 'likes_count',
            'comments_count', 'created_at', 'updated_at', 'user_name'
        ]
        read_only_fields = ['actual_price', 'accuracy_percentage', 'profit_rate', 'status', 'prediction_date']
    
    def create(self, validated_data):
        # Handle stock symbol from frontend
        stock_symbol = validated_data.pop('stock_symbol', None)
        reasoning = validated_data.pop('reasoning', '')
        confidence = validated_data.pop('confidence', 75)
        
        if stock_symbol:
            # Get or create stock
            stock, created = Stock.objects.get_or_create(
                symbol=stock_symbol,
                defaults={
                    'name': stock_symbol,  # Use symbol as name if not found
                    'market_id': 1  # Default to first market, update this logic as needed
                }
            )
            validated_data['stock'] = stock
        
        # Set prediction date to now
        validated_data['prediction_date'] = timezone.now()
        
        # Calculate duration in days if target_date is provided
        if 'target_date' in validated_data:
            target_date = validated_data['target_date']
            if isinstance(target_date, str):
                target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
            
            duration = (target_date.date() - timezone.now().date()).days
            validated_data['duration_days'] = max(1, duration)
        
        prediction = super().create(validated_data)
        
        # Store additional metadata (reasoning, confidence) if needed
        # You could add fields to the model or use a related metadata model
        
        return prediction

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
