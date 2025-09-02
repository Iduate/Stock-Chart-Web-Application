from rest_framework import serializers
from .models import MarketData, PriceHistory
from decimal import Decimal


class MarketDataSerializer(serializers.ModelSerializer):
    """시장 데이터 시리얼라이저"""
    
    change_amount = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()
    formatted_volume = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketData
        fields = [
            'id', 'symbol', 'market', 'current_price', 'open_price',
            'high', 'low', 'volume', 'change_percent', 'market_cap',
            'timestamp', 'change_amount', 'formatted_price', 'formatted_volume'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_change_amount(self, obj):
        """가격 변화량 계산"""
        if obj.current_price and obj.open_price:
            change = obj.current_price - obj.open_price
            return float(change)
        return 0
    
    def get_formatted_price(self, obj):
        """가격 포맷팅"""
        if obj.current_price:
            if obj.current_price >= 1:
                return f"${obj.current_price:,.2f}"
            else:
                return f"${obj.current_price:.6f}"
        return "$0.00"
    
    def get_formatted_volume(self, obj):
        """거래량 포맷팅"""
        if obj.volume:
            if obj.volume >= 1_000_000_000:
                return f"{obj.volume / 1_000_000_000:.1f}B"
            elif obj.volume >= 1_000_000:
                return f"{obj.volume / 1_000_000:.1f}M"
            elif obj.volume >= 1_000:
                return f"{obj.volume / 1_000:.1f}K"
            else:
                return str(obj.volume)
        return "0"


class PriceHistorySerializer(serializers.ModelSerializer):
    """가격 이력 시리얼라이저"""
    
    formatted_timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'symbol', 'market', 'price', 'volume', 
            'timestamp', 'formatted_timestamp'
        ]
        read_only_fields = ['id']
    
    def get_formatted_timestamp(self, obj):
        """타임스탬프 포맷팅"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')


class RealTimeQuoteSerializer(serializers.Serializer):
    """실시간 시세 응답 시리얼라이저"""
    
    symbol = serializers.CharField(max_length=20)
    current_price = serializers.DecimalField(max_digits=15, decimal_places=8)
    open_price = serializers.DecimalField(max_digits=15, decimal_places=8)
    high = serializers.DecimalField(max_digits=15, decimal_places=8)
    low = serializers.DecimalField(max_digits=15, decimal_places=8)
    volume = serializers.IntegerField()
    change_percent = serializers.DecimalField(max_digits=10, decimal_places=4)
    market = serializers.CharField(max_length=20)
    timestamp = serializers.DateTimeField()


class HistoricalDataSerializer(serializers.Serializer):
    """과거 데이터 응답 시리얼라이저"""
    
    timestamp = serializers.CharField()
    open = serializers.DecimalField(max_digits=15, decimal_places=8)
    high = serializers.DecimalField(max_digits=15, decimal_places=8)
    low = serializers.DecimalField(max_digits=15, decimal_places=8)
    close = serializers.DecimalField(max_digits=15, decimal_places=8)
    volume = serializers.IntegerField()


class CryptoDataSerializer(serializers.Serializer):
    """암호화폐 데이터 시리얼라이저"""
    
    symbol = serializers.CharField(max_length=20)
    current_price = serializers.DecimalField(max_digits=15, decimal_places=8)
    open_price = serializers.DecimalField(max_digits=15, decimal_places=8)
    high = serializers.DecimalField(max_digits=15, decimal_places=8)
    low = serializers.DecimalField(max_digits=15, decimal_places=8)
    volume = serializers.IntegerField()
    change_percent = serializers.DecimalField(max_digits=10, decimal_places=4)
    market = serializers.CharField(max_length=20)
    timestamp = serializers.DateTimeField()


class ForexDataSerializer(serializers.Serializer):
    """외환 데이터 시리얼라이저"""
    
    from_symbol = serializers.CharField(max_length=10)
    to_symbol = serializers.CharField(max_length=10)
    exchange_rate = serializers.DecimalField(max_digits=15, decimal_places=8)
    last_refreshed = serializers.CharField()
    timestamp = serializers.DateTimeField()


class SymbolSearchSerializer(serializers.Serializer):
    """심볼 검색 결과 시리얼라이저"""
    
    symbol = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=50)
    region = serializers.CharField(max_length=50)
    market_open = serializers.CharField(max_length=20)
    market_close = serializers.CharField(max_length=20)
    timezone = serializers.CharField(max_length=50)
    currency = serializers.CharField(max_length=10)
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
