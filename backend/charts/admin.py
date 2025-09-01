from django.contrib import admin
from .models import Market, Stock, ChartPrediction, ChartLike, ChartComment, Event, EventParticipation

# 관리자 사이트 헤더 변경
admin.site.site_header = "스톡차트 관리자 패널"
admin.site.site_title = "스톡차트 관리"
admin.site.index_title = "관리자 대시보드"

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    """시장 관리자"""
    
    list_display = ('name', 'code', 'market_type', 'timezone', 'is_active')
    list_filter = ('market_type', 'is_active')
    search_fields = ('name', 'code')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """종목 관리자"""
    
    list_display = ('name', 'symbol', 'market', 'is_active', 'created_at')
    list_filter = ('market', 'is_active', 'created_at')
    search_fields = ('name', 'symbol')

@admin.register(ChartPrediction)
class ChartPredictionAdmin(admin.ModelAdmin):
    """차트 예측 관리자"""
    
    list_display = ('user', 'stock', 'predicted_price', 'target_date', 'status', 'accuracy_percentage', 'profit_rate')
    list_filter = ('status', 'is_public', 'stock__market', 'created_at')
    search_fields = ('user__username', 'stock__name', 'stock__symbol')
    date_hierarchy = 'created_at'
    readonly_fields = ('accuracy_percentage', 'profit_rate', 'views_count', 'likes_count', 'comments_count')

@admin.register(ChartLike)
class ChartLikeAdmin(admin.ModelAdmin):
    """차트 좋아요 관리자"""
    
    list_display = ('user', 'prediction', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'prediction__stock__name')

@admin.register(ChartComment)
class ChartCommentAdmin(admin.ModelAdmin):
    """차트 댓글 관리자"""
    
    list_display = ('user', 'prediction', 'content_preview', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('user__username', 'content', 'prediction__stock__name')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '내용 미리보기'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """이벤트 관리자"""
    
    list_display = ('title', 'status', 'start_date', 'end_date', 'participants_count', 'max_participants')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    """이벤트 참가 관리자"""
    
    list_display = ('user', 'event', 'prediction', 'rank', 'prize_won', 'created_at')
    list_filter = ('event', 'rank', 'created_at')
    search_fields = ('user__username', 'event__title')
