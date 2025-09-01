from django.db import models
from charts.models import Stock

class MarketDataSource(models.Model):
    """시장 데이터 소스"""
    
    SOURCE_CHOICES = [
        ('yahoo', 'Yahoo Finance'),
        ('alpha_vantage', 'Alpha Vantage'),
        ('twelve_data', 'Twelve Data'),
        ('finnhub', 'Finnhub'),
        ('polygon', 'Polygon.io'),
    ]
    
    name = models.CharField('소스명', max_length=100)
    code = models.CharField('소스 코드', max_length=20, choices=SOURCE_CHOICES, unique=True)
    api_key = models.CharField('API 키', max_length=200, blank=True)
    base_url = models.URLField('기본 URL')
    rate_limit_per_minute = models.IntegerField('분당 요청 제한', default=60)
    is_active = models.BooleanField('활성 상태', default=True)
    priority = models.IntegerField('우선순위', default=1)
    
    class Meta:
        verbose_name = '시장 데이터 소스'
        verbose_name_plural = '시장 데이터 소스들'
        ordering = ['priority']
    
    def __str__(self):
        return self.name

class PriceData(models.Model):
    """가격 데이터"""
    
    INTERVAL_CHOICES = [
        ('1m', '1분'),
        ('5m', '5분'),
        ('15m', '15분'),
        ('30m', '30분'),
        ('1h', '1시간'),
        ('4h', '4시간'),
        ('1d', '1일'),
        ('1w', '1주'),
        ('1M', '1월'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name='종목')
    timestamp = models.DateTimeField('시간')
    open_price = models.DecimalField('시가', max_digits=15, decimal_places=8)
    high_price = models.DecimalField('고가', max_digits=15, decimal_places=8)
    low_price = models.DecimalField('저가', max_digits=15, decimal_places=8)
    close_price = models.DecimalField('종가', max_digits=15, decimal_places=8)
    volume = models.BigIntegerField('거래량')
    interval = models.CharField('간격', max_length=5, choices=INTERVAL_CHOICES)
    source = models.ForeignKey(MarketDataSource, on_delete=models.CASCADE, verbose_name='데이터 소스')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '가격 데이터'
        verbose_name_plural = '가격 데이터들'
        unique_together = ['stock', 'timestamp', 'interval', 'source']
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['stock', 'timestamp']),
            models.Index(fields=['stock', 'interval', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.timestamp} - {self.close_price}"

class MarketStatus(models.Model):
    """시장 상태"""
    
    STATUS_CHOICES = [
        ('open', '개장'),
        ('closed', '휴장'),
        ('pre_market', '시간외 거래'),
        ('after_market', '시간외 거래'),
    ]
    
    market = models.ForeignKey('charts.Market', on_delete=models.CASCADE, verbose_name='시장')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES)
    next_open = models.DateTimeField('다음 개장 시간', null=True, blank=True)
    next_close = models.DateTimeField('다음 휴장 시간', null=True, blank=True)
    updated_at = models.DateTimeField('업데이트 시간', auto_now=True)
    
    class Meta:
        verbose_name = '시장 상태'
        verbose_name_plural = '시장 상태들'
    
    def __str__(self):
        return f"{self.market.name} - {self.get_status_display()}"

class NewsData(models.Model):
    """뉴스 데이터"""
    
    SENTIMENT_CHOICES = [
        ('positive', '긍정'),
        ('neutral', '중립'),
        ('negative', '부정'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True, verbose_name='관련 종목')
    title = models.CharField('제목', max_length=500)
    content = models.TextField('내용')
    source = models.CharField('출처', max_length=200)
    author = models.CharField('작성자', max_length=200, blank=True)
    published_at = models.DateTimeField('발행일')
    url = models.URLField('원문 URL')
    sentiment = models.CharField('감정', max_length=20, choices=SENTIMENT_CHOICES, null=True, blank=True)
    sentiment_score = models.DecimalField('감정 점수', max_digits=5, decimal_places=4, null=True, blank=True)
    views_count = models.IntegerField('조회수', default=0)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '뉴스 데이터'
        verbose_name_plural = '뉴스 데이터들'
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title

class TechnicalIndicator(models.Model):
    """기술적 지표"""
    
    INDICATOR_CHOICES = [
        ('sma', '단순이동평균'),
        ('ema', '지수이동평균'),
        ('rsi', 'RSI'),
        ('macd', 'MACD'),
        ('bollinger', '볼린저 밴드'),
        ('stoch', '스토캐스틱'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name='종목')
    indicator_type = models.CharField('지표 유형', max_length=20, choices=INDICATOR_CHOICES)
    timestamp = models.DateTimeField('시간')
    value = models.JSONField('지표 값')
    interval = models.CharField('간격', max_length=5, choices=PriceData.INTERVAL_CHOICES)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '기술적 지표'
        verbose_name_plural = '기술적 지표들'
        unique_together = ['stock', 'indicator_type', 'timestamp', 'interval']
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.get_indicator_type_display()}"

class DataUpdateLog(models.Model):
    """데이터 업데이트 로그"""
    
    UPDATE_TYPE_CHOICES = [
        ('price', '가격 데이터'),
        ('news', '뉴스 데이터'),
        ('indicators', '기술적 지표'),
        ('market_status', '시장 상태'),
    ]
    
    STATUS_CHOICES = [
        ('success', '성공'),
        ('failed', '실패'),
        ('partial', '부분 성공'),
    ]
    
    update_type = models.CharField('업데이트 유형', max_length=20, choices=UPDATE_TYPE_CHOICES)
    source = models.ForeignKey(MarketDataSource, on_delete=models.CASCADE, verbose_name='데이터 소스')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES)
    records_processed = models.IntegerField('처리된 레코드 수', default=0)
    error_message = models.TextField('오류 메시지', blank=True)
    started_at = models.DateTimeField('시작 시간')
    completed_at = models.DateTimeField('완료 시간', null=True, blank=True)
    
    class Meta:
        verbose_name = '데이터 업데이트 로그'
        verbose_name_plural = '데이터 업데이트 로그들'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.get_update_type_display()} - {self.source.name} - {self.status}"
