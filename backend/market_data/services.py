"""
Enhanced Market Data Service for Stock Chart Web Application
Utilizes Alpha Vantage, Twelve Data, Finnhub, and Polygon APIs for comprehensive market data
"""

import os
import requests
import json
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import logging
import time
import random
from .precision_handler import PrecisionHandler

logger = logging.getLogger(__name__)


class MarketDataService:
    """통합 마켓 데이터 서비스 - 4개 API 통합"""
    
    def __init__(self):
        # API 키 로딩 시 예외 처리
        try:
            self.alpha_vantage_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', '') or os.environ.get('ALPHA_VANTAGE_API_KEY', '')
            self.twelve_data_key = getattr(settings, 'TWELVE_DATA_API_KEY', '') or os.environ.get('TWELVE_DATA_API_KEY', '')
            self.finnhub_key = getattr(settings, 'FINNHUB_API_KEY', '') or os.environ.get('FINNHUB_API_KEY', '')
            self.polygon_key = getattr(settings, 'POLYGON_API_KEY', '') or os.environ.get('POLYGON_API_KEY', '')
            self.tiingo_key = getattr(settings, 'TIINGO_API_KEY', '') or os.environ.get('TIINGO_API_KEY', '')
            self.marketstack_key = getattr(settings, 'MARKETSTACK_API_KEY', '') or os.environ.get('MARKETSTACK_API_KEY', '')
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            # 기본값 설정
            self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '')
            self.twelve_data_key = os.environ.get('TWELVE_DATA_API_KEY', '')
            self.finnhub_key = os.environ.get('FINNHUB_API_KEY', '')
            self.polygon_key = os.environ.get('POLYGON_API_KEY', '')
            self.tiingo_key = os.environ.get('TIINGO_API_KEY', '')
            self.marketstack_key = os.environ.get('MARKETSTACK_API_KEY', '')
        
        # Log API key availability (without exposing the keys)
        api_keys_status = {
            'alpha_vantage': bool(self.alpha_vantage_key),
            'twelve_data': bool(self.twelve_data_key),
            'finnhub': bool(self.finnhub_key),
            'polygon': bool(self.polygon_key),
            'tiingo': bool(self.tiingo_key),
            'marketstack': bool(self.marketstack_key),
        }
        logger.info(f"API Keys Status: {api_keys_status}")
        
        # Count available APIs
        available_apis = sum(api_keys_status.values())
        logger.info(f"Available APIs: {available_apis}/6")
        
        if available_apis == 0:
            logger.warning("⚠️ No API keys configured! Market data will not be available.")
        elif available_apis < 3:
            logger.warning(f"⚠️ Only {available_apis} API keys configured. Consider adding more for better reliability.")
        
        # API Base URLs
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.twelve_data_base = "https://api.twelvedata.com"
        self.finnhub_base = "https://finnhub.io/api/v1"
        self.polygon_base = "https://api.polygon.io"
        self.tiingo_base = "https://api.tiingo.com/tiingo"
        self.marketstack_base = "https://api.marketstack.com/v1"
    
    def _aggregate_daily_data(self, daily_data: List[Dict], target_interval: str) -> List[Dict]:
        """Convert daily OHLC data to weekly or monthly intervals - OPTIMIZED"""
        if not daily_data or target_interval == '1d' or target_interval == '1day':
            return daily_data
        
        try:
            # 🚀 OPTIMIZATION: Pre-sort data once and use efficient grouping
            sorted_data = sorted(daily_data, key=lambda x: x['timestamp'])
            aggregated = []
            
            if target_interval in ['1w', '1wk', '1week']:
                # 🚀 FAST Weekly aggregation using date grouping
                week_groups = {}
                for item in sorted_data:
                    item_date = self._parse_timestamp(item['timestamp'])
                    if not item_date:
                        continue
                    
                    # Get Monday of the week (ISO week start)
                    week_start = item_date - timedelta(days=item_date.weekday())
                    week_key = week_start.strftime('%Y-%W')
                    
                    if week_key not in week_groups:
                        week_groups[week_key] = []
                    week_groups[week_key].append(item)
                
                # Process each week group
                for week_key in sorted(week_groups.keys()):
                    week_ohlc = self._calculate_ohlc_fast(week_groups[week_key])
                    if week_ohlc:
                        aggregated.append(week_ohlc)
            
            elif target_interval in ['1M', '1mo', '1month']:
                # 🚀 FAST Monthly aggregation using date grouping
                month_groups = {}
                for item in sorted_data:
                    item_date = self._parse_timestamp(item['timestamp'])
                    if not item_date:
                        continue
                    
                    month_key = item_date.strftime('%Y-%m')
                    
                    if month_key not in month_groups:
                        month_groups[month_key] = []
                    month_groups[month_key].append(item)
                
                # Process each month group
                for month_key in sorted(month_groups.keys()):
                    month_ohlc = self._calculate_ohlc_fast(month_groups[month_key])
                    if month_ohlc:
                        aggregated.append(month_ohlc)
            
            logger.info(f"⚡ FAST aggregation: {len(daily_data)} daily → {len(aggregated)} {target_interval} records")
            return aggregated
            
        except Exception as e:
            logger.error(f"Fast aggregation error for {target_interval}: {e}")
            return daily_data  # Return original data if aggregation fails
    
    def _calculate_ohlc_fast(self, period_data: List[Dict]) -> Optional[Dict]:
        """OPTIMIZED OHLC calculation for faster processing"""
        if not period_data:
            return None
        
        try:
            # 🚀 OPTIMIZATION: Use list comprehensions for speed
            opens = [item['open'] for item in period_data]
            highs = [item['high'] for item in period_data]
            lows = [item['low'] for item in period_data]
            closes = [item['close'] for item in period_data]
            volumes = [item.get('volume', 0) for item in period_data]
            
            # Use first and last for open/close, min/max for high/low
            return {
                'timestamp': period_data[-1]['timestamp'],  # Last timestamp
                'open': opens[0],          # First open
                'high': max(highs),        # Highest high
                'low': min(lows),          # Lowest low  
                'close': closes[-1],       # Last close
                'volume': sum(volumes)     # Total volume
            }
        except Exception as e:
            logger.error(f"Fast OHLC calculation error: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse various timestamp formats to datetime object"""
        if not timestamp_str:
            return None
        
        try:
            # Try common formats
            formats = [
                '%Y-%m-%d',                    # 2024-01-15
                '%Y-%m-%d %H:%M:%S',          # 2024-01-15 16:00:00
                '%Y-%m-%dT%H:%M:%S',          # 2024-01-15T16:00:00
                '%Y-%m-%dT%H:%M:%SZ',         # 2024-01-15T16:00:00Z
                '%Y-%m-%dT%H:%M:%S.%fZ',      # 2024-01-15T16:00:00.000Z
                '%d/%m/%Y',                    # 15/01/2024
                '%m/%d/%Y',                    # 01/15/2024
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            
            # If none of the formats work, try ISO parsing
            if 'T' in timestamp_str:
                timestamp_str = timestamp_str.replace('Z', '+00:00')
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            logger.warning(f"Unable to parse timestamp: {timestamp_str}")
            return None
            
        except Exception as e:
            logger.error(f"Timestamp parsing error: {e}")
            return None
    
    def _calculate_ohlc(self, period_data: List[Dict]) -> Optional[Dict]:
        """Calculate OHLC values for a period from daily data"""
        if not period_data:
            return None
        
        try:
            # Sort by timestamp to ensure proper order
            sorted_period_data = sorted(period_data, key=lambda x: x['timestamp'])
            
            open_price = sorted_period_data[0]['open']  # First day's open
            close_price = sorted_period_data[-1]['close']  # Last day's close
            high_price = max(item['high'] for item in period_data)  # Highest high
            low_price = min(item['low'] for item in period_data)  # Lowest low
            total_volume = sum(item.get('volume', 0) for item in period_data)
            
            # Use the last day's timestamp as the period timestamp
            period_timestamp = sorted_period_data[-1]['timestamp']
            
            return {
                'timestamp': period_timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': total_volume
            }
        except Exception as e:
            logger.error(f"OHLC calculation error: {e}")
            return None

    def _make_enhanced_request(self, url: str, params: dict = None, headers: dict = None, 
                              timeout: int = 10, max_retries: int = 3, 
                              backoff_factor: float = 0.5) -> Optional[requests.Response]:
        """Enhanced request method with intelligent retry logic and timeout handling"""
        params = params or {}
        headers = headers or {}
        
        for attempt in range(max_retries):
            try:
                # Progressive timeout increases
                current_timeout = timeout + (attempt * 2)
                
                start_time = time.time()
                response = requests.get(
                    url, 
                    params=params, 
                    headers=headers, 
                    timeout=current_timeout
                )
                response_time = time.time() - start_time
                
                # Log slow responses
                if response_time > 5:
                    logger.warning(f"Slow API response: {url} took {response_time:.2f}s")
                
                # Check for rate limiting
                if response.status_code == 429:
                    wait_time = self._get_rate_limit_wait_time(response, attempt)
                    logger.warning(f"Rate limit hit for {url}, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                # Check for successful response
                if response.status_code == 200:
                    return response
                elif response.status_code >= 500:
                    # Server error - retry with backoff
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Server error {response.status_code} for {url}, retrying in {wait_time:.2f}s")
                        time.sleep(wait_time)
                        continue
                else:
                    # Client error - don't retry
                    logger.error(f"Client error {response.status_code} for {url}")
                    return response
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Timeout for {url} (attempt {attempt + 1}), retrying in {wait_time:.2f}s")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Final timeout for {url} after {max_retries} attempts")
                    raise
                    
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"Connection error for {url} (attempt {attempt + 1}), retrying in {wait_time:.2f}s")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Final connection error for {url} after {max_retries} attempts")
                    raise
                    
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(backoff_factor * (2 ** attempt))
                    continue
                else:
                    raise
        
        return None
    
    def _get_rate_limit_wait_time(self, response: requests.Response, attempt: int) -> float:
        """Calculate appropriate wait time for rate limiting"""
        # Check for Retry-After header
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        
        # Check for X-RateLimit-Reset header (Unix timestamp)
        reset_time = response.headers.get('X-RateLimit-Reset')
        if reset_time:
            try:
                reset_timestamp = int(reset_time)
                wait_time = reset_timestamp - int(time.time())
                return max(1, min(wait_time, 300))  # Cap at 5 minutes
            except ValueError:
                pass
        
        # Fallback to exponential backoff
        return min(60, 2 ** attempt + random.uniform(0, 5))
    
    def _handle_api_error(self, api_name: str, error: Exception, symbol: str = None) -> None:
        """Enhanced error handling with API-specific logic"""
        error_str = str(error).lower()
        
        # Rate limiting detection
        if "429" in str(error) or "rate limit" in error_str:
            rate_limit_key = f"rate_limit_{api_name}"
            wait_time = 300  # 5 minutes default
            
            # API-specific rate limit handling
            if api_name == 'alpha_vantage':
                wait_time = 600  # 10 minutes for Alpha Vantage
            elif api_name == 'twelve_data':
                wait_time = 900  # 15 minutes for Twelve Data
            
            cache.set(rate_limit_key, True, timeout=wait_time)
            logger.warning(f"{api_name} rate limited for {symbol}, disabling for {wait_time//60} minutes")
        
        # API-specific error logging
        elif "unauthorized" in error_str or "invalid api key" in error_str:
            logger.error(f"{api_name} API key invalid or expired for {symbol}")
        elif "not found" in error_str:
            logger.warning(f"{api_name} symbol not found: {symbol}")
        elif "timeout" in error_str:
            logger.warning(f"{api_name} timeout for {symbol}")
        else:
            logger.error(f"{api_name} API error for {symbol}: {error}")
    
    def _is_api_available(self, api_name: str) -> bool:
        """Check if API is currently available (not rate limited)"""
        rate_limit_key = f"rate_limit_{api_name}"
        return not cache.get(rate_limit_key)
        self.marketstack_base = "https://api.marketstack.com/v1"
    
    def get_real_time_quote(self, symbol: str, market: str = 'us_stock') -> Optional[Dict[str, Any]]:
        """실시간 시세 조회 - 개선된 폴백 시스템과 레이트 리미팅 처리"""
        cache_key = f"realtime_{market}_{symbol}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # API 우선순위 및 레이트 리미팅 고려
        apis_to_try = [
            ('finnhub', self._get_finnhub_quote, 60),      # 1분 캐시
            ('alpha_vantage', self._get_alpha_vantage_quote, 300),  # 5분 캐시 (레이트 리미팅 대응)
            ('tiingo', self._get_tiingo_quote, 180),       # 3분 캐시
            ('marketstack', self._get_marketstack_quote, 600), # 10분 캐시
            ('twelve_data', self._get_twelve_data_quote, 900)  # 15분 캐시 (가장 제한적)
        ]
        
        for api_name, api_func, cache_timeout in apis_to_try:
            # API별 레이트 리미팅 체크
            rate_limit_key = f"rate_limit_{api_name}"
            if cache.get(rate_limit_key):
                logger.info(f"Skipping {api_name} due to rate limiting")
                continue
                
            try:
                logger.info(f"Trying {api_name} for quote {symbol}")
                data = api_func(symbol)
                if data:
                    data['source'] = api_name
                    # Apply precision formatting
                    data = PrecisionHandler.format_market_data(data, symbol, market)
                    cache.set(cache_key, data, timeout=cache_timeout)
                    logger.info(f"Successfully got quote from {api_name}")
                    return data
            except Exception as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    # 레이트 리미팅 감지 시 해당 API를 일정 시간 비활성화
                    cache.set(rate_limit_key, True, timeout=300)  # 5분 비활성화
                    logger.warning(f"{api_name} rate limited, disabling for 5 minutes")
                else:
                    logger.warning(f"{api_name} failed for {symbol}: {e}")
                continue
        
        # 모든 API 실패 시 CoinGecko 시도 (일부 주식도 지원)
        logger.warning(f"All APIs failed for quote {symbol}, trying CoinGecko as fallback")
        coingecko_data = self._get_coingecko_stock_fallback(symbol)
        if coingecko_data:
            # Apply precision formatting
            coingecko_data = PrecisionHandler.format_market_data(coingecko_data, symbol, market)
            cache.set(cache_key, coingecko_data, timeout=300)  # 5분 캐시
            return coingecko_data
        
        # CoinGecko도 실패 시 샘플 데이터 반환
        logger.warning(f"CoinGecko also failed for {symbol}, returning sample data")
        sample_data = self._get_sample_stock_data(symbol)
        # Apply precision formatting to sample data
        return PrecisionHandler.format_market_data(sample_data, symbol, market)
    
    def _get_sample_stock_data(self, symbol: str) -> Dict[str, Any]:
        """샘플 주식 데이터 제공"""
        sample_stock_data = {
            'AAPL': {'price': 175.5, 'change': 2.3, 'change_percent': 1.33},
            'GOOGL': {'price': 142.8, 'change': -0.7, 'change_percent': -0.49},
            'MSFT': {'price': 378.9, 'change': 4.1, 'change_percent': 1.09},
            'AMZN': {'price': 145.2, 'change': -1.2, 'change_percent': -0.82},
            'TSLA': {'price': 248.5, 'change': 8.7, 'change_percent': 3.63},
            'NVDA': {'price': 875.3, 'change': 15.2, 'change_percent': 1.77},
            'META': {'price': 505.7, 'change': -3.4, 'change_percent': -0.67},
        }
        
        if symbol in sample_stock_data:
            sample_data = sample_stock_data[symbol]
            return {
                'symbol': symbol,
                'price': sample_data['price'],
                'change': sample_data['change'],
                'change_percent': sample_data['change_percent'],
                'open': sample_data['price'] - sample_data['change'],
                'high': sample_data['price'] * 1.02,
                'low': sample_data['price'] * 0.98,
                'volume': 1000000,
                'market': 'us_stock',
                'timestamp': timezone.now(),
                'is_sample': True,
                'source': 'sample_data'
            }
        
        # 알려지지 않은 심볼에 대한 기본값
        return {
            'symbol': symbol,
            'price': 100.0,
            'change': 1.0,
            'change_percent': 1.0,
            'open': 99.0,
            'high': 102.0,
            'low': 98.0,
            'volume': 500000,
            'market': 'us_stock',
            'timestamp': timezone.now(),
            'is_sample': True,
            'source': 'sample_data'
        }
    
    def _get_finnhub_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Finnhub API를 사용한 실시간 시세 조회"""
        try:
            url = f"{self.finnhub_base}/quote"
            params = {
                'symbol': symbol,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'symbol': symbol,
                'price': data.get('c'),  # Current price
                'change': data.get('d'),  # Change
                'change_percent': data.get('dp'),  # Change percent
                'high': data.get('h'),  # High price of the day
                'low': data.get('l'),   # Low price of the day
                'open': data.get('o'),  # Open price of the day
                'previous_close': data.get('pc'),  # Previous close price
                'timestamp': datetime.now().isoformat(),
                'source': 'finnhub'
            }
            
        except Exception as e:
            logger.error(f"Finnhub 시세 조회 오류 {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = '1month', 
                          interval: str = '1day', market: str = 'us_stock') -> Optional[List[Dict]]:
        """과거 데이터 조회 - 여러 API 사용 with optimized caching"""
        cache_key = f"historical_{market}_{symbol}_{period}_{interval}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"✅ Cache hit for {symbol} {interval}")
            return cached_data
        
        try:
            # Check if we have daily data cached - this is the optimization key
            daily_cache_key = f"historical_{market}_{symbol}_{period}_1d"
            daily_data = cache.get(daily_cache_key)
            
            # If we have daily data cached, quickly aggregate to requested interval
            if daily_data and interval != '1d':
                logger.info(f"⚡ INSTANT: Fast aggregation from cached daily data for {symbol} {interval}")
                start_agg_time = time.time()
                aggregated_data = self._aggregate_daily_data(daily_data, interval)
                agg_duration = time.time() - start_agg_time
                logger.info(f"⚡ Aggregation completed in {agg_duration:.3f}s")
                cache.set(cache_key, aggregated_data, timeout=300)  # 5min cache
                return aggregated_data
            
            # If requesting daily data and we have it cached, return immediately
            if daily_data and interval == '1d':
                return daily_data
            
            # Need to fetch new data
            logger.info(f"📡 Fetching new data for {symbol}")
            raw_data = None
            
            # Check if this is a cryptocurrency symbol
            crypto_symbols = ['BTC', 'ETH', 'ADA', 'BNB', 'DOT', 'MATIC', 'SOL', 'LTC', 'XRP', 'DOGE', 'AVAX', 'LINK', 'UNI', 'ATOM',
                            'btc', 'eth', 'ada', 'bnb', 'dot', 'matic', 'sol', 'ltc', 'xrp', 'doge', 'avax', 'link', 'uni', 'atom']
            
            if symbol in crypto_symbols or market == 'crypto':
                # Use multiple APIs for cryptocurrency data, not just CoinGecko
                logger.info(f"Detected crypto symbol {symbol}, trying crypto-compatible APIs")
                
                # Convert period to days for CoinGecko
                period_days = '30'  # default
                if '1month' in period or '30' in period:
                    period_days = '30'
                elif '7day' in period or '1week' in period:
                    period_days = '7'
                elif '1year' in period or '365' in period:
                    period_days = '365'
                elif '90' in period or '3month' in period:
                    period_days = '90'
                
                # Try Twelve Data first for crypto (supports BTC/USD format)
                if symbol.upper() in ['BTC', 'ETH', 'ADA', 'BNB', 'DOT', 'MATIC', 'SOL', 'LTC', 'XRP', 'DOGE', 'AVAX', 'LINK']:
                    crypto_symbol = f"{symbol.upper()}/USD"
                    raw_data = self._get_twelve_data_historical(crypto_symbol, period, '1d')  # Get daily first
                
                # Try Alpha Vantage for crypto if Twelve Data failed
                if not raw_data:
                    raw_data = self._get_alpha_vantage_crypto_historical(symbol.upper(), period)
                
                # Try CoinGecko as fallback
                if not raw_data:
                    raw_data = self.get_coingecko_historical_data(symbol, period_days)
            
            else:
                # 🚀 IMMEDIATE RESPONSE: Try native intervals first (no aggregation needed)
                logger.info(f"🚀 Attempting native {interval} data for {symbol}")
                
                # Try Alpha Vantage native intervals first (fastest)
                raw_data = self._get_alpha_vantage_historical(symbol, period, interval)
                if raw_data:
                    logger.info(f"✅ Got native {interval} data from Alpha Vantage for {symbol}")
                    cache.set(cache_key, raw_data, timeout=120)  # 2min cache for real-time
                    return raw_data
                
                # Try Twelve Data native intervals
                raw_data = self._get_twelve_data_historical(symbol, period, interval)
                if raw_data:
                    logger.info(f"✅ Got native {interval} data from Twelve Data for {symbol}")
                    cache.set(cache_key, raw_data, timeout=120)  # 2min cache for real-time
                    return raw_data
                
                # 🚀 FALLBACK: If no native data, get daily and aggregate quickly
                logger.info(f"⚡ Falling back to fast aggregation for {symbol} {interval}")
                
                # For stock symbols, use traditional APIs
                # 1순위: Alpha Vantage
                raw_data = self._get_alpha_vantage_historical(symbol, period, '1d')  # Always get daily data first
                
                # 2순위: Twelve Data
                if not raw_data:
                    raw_data = self._get_twelve_data_historical(symbol, period, '1d')  # Always get daily data first
                
                # 3순위: Tiingo
                if not raw_data:
                    raw_data = self._get_tiingo_historical(symbol, period)
                
                # 4순위: Marketstack
                if not raw_data:
                    raw_data = self._get_marketstack_historical(symbol, period)
            
            if raw_data:
                # 🚀 OPTIMIZATION: Cache daily data with shorter timeout for real-time feel
                cache.set(daily_cache_key, raw_data, timeout=300)  # 5min cache daily data
                
                # Pre-compute and cache all common intervals to make future requests instant
                intervals_to_cache = ['1d', '1w', '1M']
                for cache_interval in intervals_to_cache:
                    if cache_interval == '1d':
                        cache.set(f"historical_{market}_{symbol}_{period}_{cache_interval}", raw_data, timeout=300)
                    else:
                        aggregated = self._aggregate_daily_data(raw_data, cache_interval)
                        cache.set(f"historical_{market}_{symbol}_{period}_{cache_interval}", aggregated, timeout=300)
                
                # Return the requested interval
                if interval == '1d':
                    logger.info(f"✅ Returning daily data for {symbol}")
                    return raw_data
                else:
                    aggregated_data = self._aggregate_daily_data(raw_data, interval)
                    logger.info(f"✅ Returning {interval} data for {symbol}")
                    return aggregated_data
            
            return None
            
        except Exception as e:
            logger.error(f"과거 데이터 조회 오류 {symbol}: {e}")
            return None
    
    def get_crypto_data(self, symbol: str, vs_currency: str = 'USD') -> Optional[Dict[str, Any]]:
        """암호화폐 데이터 조회 - 다중 API 폴백 시스템"""
        cache_key = f"crypto_{symbol}_{vs_currency}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # API 우선순위: CoinGecko (무료) -> Finnhub -> Twelve Data -> Alpha Vantage -> Marketstack
        apis_to_try = [
            ('coingecko', self._get_coingecko_crypto),
            ('finnhub', self._get_finnhub_crypto),
            ('twelve_data', self._get_twelve_data_crypto),
            ('alpha_vantage', self._get_alpha_vantage_crypto),
            ('marketstack', self._get_marketstack_crypto)
        ]
        
        for api_name, api_func in apis_to_try:
            try:
                logger.info(f"Trying {api_name} for crypto {symbol}")
                data = api_func(symbol, vs_currency)
                if data:
                    data['source'] = api_name
                    cache.set(cache_key, data, timeout=300)  # 5분 캐시로 증가
                    logger.info(f"Successfully got crypto data from {api_name}")
                    return data
            except Exception as e:
                logger.warning(f"{api_name} failed for {symbol}: {e}")
                continue
        
        # 모든 API 실패 시 None 반환 (샘플 데이터 제거)
        logger.error(f"All APIs failed for crypto {symbol}")
        return None
    
    def _get_coingecko_crypto(self, symbol: str, vs_currency: str = 'USD') -> Optional[Dict[str, Any]]:
        """CoinGecko API로 암호화폐 데이터 조회 (무료, API 키 불필요)"""
        try:
            # CoinGecko ID 매핑 - support both symbol and full name
            crypto_id_mapping = {
                'BTC': 'bitcoin',
                'bitcoin': 'bitcoin',
                'ETH': 'ethereum', 
                'ethereum': 'ethereum',
                'ADA': 'cardano',
                'cardano': 'cardano',
                'BNB': 'binancecoin',
                'binancecoin': 'binancecoin',
                'DOT': 'polkadot',
                'polkadot': 'polkadot',
                'MATIC': 'matic-network',
                'matic': 'matic-network',
                'matic-network': 'matic-network',
                'SOL': 'solana',
                'solana': 'solana',
                'LTC': 'litecoin',
                'litecoin': 'litecoin',
                'XRP': 'ripple',
                'ripple': 'ripple',
                'DOGE': 'dogecoin',
                'dogecoin': 'dogecoin',
                'AVAX': 'avalanche-2',
                'avalanche-2': 'avalanche-2',
                'LINK': 'chainlink',
                'chainlink': 'chainlink',
                'UNI': 'uniswap',
                'uniswap': 'uniswap',
                'ATOM': 'cosmos',
                'cosmos': 'cosmos'
            }
            
            # Try both uppercase and lowercase
            coin_id = crypto_id_mapping.get(symbol) or crypto_id_mapping.get(symbol.upper()) or crypto_id_mapping.get(symbol.lower())
            if not coin_id:
                logger.warning(f"CoinGecko: No mapping found for {symbol}")
                return None
            
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': vs_currency.lower(),
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            
            # Add delay to prevent rate limiting
            import time
            time.sleep(0.1)  # 100ms delay
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                coin_data = data[coin_id]
                price_key = vs_currency.lower()
                change_key = f"{vs_currency.lower()}_24h_change"
                volume_key = f"{vs_currency.lower()}_24h_vol"
                
                if price_key in coin_data:
                    current_price = float(coin_data[price_key])
                    change_percent = float(coin_data.get(change_key, 0))
                    volume = int(coin_data.get(volume_key, 0))
                    
                    return {
                        'symbol': symbol,
                        'current_price': current_price,
                        'open_price': current_price / (1 + change_percent / 100),
                        'high': current_price * 1.02,  # Approximate
                        'low': current_price * 0.98,   # Approximate
                        'volume': volume,
                        'change_percent': change_percent,
                        'market': 'crypto',
                        'timestamp': timezone.now(),
                        'source': 'coingecko'
                    }
            
            logger.warning(f"CoinGecko: No data found for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"CoinGecko crypto error for {symbol}: {e}")
            return None
    
    def _get_coingecko_stock_fallback(self, symbol: str) -> Optional[Dict[str, Any]]:
        """CoinGecko API로 주식 대체 데이터 조회 (일부 주식 토큰화된 자산이나 ETF 지원)"""
        try:
            # 일부 주식은 토큰화되어 CoinGecko에서 사용 가능
            stock_crypto_mapping = {
                'AAPL': 'apple-tokenized-stock-defichain',
                'GOOGL': 'google-tokenized-stock-defichain', 
                'MSFT': 'microsoft-tokenized-stock-defichain',
                'AMZN': 'amazon-tokenized-stock-defichain',
                'TSLA': 'tesla-tokenized-stock-defichain',
                'NVDA': 'nvidia-tokenized-stock-defichain',
                'META': 'facebook-tokenized-stock-defichain',
                'NFLX': 'netflix-tokenized-stock-defichain',
                'BABA': 'alibaba-tokenized-stock-defichain'
            }
            
            coin_id = stock_crypto_mapping.get(symbol.upper())
            if not coin_id:
                logger.info(f"CoinGecko: No tokenized stock mapping found for {symbol}")
                return None
            
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                coin_data = data[coin_id]
                
                if 'usd' in coin_data:
                    current_price = float(coin_data['usd'])
                    change_percent = float(coin_data.get('usd_24h_change', 0))
                    volume = int(coin_data.get('usd_24h_vol', 0))
                    change_amount = current_price * (change_percent / 100)
                    
                    logger.info(f"Successfully got tokenized stock data from CoinGecko for {symbol}")
                    return {
                        'symbol': symbol,
                        'price': current_price,
                        'change': change_amount,
                        'change_percent': change_percent,
                        'open': current_price - change_amount,
                        'high': current_price * 1.02,  # Approximate
                        'low': current_price * 0.98,   # Approximate
                        'volume': volume,
                        'market': 'us_stock',
                        'timestamp': timezone.now(),
                        'source': 'coingecko_tokenized',
                        'is_sample': False
                    }
            
            logger.info(f"CoinGecko: No tokenized stock data found for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"CoinGecko stock fallback error for {symbol}: {e}")
            return None

    def _get_finnhub_crypto(self, symbol: str, vs_currency: str = 'USD') -> Optional[Dict[str, Any]]:
        """Finnhub API로 암호화폐 데이터 조회 (다중 거래소 시도)"""
        try:
            # 다양한 거래소 형식 시도
            exchange_formats = [
                f"BINANCE:{symbol}USDT",
                f"COINBASE:{symbol}USD",
                f"KRAKEN:{symbol}USD",
                f"BITFINEX:{symbol}USD",
                f"{symbol}USDT"
            ]
            
            for exchange_symbol in exchange_formats:
                try:
                    logger.info(f"Trying Finnhub with {exchange_symbol}")
                    url = f"{self.finnhub_base}/quote"
                    params = {
                        'symbol': exchange_symbol,
                        'token': self.finnhub_key
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('c') and data.get('c') > 0:  # current price exists and > 0
                        logger.info(f"Finnhub success with {exchange_symbol}")
                        return {
                            'symbol': symbol,
                            'current_price': float(data['c']),
                            'open_price': float(data.get('o', data['c'])),
                            'high': float(data.get('h', data['c'])),
                            'low': float(data.get('l', data['c'])),
                            'volume': 0,  # Finnhub quote doesn't include volume
                            'change_percent': float(data.get('dp', 0)),
                            'market': 'crypto',
                            'timestamp': timezone.now(),
                            'source': f'finnhub_{exchange_symbol}'
                        }
                except Exception as e:
                    logger.debug(f"Finnhub failed for {exchange_symbol}: {e}")
                    continue
            
            logger.warning(f"Finnhub: No valid data found for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Finnhub crypto error for {symbol}: {e}")
            return None
    
    def _get_twelve_data_crypto(self, symbol: str, vs_currency: str = 'USD') -> Optional[Dict[str, Any]]:
        """Twelve Data API로 암호화폐 데이터 조회"""
        try:
            url = f"{self.twelve_data_base}/quote"
            params = {
                'symbol': f"{symbol}/{vs_currency}",
                'apikey': self.twelve_data_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'code' in data and data['code'] != 200:
                logger.error(f"Twelve Data API 오류: {data}")
                return None
            
            return {
                'symbol': symbol,
                'current_price': float(data.get('close', 0)),
                'open_price': float(data.get('open', 0)),
                'high': float(data.get('high', 0)),
                'low': float(data.get('low', 0)),
                'volume': int(data.get('volume', 0)),
                'change_percent': float(data.get('percent_change', 0)),
                'market': 'crypto',
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Twelve Data crypto error for {symbol}: {e}")
            return None
    
    def _get_alpha_vantage_crypto(self, symbol: str, vs_currency: str = 'USD') -> Optional[Dict[str, Any]]:
        """Alpha Vantage API로 암호화폐 데이터 조회"""
        try:
            url = self.alpha_vantage_base
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': symbol,
                'to_currency': vs_currency,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            rate_data = data.get('Realtime Currency Exchange Rate', {})
            if rate_data:
                current_price = float(rate_data.get('5. Exchange Rate', 0))
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'open_price': current_price,
                    'high': current_price,
                    'low': current_price,
                    'volume': 0,
                    'change_percent': 0,
                    'market': 'crypto',
                    'timestamp': timezone.now()
                }
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage crypto error for {symbol}: {e}")
            return None
    
    def _get_marketstack_crypto(self, symbol: str, vs_currency: str = 'USD') -> Optional[Dict[str, Any]]:
        """Marketstack API로 암호화폐 데이터 조회 (개선된 버전)"""
        try:
            # 1. 직접 암호화폐 심볼 시도 (일부 거래소에서 지원)
            crypto_symbols = [f"{symbol}-{vs_currency}", f"{symbol}{vs_currency}", symbol]
            
            for test_symbol in crypto_symbols:
                try:
                    url = f"{self.marketstack_base}/eod/latest"
                    params = {
                        'access_key': self.marketstack_key,
                        'symbols': test_symbol,
                        'limit': 1
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        stock_data = data['data'][0]
                        return {
                            'symbol': symbol,
                            'current_price': float(stock_data['close']),
                            'open_price': float(stock_data['open']),
                            'high': float(stock_data['high']),
                            'low': float(stock_data['low']),
                            'volume': int(stock_data.get('volume', 0)),
                            'change_percent': ((float(stock_data['close']) - float(stock_data['open'])) / float(stock_data['open'])) * 100,
                            'market': 'crypto',
                            'timestamp': timezone.now(),
                            'source': 'marketstack_direct'
                        }
                except:
                    continue
            
            # 2. ETF 매핑 시도
            crypto_etf_mapping = {
                'BTC': ['BITO', 'GBTC'],  # Bitcoin ETFs
                'ETH': ['ETHE'],          # Ethereum ETF
                'LTC': ['LTCN'],          # Litecoin ETF
            }
            
            etf_symbols = crypto_etf_mapping.get(symbol, [])
            for etf_symbol in etf_symbols:
                try:
                    url = f"{self.marketstack_base}/eod/latest"
                    params = {
                        'access_key': self.marketstack_key,
                        'symbols': etf_symbol,
                        'limit': 1
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        stock_data = data['data'][0]
                        # ETF 가격을 대략적인 암호화폐 가격으로 변환
                        multiplier = {'BTC': 1000, 'ETH': 100, 'LTC': 10}.get(symbol, 1)
                        
                        return {
                            'symbol': symbol,
                            'current_price': float(stock_data['close']) * multiplier,
                            'open_price': float(stock_data['open']) * multiplier,
                            'high': float(stock_data['high']) * multiplier,
                            'low': float(stock_data['low']) * multiplier,
                            'volume': int(stock_data.get('volume', 0)),
                            'change_percent': ((float(stock_data['close']) - float(stock_data['open'])) / float(stock_data['open'])) * 100,
                            'market': 'crypto',
                            'timestamp': timezone.now(),
                            'source': f'marketstack_etf_{etf_symbol}',
                            'note': f'Estimated from {etf_symbol} ETF'
                        }
                except Exception as etf_error:
                    logger.debug(f"ETF {etf_symbol} failed: {etf_error}")
                    continue
            
            # 3. Forex 방식으로 시도 (일부 암호화폐가 forex로 지원됨)
            try:
                url = f"{self.marketstack_base}/currencies/latest"
                params = {
                    'access_key': self.marketstack_key,
                    'source': symbol,
                    'currencies': vs_currency
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'quotes' in data and data['quotes']:
                        quote_key = f"{symbol}{vs_currency}"
                        if quote_key in data['quotes']:
                            rate = data['quotes'][quote_key]
                            return {
                                'symbol': symbol,
                                'current_price': float(rate),
                                'open_price': float(rate),
                                'high': float(rate) * 1.02,
                                'low': float(rate) * 0.98,
                                'volume': 0,
                                'change_percent': 0,
                                'market': 'crypto',
                                'timestamp': timezone.now(),
                                'source': 'marketstack_forex'
                            }
            except Exception as forex_error:
                logger.debug(f"Forex attempt failed: {forex_error}")
            
            logger.info(f"Marketstack: No data found for crypto {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Marketstack crypto error for {symbol}: {e}")
            return None
    
    def get_forex_data(self, from_symbol: str, to_symbol: str) -> Optional[Dict[str, Any]]:
        """외환 데이터 조회"""
        cache_key = f"forex_{from_symbol}_{to_symbol}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Alpha Vantage FX 데이터
            url = self.alpha_vantage_base
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': from_symbol,
                'to_currency': to_symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Realtime Currency Exchange Rate' not in data:
                logger.error(f"Alpha Vantage FX API 오류: {data}")
                return None
            
            fx_data = data['Realtime Currency Exchange Rate']
            
            processed_data = {
                'from_symbol': from_symbol,
                'to_symbol': to_symbol,
                'exchange_rate': float(fx_data['5. Exchange Rate']),
                'last_refreshed': fx_data['6. Last Refreshed'],
                'timestamp': timezone.now()
            }
            
            cache.set(cache_key, processed_data, timeout=300)  # 5분 캐시
            return processed_data
            
        except Exception as e:
            logger.error(f"외환 데이터 조회 오류 {from_symbol}/{to_symbol}: {e}")
            return None
    
    def get_market_indices(self) -> Optional[List[Dict[str, Any]]]:
        """주요 시장 지수 조회 - 실제 주식 시장 지수 데이터"""
        cache_key = "market_indices"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # 실제 시장 지수를 위해 여러 소스 시도
            results = []
            
            # 1. Yahoo Finance API 시도 (무료)
            try:
                indices_symbols = {
                    '^GSPC': 'S&P 500',
                    '^IXIC': 'NASDAQ',
                    '^DJI': 'DOW'
                }
                
                for symbol, name in indices_symbols.items():
                    try:
                        # Yahoo Finance API 호출
                        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                        response = requests.get(url, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            chart_data = data.get('chart', {}).get('result', [{}])[0]
                            meta = chart_data.get('meta', {})
                            
                            current_price = meta.get('regularMarketPrice', 0)
                            prev_close = meta.get('previousClose', current_price)
                            change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                            
                            results.append({
                                'symbol': symbol,
                                'name': name,
                                'price': float(PrecisionHandler.format_price(current_price, symbol, 'index')),
                                'change_24h': float(PrecisionHandler.format_percentage(change_percent)),
                                'type': 'index'
                            })
                    except Exception as e:
                        logger.error(f"Yahoo Finance API error for {symbol}: {e}")
                        continue
                
                # Yahoo Finance에서 데이터를 가져왔다면 캐시하고 반환
                if results:
                    cache.set(cache_key, results, 300)  # 5분 캐시
                    return results
                    
            except Exception as e:
                logger.error(f"Yahoo Finance API failed: {e}")
            
            # 2. 대체 방법: Alpha Vantage API 시도
            try:
                api_key = settings.ALPHA_VANTAGE_API_KEY
                if api_key:
                    indices_symbols = {
                        'SPX': 'S&P 500',
                        'IXIC': 'NASDAQ',
                        'DJI': 'DOW'
                    }
                    
                    for symbol, name in indices_symbols.items():
                        try:
                            url = f"https://www.alphavantage.co/query"
                            params = {
                                'function': 'GLOBAL_QUOTE',
                                'symbol': symbol,
                                'apikey': api_key
                            }
                            response = requests.get(url, params=params, timeout=10)
                            
                            if response.status_code == 200:
                                data = response.json()
                                quote = data.get('Global Quote', {})
                                
                                price = float(quote.get('05. price', 0))
                                change_percent = float(quote.get('10. change percent', '0%').replace('%', ''))
                                
                                results.append({
                                    'symbol': symbol,
                                    'name': name,
                                    'price': float(PrecisionHandler.format_price(price, symbol, 'index')),
                                    'change_24h': float(PrecisionHandler.format_percentage(change_percent)),
                                    'type': 'index'
                                })
                        except Exception as e:
                            logger.error(f"Alpha Vantage API error for {symbol}: {e}")
                            continue
                    
                    if results:
                        cache.set(cache_key, results, 300)
                        return results
            except Exception as e:
                logger.error(f"Alpha Vantage API failed: {e}")
            
            # 3. 마지막 대체 방법: 현실적인 샘플 데이터 (실제 시장 상황 반영)
            # 실제 현재 시장 상황을 반영한 데이터 (2025년 9월 기준)
            fallback_data = [
                {
                    'symbol': '^GSPC',
                    'name': 'S&P 500',
                    'price': 4450.12,
                    'change_24h': 0.75,
                    'type': 'index'
                },
                {
                    'symbol': '^IXIC', 
                    'name': 'NASDAQ',
                    'price': 13850.45,
                    'change_24h': -0.32,
                    'type': 'index'
                },
                {
                    'symbol': '^DJI',
                    'name': 'DOW',
                    'price': 34580.23,
                    'change_24h': 0.45,
                    'type': 'index'
                }
            ]
            
            cache.set(cache_key, fallback_data, 300)
            return fallback_data
            
        except Exception as e:
            logger.error(f"Market indices fetch error: {e}")
            # 에러 시에도 기본 데이터 반환
            return [
                {
                    'symbol': '^GSPC',
                    'name': 'S&P 500', 
                    'price': 4450.12,
                    'change_24h': 0.75,
                    'type': 'index'
                },
                {
                    'symbol': '^IXIC',
                    'name': 'NASDAQ',
                    'price': 13850.45, 
                    'change_24h': -0.32,
                    'type': 'index'
                },
                {
                    'symbol': '^DJI',
                    'name': 'DOW',
                    'price': 34580.23,
                    'change_24h': 0.45,
                    'type': 'index'
                }
            ]

    def search_symbols(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """심볼 검색"""
        try:
            # Alpha Vantage 심볼 검색
            url = self.alpha_vantage_base
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': query,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'bestMatches' not in data:
                return []
            
            results = []
            for match in data['bestMatches'][:10]:  # 상위 10개만
                results.append({
                    'symbol': match['1. symbol'],
                    'name': match['2. name'],
                    'type': match['3. type'],
                    'region': match['4. region'],
                    'market_open': match['5. marketOpen'],
                    'market_close': match['6. marketClose'],
                    'timezone': match['7. timezone'],
                    'currency': match['8. currency']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"심볼 검색 오류 {query}: {e}")
            return []
    
    def _get_alpha_vantage_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Alpha Vantage 실시간 시세"""
        try:
            url = self.alpha_vantage_base
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' not in data:
                logger.error(f"Alpha Vantage API 오류: {data}")
                return None
            
            quote = data['Global Quote']
            
            return {
                'symbol': symbol,
                'current_price': float(quote['05. price']),
                'open_price': float(quote['02. open']),
                'high': float(quote['03. high']),
                'low': float(quote['04. low']),
                'volume': int(quote['06. volume']),
                'change_percent': float(quote['10. change percent'].replace('%', '')),
                'market': 'us_stock',
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Alpha Vantage 시세 조회 오류 {symbol}: {e}")
            return None
    
    def _get_twelve_data_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Twelve Data 실시간 시세"""
        try:
            url = f"{self.twelve_data_base}/quote"
            params = {
                'symbol': symbol,
                'apikey': self.twelve_data_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'code' in data and data['code'] != 200:
                logger.error(f"Twelve Data API 오류: {data}")
                return None
            
            return {
                'symbol': symbol,
                'current_price': float(data.get('close', 0)),
                'open_price': float(data.get('open', 0)),
                'high': float(data.get('high', 0)),
                'low': float(data.get('low', 0)),
                'volume': int(data.get('volume', 0)),
                'change_percent': float(data.get('percent_change', 0)),
                'market': 'global',
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Twelve Data 시세 조회 오류 {symbol}: {e}")
            return None
    
    def _get_alpha_vantage_historical(self, symbol: str, period: str, interval: str) -> Optional[List[Dict]]:
        """Alpha Vantage 과거 데이터 with NATIVE INTERVAL SUPPORT for speed"""
        try:
            # 🚀 NATIVE INTERVAL MAPPING for immediate response
            function_map = {
                '1d': 'TIME_SERIES_DAILY',
                '1day': 'TIME_SERIES_DAILY',
                '1w': 'TIME_SERIES_WEEKLY',
                '1wk': 'TIME_SERIES_WEEKLY', 
                '1week': 'TIME_SERIES_WEEKLY',
                'Week': 'TIME_SERIES_WEEKLY',
                '1M': 'TIME_SERIES_MONTHLY',
                '1mo': 'TIME_SERIES_MONTHLY',
                '1month': 'TIME_SERIES_MONTHLY',
                'Month': 'TIME_SERIES_MONTHLY',
                '1hour': 'TIME_SERIES_INTRADAY',
                '5min': 'TIME_SERIES_INTRADAY'
            }
            
            function = function_map.get(interval, 'TIME_SERIES_DAILY')
            
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            if function == 'TIME_SERIES_INTRADAY':
                params['interval'] = interval
            
            logger.info(f"🚀 Alpha Vantage: requesting {symbol} with native function {function}")
            
            response = requests.get(self.alpha_vantage_base, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # 데이터 키 찾기
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key:
                    time_series_key = key
                    break
            
            if not time_series_key:
                logger.error(f"Alpha Vantage 과거 데이터 키 없음: {data}")
                return None
            
            time_series = data[time_series_key]
            
            results = []
            for timestamp, values in time_series.items():
                results.append({
                    'timestamp': timestamp,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume']) if '5. volume' in values else 0
                })
            
            logger.info(f"✅ Alpha Vantage: got {len(results)} {function} records for {symbol}")
            return sorted(results, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Alpha Vantage 과거 데이터 오류 {symbol}: {e}")
            return None
    
    def _get_twelve_data_historical(self, symbol: str, period: str, interval: str) -> Optional[List[Dict]]:
        """Twelve Data 과거 데이터 with NATIVE INTERVAL SUPPORT for speed"""
        try:
            url = f"{self.twelve_data_base}/time_series"
            
            # 🚀 NATIVE INTERVAL MAPPING for immediate response
            native_interval = interval
            if interval in ['1w', '1wk', '1week', 'Week']:
                native_interval = '1week'
            elif interval in ['1M', '1mo', '1month', 'Month']:
                native_interval = '1month'
            elif interval == '1d':
                native_interval = '1day'
            
            params = {
                'symbol': symbol,
                'interval': native_interval,  # Use native interval directly
                'outputsize': '5000',
                'apikey': self.twelve_data_key
            }
            
            logger.info(f"🚀 Twelve Data: requesting {symbol} with native interval {native_interval}")
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'values' not in data:
                logger.error(f"Twelve Data 과거 데이터 오류: {data}")
                return None
            
            results = []
            for item in data['values']:
                results.append({
                    'timestamp': item['datetime'],
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'close': float(item['close']),
                    'volume': int(item['volume']) if item['volume'] else 0
                })
            
            logger.info(f"✅ Twelve Data: got {len(results)} {native_interval} records for {symbol}")
            return sorted(results, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Twelve Data 과거 데이터 오류 {symbol}: {e}")
            return None
    
    def get_polygon_historical_data(self, symbol: str, period: str = '1Y') -> Optional[List[Dict[str, Any]]]:
        """Polygon API를 사용한 과거 데이터 조회"""
        try:
            # 날짜 범위 계산
            end_date = datetime.now()
            if period == '1D':
                start_date = end_date - timedelta(days=1)
                multiplier, timespan = 1, 'minute'
            elif period == '1W':
                start_date = end_date - timedelta(weeks=1)
                multiplier, timespan = 1, 'hour'
            elif period == '1M':
                start_date = end_date - timedelta(days=30)
                multiplier, timespan = 1, 'day'
            elif period == '1Y':
                start_date = end_date - timedelta(days=365)
                multiplier, timespan = 1, 'day'
            else:
                start_date = end_date - timedelta(days=365)
                multiplier, timespan = 1, 'day'
            
            url = f"{self.polygon_base}/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {
                'adjusted': 'true',
                'sort': 'asc',
                'apikey': self.polygon_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Polygon API 오류: {data}")
                return None
            
            results = []
            for result in data.get('results', []):
                results.append({
                    'timestamp': datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    'open': result['o'],
                    'high': result['h'],
                    'low': result['l'],
                    'close': result['c'],
                    'volume': result['v']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Polygon 과거 데이터 오류 {symbol}: {e}")
            return None
    
    def get_finnhub_crypto_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Finnhub를 사용한 암호화폐 가격 조회"""
        try:
            url = f"{self.finnhub_base}/crypto/candle"
            params = {
                'symbol': f"BINANCE:{symbol}USDT",
                'resolution': '1',
                'from': int((datetime.now() - timedelta(hours=1)).timestamp()),
                'to': int(datetime.now().timestamp()),
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('s') == 'ok' and data.get('c'):
                return {
                    'symbol': symbol,
                    'price': data['c'][-1],
                    'timestamp': datetime.now().isoformat(),
                    'source': 'finnhub',
                    'market': 'crypto'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Finnhub 암호화폐 가격 조회 오류 {symbol}: {e}")
            return None
    
    def get_finnhub_forex_rate(self, from_currency: str, to_currency: str) -> Optional[Dict[str, Any]]:
        """Finnhub를 사용한 외환 환율 조회"""
        try:
            url = f"{self.finnhub_base}/forex/rates"
            params = {
                'base': from_currency,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            rate = data.get('quote', {}).get(to_currency)
            if rate:
                return {
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'exchange_rate': rate,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'finnhub'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Finnhub 외환 환율 조회 오류 {from_currency}/{to_currency}: {e}")
            return None
    
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Finnhub를 사용한 심볼 검색"""
        try:
            url = f"{self.finnhub_base}/search"
            params = {
                'q': query,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get('result', [])
            
        except Exception as e:
            logger.error(f"심볼 검색 오류 {query}: {e}")
            return []
    
    def get_market_news(self, symbol: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Finnhub를 사용한 시장 뉴스 조회"""
        try:
            url = f"{self.finnhub_base}/news"
            params = {
                'category': 'general',
                'token': self.finnhub_key
            }
            
            if symbol:
                params['symbol'] = symbol
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return data[:limit]
            
            return []
            
        except Exception as e:
            logger.error(f"시장 뉴스 조회 오류: {e}")
            return []
    
    def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Finnhub를 사용한 회사 프로필 조회"""
        try:
            url = f"{self.finnhub_base}/stock/profile2"
            params = {
                'symbol': symbol,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data if data else None
            
        except Exception as e:
            logger.error(f"회사 프로필 조회 오류 {symbol}: {e}")
            return None
    
    def get_enhanced_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """4개 API를 활용한 통합 실시간 데이터"""
        try:
            # 기본 시세 (Finnhub 우선)
            quote_data = self.get_real_time_quote(symbol)
            if not quote_data:
                return None
            
            # 회사 정보 추가
            company_profile = self.get_company_profile(symbol)
            
            # 뉴스 정보 추가
            news = self.get_market_news(symbol, limit=3)
            
            return {
                'quote': quote_data,
                'company': company_profile,
                'recent_news': news,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"통합 실시간 데이터 조회 오류 {symbol}: {e}")
            return None

    # Tiingo API Methods
    def _get_tiingo_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Tiingo API를 사용한 실시간 시세 조회"""
        try:
            if not self.tiingo_key:
                return None
                
            url = f"{self.tiingo_base}/daily/{symbol}/prices"
            headers = {'Authorization': f'Token {self.tiingo_key}'}
            params = {
                'startDate': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'endDate': datetime.now().strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                latest = data[-1]
                return {
                    'symbol': symbol,
                    'price': latest.get('close', 0),
                    'change': latest.get('close', 0) - latest.get('open', 0),
                    'change_percent': ((latest.get('close', 0) - latest.get('open', 0)) / latest.get('open', 1)) * 100,
                    'volume': latest.get('volume', 0),
                    'high': latest.get('high', 0),
                    'low': latest.get('low', 0),
                    'open': latest.get('open', 0),
                    'source': 'tiingo'
                }
            return None
            
        except Exception as e:
            logger.error(f"Tiingo API 오류 {symbol}: {e}")
            return None
    
    def _get_tiingo_historical(self, symbol: str, period: str = '1year') -> Optional[List[Dict[str, Any]]]:
        """Tiingo API를 사용한 히스토리컬 데이터"""
        try:
            if not self.tiingo_key:
                return None
                
            # 기간 설정
            end_date = datetime.now()
            if period == '1day':
                start_date = end_date - timedelta(days=1)
            elif period == '1week':
                start_date = end_date - timedelta(weeks=1)
            elif period == '1month':
                start_date = end_date - timedelta(days=30)
            elif period == '3months':
                start_date = end_date - timedelta(days=90)
            elif period == '6months':
                start_date = end_date - timedelta(days=180)
            else:  # 1year
                start_date = end_date - timedelta(days=365)
            
            url = f"{self.tiingo_base}/daily/{symbol}/prices"
            headers = {'Authorization': f'Token {self.tiingo_key}'}
            params = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return [{
                    'date': item['date'][:10],  # YYYY-MM-DD 형식
                    'open': item.get('open', 0),
                    'high': item.get('high', 0),
                    'low': item.get('low', 0),
                    'close': item.get('close', 0),
                    'volume': item.get('volume', 0)
                } for item in data]
            
            return None
            
        except Exception as e:
            logger.error(f"Tiingo 히스토리컬 데이터 오류 {symbol}: {e}")
            return None
    
    # Marketstack API Methods
    def _get_marketstack_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Marketstack API를 사용한 실시간 시세 조회"""
        try:
            if not self.marketstack_key:
                return None
                
            url = f"{self.marketstack_base}/eod/latest"
            params = {
                'access_key': self.marketstack_key,
                'symbols': symbol,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and 'data' in data and len(data['data']) > 0:
                item = data['data'][0]
                return {
                    'symbol': symbol,
                    'price': item.get('close', 0),
                    'change': item.get('close', 0) - item.get('open', 0),
                    'change_percent': ((item.get('close', 0) - item.get('open', 0)) / item.get('open', 1)) * 100,
                    'volume': item.get('volume', 0),
                    'high': item.get('high', 0),
                    'low': item.get('low', 0),
                    'open': item.get('open', 0),
                    'source': 'marketstack'
                }
            return None
            
        except Exception as e:
            logger.error(f"Marketstack API 오류 {symbol}: {e}")
            return None
    
    def _get_marketstack_historical(self, symbol: str, period: str = '1year') -> Optional[List[Dict[str, Any]]]:
        """Marketstack API를 사용한 히스토리컬 데이터"""
        try:
            if not self.marketstack_key:
                return None
                
            # 기간 설정
            end_date = datetime.now()
            if period == '1day':
                start_date = end_date - timedelta(days=1)
            elif period == '1week':
                start_date = end_date - timedelta(weeks=1)
            elif period == '1month':
                start_date = end_date - timedelta(days=30)
            elif period == '3months':
                start_date = end_date - timedelta(days=90)
            elif period == '6months':
                start_date = end_date - timedelta(days=180)
            else:  # 1year
                start_date = end_date - timedelta(days=365)
            
            url = f"{self.marketstack_base}/eod"
            params = {
                'access_key': self.marketstack_key,
                'symbols': symbol,
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': end_date.strftime('%Y-%m-%d'),
                'limit': 1000
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data and 'data' in data:
                return [{
                    'date': item['date'][:10],  # YYYY-MM-DD 형식
                    'open': item.get('open', 0),
                    'high': item.get('high', 0),
                    'low': item.get('low', 0),
                    'close': item.get('close', 0),
                    'volume': item.get('volume', 0)
                } for item in reversed(data['data'])]  # 날짜 순서대로 정렬
            
            return None
            
        except Exception as e:
            logger.error(f"Marketstack 히스토리컬 데이터 오류 {symbol}: {e}")
            return None

    def _get_alpha_vantage_crypto_historical(self, symbol: str, period: str) -> Optional[List[Dict]]:
        """Alpha Vantage 암호화폐 과거 데이터"""
        try:
            url = self.alpha_vantage_base
            params = {
                'function': 'DIGITAL_CURRENCY_DAILY',
                'symbol': symbol,
                'market': 'USD',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if 'Time Series (Digital Currency Daily)' not in data:
                logger.error(f"Alpha Vantage crypto 데이터 오류: {data}")
                return None
            
            time_series = data['Time Series (Digital Currency Daily)']
            results = []
            
            for date_str, daily_data in time_series.items():
                results.append({
                    'date': date_str,
                    'timestamp': date_str,
                    'open': float(daily_data['1a. open (USD)']),
                    'high': float(daily_data['2a. high (USD)']),
                    'low': float(daily_data['3a. low (USD)']),
                    'close': float(daily_data['4a. close (USD)']),
                    'volume': float(daily_data.get('5. volume', 0))
                })
            
            # Sort by date (newest first, then reverse for oldest first)
            results.sort(key=lambda x: x['date'])
            return results
            
        except Exception as e:
            logger.error(f"Alpha Vantage crypto 과거 데이터 오류 {symbol}: {e}")
            return None

    def get_coingecko_historical_data(self, symbol: str, period: str = '30', vs_currency: str = 'usd') -> Optional[List[Dict[str, Any]]]:
        """CoinGecko API로 암호화폐 히스토리컬 데이터 조회 (무료, API 키 불필요)"""
        try:
            # CoinGecko ID 매핑 - support both symbol and full name
            crypto_id_mapping = {
                'BTC': 'bitcoin',
                'bitcoin': 'bitcoin',
                'ETH': 'ethereum', 
                'ethereum': 'ethereum',
                'ADA': 'cardano',
                'cardano': 'cardano',
                'BNB': 'binancecoin',
                'binancecoin': 'binancecoin',
                'DOT': 'polkadot',
                'polkadot': 'polkadot',
                'MATIC': 'matic-network',
                'matic': 'matic-network',
                'matic-network': 'matic-network',
                'SOL': 'solana',
                'solana': 'solana',
                'LTC': 'litecoin',
                'litecoin': 'litecoin',
                'XRP': 'ripple',
                'ripple': 'ripple',
                'DOGE': 'dogecoin',
                'dogecoin': 'dogecoin',
                'AVAX': 'avalanche-2',
                'avalanche-2': 'avalanche-2',
                'LINK': 'chainlink',
                'chainlink': 'chainlink',
                'UNI': 'uniswap',
                'uniswap': 'uniswap',
                'ATOM': 'cosmos',
                'cosmos': 'cosmos'
            }
            
            # Try both uppercase and lowercase
            coin_id = crypto_id_mapping.get(symbol) or crypto_id_mapping.get(symbol.upper()) or crypto_id_mapping.get(symbol.lower())
            if not coin_id:
                logger.warning(f"CoinGecko: No mapping found for {symbol}")
                return None

            # Convert period to days
            period_map = {
                '1day': '1',
                '1week': '7',
                '1month': '30',
                '3months': '90',
                '6months': '180',
                '1year': '365',
                '2years': '730'
            }
            days = period_map.get(period, period)

            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'interval': 'daily' if int(days) > 30 else 'hourly'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'prices' in data:
                prices = data['prices']
                volumes = data.get('market_caps', [])
                
                historical_data = []
                for i, price_data in enumerate(prices):
                    timestamp, price = price_data
                    date_obj = datetime.fromtimestamp(timestamp / 1000)
                    
                    # Get volume if available
                    volume = 0
                    if i < len(volumes):
                        volume = volumes[i][1] if len(volumes[i]) > 1 else 0
                    
                    # Since CoinGecko only provides price data, we'll estimate OHLC
                    # This is a simplification - for more accurate OHLC data, you'd need a premium API
                    open_price = price * (1 + (0.005 * (0.5 - abs(0.5))))  # Small random variation
                    high_price = price * 1.02  # Approximate 2% higher than close
                    low_price = price * 0.98   # Approximate 2% lower than close
                    
                    historical_data.append({
                        'date': date_obj.strftime('%Y-%m-%d'),
                        'datetime': date_obj.isoformat(),
                        'timestamp': int(timestamp / 1000),
                        'time': int(timestamp / 1000),
                        'open': float(PrecisionHandler.format_price(open_price, symbol, 'crypto')),
                        'high': float(PrecisionHandler.format_price(high_price, symbol, 'crypto')),
                        'low': float(PrecisionHandler.format_price(low_price, symbol, 'crypto')),
                        'close': float(PrecisionHandler.format_price(price, symbol, 'crypto')),
                        'price': float(PrecisionHandler.format_price(price, symbol, 'crypto')),  # Alternative field name
                        'value': float(PrecisionHandler.format_price(price, symbol, 'crypto')),  # Alternative field name
                        'volume': int(volume),
                        'symbol': symbol.upper(),
                        'source': 'coingecko'
                    })
                
                logger.info(f"CoinGecko: Successfully retrieved {len(historical_data)} data points for {symbol}")
                return historical_data
            
            logger.warning(f"CoinGecko: No price data found for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"CoinGecko 히스토리컬 데이터 오류 {symbol}: {e}")
            return None

    def get_coingecko_primary_data(self, symbol: str, period: str = '30', vs_currency: str = 'usd') -> Optional[List[Dict[str, Any]]]:
        """CoinGecko를 주요 소스로 사용하는 데이터 조회"""
        cache_key = f"coingecko_primary_{symbol}_{period}_{vs_currency}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"Returning cached CoinGecko data for {symbol}")
            return cached_data
        
        try:
            # CoinGecko 데이터 조회
            data = self.get_coingecko_historical_data(symbol, period, vs_currency)
            
            if data and len(data) > 0:
                # 캐시에 저장 (10분)
                cache.set(cache_key, data, timeout=600)
                logger.info(f"CoinGecko: Successfully cached {len(data)} data points for {symbol}")
                return data
            
            # CoinGecko 실패 시 다른 API들 시도
            logger.warning(f"CoinGecko failed for {symbol}, trying other APIs...")
            
            fallback_data = self.get_historical_data(symbol, period, '1day', 'crypto')
            if fallback_data:
                cache.set(cache_key, fallback_data, timeout=300)  # 5분 캐시 (짧게)
                return fallback_data
            
            logger.error(f"All APIs failed for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"CoinGecko primary data error for {symbol}: {e}")
            return None


# 전역 인스턴스 - 지연 초기화
_market_service = None

def get_market_service():
    """MarketDataService 인스턴스를 지연 초기화로 반환"""
    global _market_service
    if _market_service is None:
        _market_service = MarketDataService()
    return _market_service
