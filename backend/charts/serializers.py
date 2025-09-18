from rest_framework import serializers
from .models import ChartPrediction, Event, Stock, Market
from django.utils import timezone
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

class ChartPredictionSerializer(serializers.ModelSerializer):
    """차트 예측 시리얼라이저"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    
    # Allow frontend to send stock data directly
    stock_symbol = serializers.CharField(write_only=True, required=False)
    reasoning = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    confidence = serializers.IntegerField(min_value=1, max_value=100, required=False)
    
    # Override required fields that will be calculated
    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all(), required=False)
    duration_days = serializers.IntegerField(required=False)
    
    # Override price fields to handle precision properly
    current_price = serializers.DecimalField(max_digits=20, decimal_places=8, required=True)
    predicted_price = serializers.DecimalField(max_digits=20, decimal_places=8, required=True)
    
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
    
    def validate_current_price(self, value):
        """Validate and round current price based on market precision"""
        if value is not None:
            # Convert to Decimal for precision handling
            if isinstance(value, (int, float)):
                value = Decimal(str(value))
            elif isinstance(value, str):
                value = Decimal(value)
            # Round to 8 decimal places max
            return value.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        return value
    
    def validate_predicted_price(self, value):
        """Validate and round predicted price based on market precision"""
        if value is not None:
            # Convert to Decimal for precision handling
            if isinstance(value, (int, float)):
                value = Decimal(str(value))
            elif isinstance(value, str):
                value = Decimal(value)
            # Round to 8 decimal places max
            return value.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        return value
    
    def to_internal_value(self, data):
        """Convert and validate input data before serializer validation"""
        # Handle current_price
        if 'current_price' in data:
            try:
                price = data['current_price']
                if isinstance(price, (int, float)):
                    price = Decimal(str(price))
                elif isinstance(price, str):
                    price = Decimal(price)
                # Round to 8 decimal places to ensure validation passes
                data['current_price'] = price.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
            except (ValueError, TypeError):
                pass  # Let the field validation handle the error
        
        # Handle predicted_price
        if 'predicted_price' in data:
            try:
                price = data['predicted_price']
                if isinstance(price, (int, float)):
                    price = Decimal(str(price))
                elif isinstance(price, str):
                    price = Decimal(price)
                # Round to 8 decimal places to ensure validation passes
                data['predicted_price'] = price.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
            except (ValueError, TypeError):
                pass  # Let the field validation handle the error
        
        return super().to_internal_value(data)
    
    def validate(self, data):
        """Validate that either stock or stock_symbol is provided"""
        if not data.get('stock') and not data.get('stock_symbol'):
            raise serializers.ValidationError("Either 'stock' or 'stock_symbol' must be provided")
        
        if not data.get('target_date'):
            raise serializers.ValidationError("target_date is required")
            
        if not data.get('current_price'):
            raise serializers.ValidationError("current_price is required")
            
        if not data.get('predicted_price'):
            raise serializers.ValidationError("predicted_price is required")
        
        return data
    
    def create(self, validated_data):
        # Handle stock symbol from frontend
        stock_symbol = validated_data.pop('stock_symbol', None)
        reasoning = validated_data.pop('reasoning', '')
        confidence = validated_data.pop('confidence', 75)
        
        if stock_symbol and not validated_data.get('stock'):
            # Get or create a default market for the stock
            from .models import Market
            market, created = Market.objects.get_or_create(
                code='us_stock',
                defaults={
                    'name': 'US Stock Market',
                    'market_type': 'us_stock',
                    'timezone': 'America/New_York'
                }
            )
            
            # Get or create stock
            stock, created = Stock.objects.get_or_create(
                symbol=stock_symbol,
                defaults={
                    'name': stock_symbol,  # Use symbol as name if not found
                    'market': market
                }
            )
            validated_data['stock'] = stock
        
        # Set prediction date to now
        validated_data['prediction_date'] = timezone.now()
        
        # Handle target_date - convert date string to datetime
        if 'target_date' in validated_data:
            target_date = validated_data['target_date']
            if isinstance(target_date, str):
                # Parse date string (YYYY-MM-DD) and convert to datetime
                try:
                    if 'T' in target_date or 'Z' in target_date:
                        # Already ISO format
                        target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                    else:
                        # Date only format (YYYY-MM-DD), add time
                        target_date = datetime.strptime(target_date, '%Y-%m-%d')
                        # Set to end of day in current timezone
                        target_date = target_date.replace(hour=23, minute=59, second=59)
                        target_date = timezone.make_aware(target_date)
                except ValueError as e:
                    raise serializers.ValidationError(f"Invalid date format: {target_date}")
                
                validated_data['target_date'] = target_date
            
            # Calculate duration in days
            current_date = timezone.now()
            duration = (target_date.date() - current_date.date()).days
            validated_data['duration_days'] = max(1, duration)
        
        # Set default user if not authenticated (for testing)
        if not validated_data.get('user'):
            from django.contrib.auth import get_user_model
            import uuid
            User = get_user_model()
            # For anonymous users, create a default user or handle appropriately
            # In production, you should require authentication
            try:
                # Try to get existing anonymous user first
                default_user = User.objects.get(username='anonymous')
            except User.DoesNotExist:
                # Create new anonymous user with unique referral code
                default_user = User.objects.create(
                    username='anonymous',
                    first_name='Anonymous',
                    last_name='User',
                    email='anonymous@example.com',
                    user_type='free',
                    referral_code=str(uuid.uuid4())[:20]  # Generate unique referral code
                )
            validated_data['user'] = default_user
        
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
