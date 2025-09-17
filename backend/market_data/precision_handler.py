"""
Decimal Precision Handler for Stock Market Data
Ensures accurate price representation with proper decimal places
"""

from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Union, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Set high precision context for calculations
getcontext().prec = 28


class PrecisionHandler:
    """주식 시장 데이터 정밀도 처리 클래스"""
    
    # 시장별 정밀도 설정
    MARKET_PRECISION = {
        'crypto': 8,        # 암호화폐는 최대 8자리
        'us_stock': 2,      # 미국 주식은 2자리 (센트)
        'kr_stock': 0,      # 한국 주식은 정수 (원)
        'jp_stock': 0,      # 일본 주식은 정수 (엔)
        'uk_stock': 2,      # 영국 주식은 2자리 (펜스)
        'ca_stock': 2,      # 캐나다 주식은 2자리
        'fr_stock': 2,      # 프랑스 주식은 2자리
        'de_stock': 2,      # 독일 주식은 2자리
        'tw_stock': 2,      # 대만 주식은 2자리
        'in_stock': 2,      # 인도 주식은 2자리
    }
    
    # 심볼별 특별 정밀도 (특정 암호화폐나 주식)
    SYMBOL_PRECISION = {
        # 고가 암호화폐 (낮은 정밀도)
        'BTC': 2,
        'ETH': 2,
        'BNB': 2,
        
        # 저가 암호화폐 (높은 정밀도)
        'DOGE': 6,
        'SHIB': 8,
        'ADA': 4,
        'XRP': 4,
        'MATIC': 4,
        
        # 한국 주식 (정수)
        '005930': 0,  # 삼성전자
        '000660': 0,  # SK하이닉스
        '035420': 0,  # NAVER
    }
    
    @classmethod
    def format_price(cls, price: Union[float, str, Decimal], 
                     symbol: str = '', market: str = 'us_stock') -> Decimal:
        """
        가격을 적절한 정밀도로 포맷팅
        
        Args:
            price: 포맷팅할 가격
            symbol: 심볼 (정밀도 결정용)
            market: 시장 타입
            
        Returns:
            포맷팅된 Decimal 가격
        """
        try:
            # Decimal로 변환
            if isinstance(price, str):
                decimal_price = Decimal(price)
            elif isinstance(price, (int, float)):
                decimal_price = Decimal(str(price))
            else:
                decimal_price = price
            
            # 정밀도 결정
            precision = cls._get_precision(symbol, market)
            
            # 반올림 적용
            quantize_value = Decimal('0.' + '0' * precision) if precision > 0 else Decimal('1')
            formatted_price = decimal_price.quantize(quantize_value, rounding=ROUND_HALF_UP)
            
            return formatted_price
            
        except Exception as e:
            logger.error(f"Price formatting error: {e}")
            return Decimal('0.00')
    
    @classmethod
    def format_percentage(cls, percentage: Union[float, str, Decimal]) -> Decimal:
        """
        퍼센테이지를 4자리 정밀도로 포맷팅
        """
        try:
            if isinstance(percentage, str):
                decimal_percentage = Decimal(percentage)
            elif isinstance(percentage, (int, float)):
                decimal_percentage = Decimal(str(percentage))
            else:
                decimal_percentage = percentage
            
            return decimal_percentage.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        except:
            return Decimal('0.0000')
    
    @classmethod
    def format_volume(cls, volume: Union[int, float, str]) -> int:
        """
        거래량을 정수로 포맷팅
        """
        try:
            return int(float(volume))
        except:
            return 0
    
    @classmethod
    def _get_precision(cls, symbol: str, market: str) -> int:
        """
        심볼과 시장에 따른 정밀도 반환
        """
        # 심볼별 특별 정밀도 우선
        if symbol.upper() in cls.SYMBOL_PRECISION:
            return cls.SYMBOL_PRECISION[symbol.upper()]
        
        # 시장별 기본 정밀도
        return cls.MARKET_PRECISION.get(market, 2)
    
    @classmethod
    def format_market_data(cls, data: Dict[str, Any], 
                          symbol: str = '', market: str = 'us_stock') -> Dict[str, Any]:
        """
        시장 데이터 전체를 적절한 정밀도로 포맷팅
        """
        formatted_data = data.copy()
        
        # 가격 관련 필드들
        price_fields = [
            'price', 'current_price', 'open_price', 'open', 'high', 'low', 
            'close', 'previous_close', 'predicted_price', 'actual_price',
            'trigger_price'
        ]
        
        for field in price_fields:
            if field in formatted_data and formatted_data[field] is not None:
                formatted_data[field] = float(cls.format_price(
                    formatted_data[field], symbol, market
                ))
        
        # 퍼센테이지 필드들
        percentage_fields = [
            'change_percent', 'change_percentage', 'profit_rate', 
            'accuracy_percentage', 'prediction_accuracy'
        ]
        
        for field in percentage_fields:
            if field in formatted_data and formatted_data[field] is not None:
                formatted_data[field] = float(cls.format_percentage(
                    formatted_data[field]
                ))
        
        # 거래량 필드들
        volume_fields = ['volume', 'market_cap']
        
        for field in volume_fields:
            if field in formatted_data and formatted_data[field] is not None:
                formatted_data[field] = cls.format_volume(formatted_data[field])
        
        return formatted_data
    
    @classmethod
    def get_display_precision(cls, symbol: str = '', market: str = 'us_stock') -> Dict[str, int]:
        """
        UI 표시용 정밀도 정보 반환
        """
        precision = cls._get_precision(symbol, market)
        
        return {
            'price_precision': precision,
            'percentage_precision': 4,
            'volume_precision': 0,
            'market': market,
            'symbol': symbol
        }
    
    @classmethod
    def validate_price_range(cls, price: Union[float, str, Decimal], 
                           symbol: str = '', market: str = 'us_stock') -> bool:
        """
        가격이 유효한 범위인지 검증
        """
        try:
            decimal_price = cls.format_price(price, symbol, market)
            
            # 기본 검증: 0보다 큰 값
            if decimal_price <= 0:
                return False
            
            # 시장별 최대값 검증
            max_values = {
                'crypto': Decimal('10000000'),    # 1천만 (비트코인 등)
                'us_stock': Decimal('100000'),    # 10만 달러
                'kr_stock': Decimal('10000000'),  # 1천만 원
            }
            
            max_value = max_values.get(market, Decimal('1000000'))
            
            return decimal_price <= max_value
            
        except:
            return False
    
    @classmethod
    def calculate_price_difference(cls, current: Union[float, str, Decimal], 
                                 previous: Union[float, str, Decimal],
                                 symbol: str = '', market: str = 'us_stock') -> Dict[str, Decimal]:
        """
        가격 차이와 변화율 계산
        """
        try:
            current_price = cls.format_price(current, symbol, market)
            previous_price = cls.format_price(previous, symbol, market)
            
            if previous_price == 0:
                return {
                    'price_change': Decimal('0'),
                    'change_percent': Decimal('0')
                }
            
            price_change = current_price - previous_price
            change_percent = (price_change / previous_price) * 100
            
            return {
                'price_change': price_change,
                'change_percent': cls.format_percentage(change_percent)
            }
            
        except Exception as e:
            logger.error(f"Price difference calculation error: {e}")
            return {
                'price_change': Decimal('0'),
                'change_percent': Decimal('0')
            }


# 편의 함수들
def format_price(price, symbol='', market='us_stock'):
    """간단한 가격 포맷팅 함수"""
    return PrecisionHandler.format_price(price, symbol, market)

def format_market_data(data, symbol='', market='us_stock'):
    """간단한 시장 데이터 포맷팅 함수"""
    return PrecisionHandler.format_market_data(data, symbol, market)

def get_precision_info(symbol='', market='us_stock'):
    """간단한 정밀도 정보 조회 함수"""
    return PrecisionHandler.get_display_precision(symbol, market)
