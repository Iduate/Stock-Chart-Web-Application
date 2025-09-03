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
        
        # 모든 API 실패 시 샘플 데이터 반환
        logger.warning(f"All APIs failed for quote {symbol}, returning sample data")
        return self._get_sample_stock_data(symbol)
    
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
        """과거 데이터 조회 - 여러 API 사용"""
        cache_key = f"historical_{market}_{symbol}_{period}_{interval}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # 1순위: Alpha Vantage
            data = self._get_alpha_vantage_historical(symbol, period, interval)
            if data:
                cache.set(cache_key, data, timeout=1800)  # 30분 캐시
                return data
            
            # 2순위: Twelve Data
            data = self._get_twelve_data_historical(symbol, period, interval)
            if data:
                cache.set(cache_key, data, timeout=1800)
                return data
            
            # 3순위: Tiingo
            data = self._get_tiingo_historical(symbol, period)
            if data:
                cache.set(cache_key, data, timeout=1800)
                return data
            
            # 4순위: Marketstack
            data = self._get_marketstack_historical(symbol, period)
            if data:
                cache.set(cache_key, data, timeout=1800)
                return data
            
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
            # CoinGecko ID 매핑
            crypto_id_mapping = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum', 
                'ADA': 'cardano',
                'BNB': 'binancecoin',
                'DOT': 'polkadot',
                'MATIC': 'matic-network',
                'SOL': 'solana',
                'LTC': 'litecoin',
                'XRP': 'ripple',
                'DOGE': 'dogecoin',
                'AVAX': 'avalanche-2',
                'LINK': 'chainlink',
                'UNI': 'uniswap',
                'ATOM': 'cosmos'
            }
            
            coin_id = crypto_id_mapping.get(symbol.upper())
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
        """주요 시장 지수 조회 - CoinGecko Global Market Data 사용"""
        cache_key = "market_indices"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # CoinGecko Global Market Data API 사용
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                global_data = response.json()
                
                # 글로벌 마켓 데이터에서 주요 지표 추출
                data = global_data.get('data', {})
                
                # 주요 시장 지수 형태로 변환
                results = [
                    {
                        'symbol': 'TOTAL_MARKET_CAP',
                        'name': 'Total Market Cap',
                        'price': data.get('total_market_cap', {}).get('usd', 0),
                        'change_24h': data.get('market_cap_change_percentage_24h_usd', 0),
                        'type': 'market_cap'
                    },
                    {
                        'symbol': 'TOTAL_VOLUME',
                        'name': 'Total Volume (24h)',
                        'price': data.get('total_volume', {}).get('usd', 0),
                        'change_24h': 0,  # Volume doesn't have change percentage
                        'type': 'volume'
                    },
                    {
                        'symbol': 'BTC_DOMINANCE',
                        'name': 'Bitcoin Dominance',
                        'price': data.get('market_cap_percentage', {}).get('btc', 0),
                        'change_24h': 0,
                        'type': 'dominance'
                    },
                    {
                        'symbol': 'ETH_DOMINANCE',
                        'name': 'Ethereum Dominance', 
                        'price': data.get('market_cap_percentage', {}).get('eth', 0),
                        'change_24h': 0,
                        'type': 'dominance'
                    },
                    {
                        'symbol': 'ACTIVE_CRYPTOS',
                        'name': 'Active Cryptocurrencies',
                        'price': data.get('active_cryptocurrencies', 0),
                        'change_24h': 0,
                        'type': 'count'
                    },
                    {
                        'symbol': 'MARKETS',
                        'name': 'Active Markets',
                        'price': data.get('markets', 0),
                        'change_24h': 0,
                        'type': 'count'
                    }
                ]
                
                logger.info("Successfully got market indices from CoinGecko")
                cache.set(cache_key, results, timeout=300)  # 5분 캐시
                return results
            
            else:
                logger.error(f"CoinGecko global data API error: {response.status_code}")
                return self._get_fallback_market_indices()
                
        except Exception as e:
            logger.error(f"시장 지수 조회 오류: {e}")
            return self._get_fallback_market_indices()
    
    def _get_fallback_market_indices(self) -> List[Dict[str, Any]]:
        """CoinGecko 실패시 대체 마켓 지수 데이터"""
        return [
            {
                'symbol': 'SPY',
                'name': 'SPDR S&P 500 ETF',
                'price': 445.50,
                'change_24h': 0.75,
                'type': 'etf'
            },
            {
                'symbol': 'QQQ',
                'name': 'Invesco QQQ ETF',
                'price': 375.20,
                'change_24h': 1.25,
                'type': 'etf'
            },
            {
                'symbol': 'IWM',
                'name': 'iShares Russell 2000 ETF',
                'price': 195.80,
                'change_24h': -0.45,
                'type': 'etf'
            },
            {
                'symbol': 'DIA',
                'name': 'SPDR Dow Jones ETF',
                'price': 355.75,
                'change_24h': 0.35,
                'type': 'etf'
            },
            {
                'symbol': 'VTI',
                'name': 'Vanguard Total Stock Market ETF',
                'price': 245.90,
                'change_24h': 0.65,
                'type': 'etf'
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
        """Alpha Vantage 과거 데이터"""
        try:
            function_map = {
                '1day': 'TIME_SERIES_DAILY',
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
            
            return sorted(results, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Alpha Vantage 과거 데이터 오류 {symbol}: {e}")
            return None
    
    def _get_twelve_data_historical(self, symbol: str, period: str, interval: str) -> Optional[List[Dict]]:
        """Twelve Data 과거 데이터"""
        try:
            url = f"{self.twelve_data_base}/time_series"
            params = {
                'symbol': symbol,
                'interval': interval,
                'outputsize': '5000',
                'apikey': self.twelve_data_key
            }
            
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


# 전역 인스턴스 - 지연 초기화
_market_service = None

def get_market_service():
    """MarketDataService 인스턴스를 지연 초기화로 반환"""
    global _market_service
    if _market_service is None:
        _market_service = MarketDataService()
    return _market_service
