from django.contrib import admin
from .models import MarketAlert, MarketData, PriceHistory


@admin.register(MarketAlert)
class MarketAlertAdmin(admin.ModelAdmin):
	list_display = ('id', 'symbol', 'market', 'alert_type', 'trigger_price', 'is_triggered', 'created_at')
	list_filter = ('market', 'alert_type', 'is_triggered', 'created_at')
	search_fields = ('symbol', 'message')


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
	list_display = ('id', 'symbol', 'market', 'current_price', 'timestamp')
	list_filter = ('market', 'timestamp')
	search_fields = ('symbol',)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'symbol', 'market', 'price', 'timestamp')
	list_filter = ('market', 'timestamp')
	search_fields = ('symbol',)
