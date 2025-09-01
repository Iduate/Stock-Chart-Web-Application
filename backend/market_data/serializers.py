from rest_framework import serializers
from .models import MarketData, PriceHistory, MarketAlert

class MarketDataSerializer(serializers.ModelSerializer):
    """시장 데이터 시리얼라이저"""
    market_name = serializers.CharField(source='get_market_display', read_only=True)
    
    class Meta:
        model = MarketData
        fields = [
            'id', 'symbol', 'market', 'market_name', 'current_price',
            'open_price', 'high', 'low', 'volume', 'change_percent',
            'market_cap', 'timestamp'
        ]

class PriceHistorySerializer(serializers.ModelSerializer):
    """가격 이력 시리얼라이저"""
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'symbol', 'market', 'price', 'volume', 'timestamp'
        ]

class MarketAlertSerializer(serializers.ModelSerializer):
    """시장 알림 시리얼라이저"""
    alert_type_name = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = MarketAlert
        fields = [
            'id', 'symbol', 'market', 'alert_type', 'alert_type_name',
            'trigger_price', 'current_price', 'message', 'is_triggered',
            'created_at', 'triggered_at'
        ]
