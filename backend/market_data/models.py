from django.db import models
from django.utils import timezone

class MarketData(models.Model):
    """시장 데이터"""
    
    MARKET_CHOICES = [
        ('crypto', '암호화폐'),
        ('kr_stock', '한국 주식'),
        ('us_stock', '미국 주식'),
        ('jp_stock', '일본 주식'),
        ('in_stock', '인도 주식'),
        ('uk_stock', '영국 주식'),
        ('ca_stock', '캐나다 주식'),
        ('fr_stock', '프랑스 주식'),
        ('de_stock', '독일 주식'),
        ('tw_stock', '대만 주식'),
    ]
    
    symbol = models.CharField('심볼', max_length=20, db_index=True)
    market = models.CharField('시장', max_length=20, choices=MARKET_CHOICES, db_index=True)
    current_price = models.DecimalField('현재 가격', max_digits=15, decimal_places=8)
    open_price = models.DecimalField('시가', max_digits=15, decimal_places=8)
    high = models.DecimalField('고가', max_digits=15, decimal_places=8)
    low = models.DecimalField('저가', max_digits=15, decimal_places=8)
    volume = models.BigIntegerField('거래량', default=0)
    change_percent = models.DecimalField('변화율(%)', max_digits=10, decimal_places=4, default=0)
    market_cap = models.BigIntegerField('시가총액', null=True, blank=True)
    timestamp = models.DateTimeField('타임스탬프', default=timezone.now, db_index=True)
    
    class Meta:
        verbose_name = '시장 데이터'
        verbose_name_plural = '시장 데이터들'
        ordering = ['-timestamp']
        unique_together = ['symbol', 'market', 'timestamp']
    
    def __str__(self):
        return f"{self.symbol} - {self.current_price} ({self.timestamp})"

class PriceHistory(models.Model):
    """가격 이력"""
    
    symbol = models.CharField('심볼', max_length=20, db_index=True)
    market = models.CharField('시장', max_length=20, db_index=True)
    price = models.DecimalField('가격', max_digits=15, decimal_places=8)
    volume = models.BigIntegerField('거래량', default=0)
    timestamp = models.DateTimeField('타임스탬프', db_index=True)
    
    class Meta:
        verbose_name = '가격 이력'
        verbose_name_plural = '가격 이력들'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['symbol', 'market', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.price} ({self.timestamp})"

class MarketAlert(models.Model):
    """시장 알림"""
    
    ALERT_TYPE_CHOICES = [
        ('price_up', '가격 상승'),
        ('price_down', '가격 하락'),
        ('volume_spike', '거래량 급증'),
        ('market_open', '시장 개장'),
        ('market_close', '시장 마감'),
    ]
    
    symbol = models.CharField('심볼', max_length=20)
    market = models.CharField('시장', max_length=20)
    alert_type = models.CharField('알림 유형', max_length=20, choices=ALERT_TYPE_CHOICES)
    trigger_price = models.DecimalField('트리거 가격', max_digits=15, decimal_places=8, null=True, blank=True)
    current_price = models.DecimalField('현재 가격', max_digits=15, decimal_places=8)
    message = models.TextField('메시지')
    is_triggered = models.BooleanField('트리거됨', default=False)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    triggered_at = models.DateTimeField('트리거일', null=True, blank=True)
    
    class Meta:
        verbose_name = '시장 알림'
        verbose_name_plural = '시장 알림들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.symbol} {self.alert_type} 알림"
