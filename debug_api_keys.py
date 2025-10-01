# Debug API Keys Test
# Add this to your market_data/views.py for debugging

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_api_keys(request):
    """Debug endpoint to check API key availability (without exposing actual keys)"""
    if not settings.DEBUG:
        return Response({'error': 'Debug endpoint only available in DEBUG mode'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    from django.conf import settings
    import os
    
    api_keys_status = {
        'django_settings': {
            'ALPHA_VANTAGE_API_KEY': bool(getattr(settings, 'ALPHA_VANTAGE_API_KEY', '')),
            'TWELVE_DATA_API_KEY': bool(getattr(settings, 'TWELVE_DATA_API_KEY', '')),
            'FINNHUB_API_KEY': bool(getattr(settings, 'FINNHUB_API_KEY', '')),
            'POLYGON_API_KEY': bool(getattr(settings, 'POLYGON_API_KEY', '')),
            'TIINGO_API_KEY': bool(getattr(settings, 'TIINGO_API_KEY', '')),
            'MARKETSTACK_API_KEY': bool(getattr(settings, 'MARKETSTACK_API_KEY', '')),
        },
        'environment_variables': {
            'ALPHA_VANTAGE_API_KEY': bool(os.environ.get('ALPHA_VANTAGE_API_KEY', '')),
            'TWELVE_DATA_API_KEY': bool(os.environ.get('TWELVE_DATA_API_KEY', '')),
            'FINNHUB_API_KEY': bool(os.environ.get('FINNHUB_API_KEY', '')),
            'POLYGON_API_KEY': bool(os.environ.get('POLYGON_API_KEY', '')),
            'TIINGO_API_KEY': bool(os.environ.get('TIINGO_API_KEY', '')),
            'MARKETSTACK_API_KEY': bool(os.environ.get('MARKETSTACK_API_KEY', '')),
        }
    }
    
    return Response(api_keys_status, status=status.HTTP_200_OK)