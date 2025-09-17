from django.db import models
from django.conf import settings
from django.utils import timezone

class Market(models.Model):
    """시장 정보"""
    
    MARKET_TYPE_CHOICES = [
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
    
    name = models.CharField('시장명', max_length=100)
    code = models.CharField('시장 코드', max_length=20, unique=True)
    market_type = models.CharField('시장 유형', max_length=20, choices=MARKET_TYPE_CHOICES)
    timezone = models.CharField('시간대', max_length=50, default='Asia/Seoul')
    is_active = models.BooleanField('활성 상태', default=True)
    
    class Meta:
        verbose_name = '시장'
        verbose_name_plural = '시장들'
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Stock(models.Model):
    """주식/암호화폐 정보"""
    
    symbol = models.CharField('심볼', max_length=20)
    name = models.CharField('이름', max_length=200)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, verbose_name='시장')
    description = models.TextField('설명', blank=True)
    logo_url = models.URLField('로고 URL', blank=True)
    is_active = models.BooleanField('활성 상태', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '종목'
        verbose_name_plural = '종목들'
        unique_together = ['symbol', 'market']
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"

class ChartPrediction(models.Model):
    """차트 예측"""
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('completed', '완료'),
        ('cancelled', '취소됨'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자', null=True, blank=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name='종목')
    current_price = models.DecimalField('현재 가격', max_digits=15, decimal_places=2)
    predicted_price = models.DecimalField('예측 가격', max_digits=15, decimal_places=2)
    prediction_date = models.DateTimeField('예측일')
    target_date = models.DateTimeField('목표일')
    duration_days = models.IntegerField('예측 기간(일)')
    actual_price = models.DecimalField('실제 가격', max_digits=15, decimal_places=2, null=True, blank=True)
    accuracy_percentage = models.DecimalField('정확도(%)', max_digits=5, decimal_places=2, null=True, blank=True)
    profit_rate = models.DecimalField('수익률(%)', max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    is_public = models.BooleanField('공개 여부', default=True)
    views_count = models.IntegerField('조회수', default=0)
    likes_count = models.IntegerField('좋아요수', default=0)
    comments_count = models.IntegerField('댓글수', default=0)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '차트 예측'
        verbose_name_plural = '차트 예측들'
        ordering = ['-created_at']
    
    def __str__(self):
        username = self.user.username if self.user else 'Anonymous'
        return f"{username} - {self.stock.name} 예측"
    
    def calculate_accuracy(self):
        """정확도 계산"""
        if self.actual_price and self.predicted_price:
            error = abs(self.actual_price - self.predicted_price)
            accuracy = max(0, 100 - (error / self.actual_price * 100))
            self.accuracy_percentage = round(accuracy, 2)
            self.save()
            return self.accuracy_percentage
        return None
    
    def calculate_profit_rate(self):
        """수익률 계산"""
        if self.actual_price and self.current_price:
            profit = ((self.actual_price - self.current_price) / self.current_price) * 100
            self.profit_rate = round(profit, 2)
            self.save()
            return self.profit_rate
        return None

class ChartLike(models.Model):
    """차트 좋아요"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    prediction = models.ForeignKey(ChartPrediction, on_delete=models.CASCADE, verbose_name='예측')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '차트 좋아요'
        verbose_name_plural = '차트 좋아요들'
        unique_together = ['user', 'prediction']

class ChartComment(models.Model):
    """차트 댓글"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    prediction = models.ForeignKey(ChartPrediction, on_delete=models.CASCADE, verbose_name='예측')
    content = models.TextField('내용')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='부모 댓글')
    is_deleted = models.BooleanField('삭제 여부', default=False)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '차트 댓글'
        verbose_name_plural = '차트 댓글들'
        ordering = ['created_at']
    
    def __str__(self):
        username = self.user.username if self.user else 'Anonymous'
        return f"{username}: {self.content[:50]}"

class Event(models.Model):
    """이벤트"""
    
    STATUS_CHOICES = [
        ('upcoming', '예정'),
        ('active', '진행중'),
        ('ended', '종료'),
    ]
    
    title = models.CharField('제목', max_length=200)
    description = models.TextField('설명')
    start_date = models.DateTimeField('시작일')
    end_date = models.DateTimeField('종료일')
    prize_description = models.TextField('상품 설명')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='upcoming')
    max_participants = models.IntegerField('최대 참가자 수', null=True, blank=True)
    participants_count = models.IntegerField('참가자 수', default=0)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '이벤트'
        verbose_name_plural = '이벤트들'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class EventParticipation(models.Model):
    """이벤트 참가"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='이벤트')
    prediction = models.ForeignKey(ChartPrediction, on_delete=models.CASCADE, verbose_name='예측')
    rank = models.IntegerField('순위', null=True, blank=True)
    prize_won = models.CharField('상품', max_length=200, blank=True)
    created_at = models.DateTimeField('참가일', auto_now_add=True)
    
    class Meta:
        verbose_name = '이벤트 참가'
        verbose_name_plural = '이벤트 참가들'
        unique_together = ['user', 'event']
