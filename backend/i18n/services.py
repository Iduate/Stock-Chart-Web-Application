import logging
import requests
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)


class TranslationService:
    """번역 서비스"""
    
    # 지원하는 언어 매핑
    LANGUAGE_MAPPING = {
        'ko': 'ko',
        'en': 'en', 
        'ja': 'ja',
        'zh': 'zh',
        'es': 'es',
        'fr': 'fr',
        'de': 'de',
        'pt': 'pt',
        'ru': 'ru',
        'ar': 'ar'
    }
    
    @classmethod
    def translate_text(cls, text: str, source_language: str = 'auto', target_language: str = 'ko') -> str:
        """
        텍스트 번역
        
        Args:
            text: 번역할 텍스트
            source_language: 원본 언어 코드
            target_language: 대상 언어 코드
            
        Returns:
            번역된 텍스트
        """
        # 캐시 키 생성
        cache_key = f"translation:{hash(text)}:{source_language}:{target_language}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            # Google Translate API 사용 (실제 환경에서는 API 키 필요)
            translated_text = cls._google_translate(text, source_language, target_language)
            
            if not translated_text:
                # Papago API 사용 (백업)
                translated_text = cls._papago_translate(text, source_language, target_language)
            
            if not translated_text:
                # 기본 번역 (단순 매핑)
                translated_text = cls._fallback_translate(text, target_language)
            
            # 결과 캐시 (1시간)
            if translated_text:
                cache.set(cache_key, translated_text, 3600)
                
            return translated_text or text
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text
    
    @classmethod
    def _google_translate(cls, text: str, source: str, target: str) -> Optional[str]:
        """Google Translate API 호출"""
        try:
            api_key = getattr(settings, 'GOOGLE_TRANSLATE_API_KEY', None)
            if not api_key:
                return None
            
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': api_key,
                'q': text,
                'source': source if source != 'auto' else '',
                'target': target,
                'format': 'text'
            }
            
            response = requests.post(url, data=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['data']['translations'][0]['translatedText']
                
        except Exception as e:
            logger.warning(f"Google Translate error: {str(e)}")
            
        return None
    
    @classmethod
    def _papago_translate(cls, text: str, source: str, target: str) -> Optional[str]:
        """Naver Papago API 호출"""
        try:
            client_id = getattr(settings, 'PAPAGO_CLIENT_ID', None)
            client_secret = getattr(settings, 'PAPAGO_CLIENT_SECRET', None)
            
            if not client_id or not client_secret:
                return None
            
            # Papago 언어 코드 매핑
            papago_mapping = {
                'ko': 'ko', 'en': 'en', 'ja': 'ja', 'zh': 'zh-CN',
                'es': 'es', 'fr': 'fr', 'de': 'de', 'pt': 'pt', 'ru': 'ru'
            }
            
            source_lang = papago_mapping.get(source, 'auto')
            target_lang = papago_mapping.get(target, 'ko')
            
            if source_lang == 'auto':
                source_lang = cls._detect_language_simple(text)
                source_lang = papago_mapping.get(source_lang, 'en')
            
            url = "https://openapi.naver.com/v1/papago/n2mt"
            headers = {
                'X-Naver-Client-Id': client_id,
                'X-Naver-Client-Secret': client_secret,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'source': source_lang,
                'target': target_lang,
                'text': text
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['message']['result']['translatedText']
                
        except Exception as e:
            logger.warning(f"Papago translate error: {str(e)}")
            
        return None
    
    @classmethod
    def _fallback_translate(cls, text: str, target_language: str) -> str:
        """기본 번역 (주요 키워드만)"""
        
        # 기본 번역 사전
        translations = {
            'ko': {
                'home': '홈',
                'charts': '차트',
                'prediction': '예측',
                'ranking': '랭킹',
                'events': '이벤트',
                'subscription': '구독',
                'login': '로그인',
                'register': '회원가입',
                'logout': '로그아웃',
                'profile': '프로필',
                'settings': '설정',
                'search': '검색',
                'buy': '구매',
                'sell': '판매',
                'price': '가격',
                'volume': '거래량',
                'high': '최고가',
                'low': '최저가',
                'open': '시가',
                'close': '종가',
                'change': '변화',
                'percent': '퍼센트',
                'market': '시장',
                'stock': '주식',
                'crypto': '암호화폐',
                'currency': '통화',
                'news': '뉴스',
                'analysis': '분석',
                'portfolio': '포트폴리오',
                'watchlist': '관심목록',
                'alert': '알림',
                'notification': '알림',
                'email': '이메일',
                'password': '비밀번호',
                'confirm': '확인',
                'cancel': '취소',
                'save': '저장',
                'delete': '삭제',
                'edit': '편집',
                'view': '보기',
                'add': '추가',
                'remove': '제거',
                'yes': '예',
                'no': '아니오',
                'ok': '확인',
                'error': '오류',
                'success': '성공',
                'warning': '경고',
                'info': '정보',
                'loading': '로딩중',
                'please_wait': '잠시만 기다려주세요',
                'try_again': '다시 시도',
                'contact_support': '지원팀 문의'
            },
            'en': {
                '홈': 'Home',
                '차트': 'Charts',
                '예측': 'Prediction',
                '랭킹': 'Ranking',
                '이벤트': 'Events',
                '구독': 'Subscription',
                '로그인': 'Login',
                '회원가입': 'Register',
                '로그아웃': 'Logout',
                '프로필': 'Profile',
                '설정': 'Settings',
                '검색': 'Search',
                '구매': 'Buy',
                '판매': 'Sell',
                '가격': 'Price',
                '거래량': 'Volume',
                '최고가': 'High',
                '최저가': 'Low',
                '시가': 'Open',
                '종가': 'Close',
                '변화': 'Change',
                '퍼센트': 'Percent',
                '시장': 'Market',
                '주식': 'Stock',
                '암호화폐': 'Cryptocurrency',
                '통화': 'Currency',
                '뉴스': 'News',
                '분석': 'Analysis',
                '포트폴리오': 'Portfolio',
                '관심목록': 'Watchlist',
                '알림': 'Alert',
                '이메일': 'Email',
                '비밀번호': 'Password',
                '확인': 'Confirm',
                '취소': 'Cancel',
                '저장': 'Save',
                '삭제': 'Delete',
                '편집': 'Edit',
                '보기': 'View',
                '추가': 'Add',
                '제거': 'Remove',
                '예': 'Yes',
                '아니오': 'No',
                '오류': 'Error',
                '성공': 'Success',
                '경고': 'Warning',
                '정보': 'Info',
                '로딩중': 'Loading',
                '잠시만 기다려주세요': 'Please wait',
                '다시 시도': 'Try again',
                '지원팀 문의': 'Contact Support'
            },
            'ja': {
                'home': 'ホーム',
                'charts': 'チャート',
                'prediction': '予測',
                'ranking': 'ランキング',
                'events': 'イベント',
                'subscription': '購読',
                'login': 'ログイン',
                'register': '登録',
                'logout': 'ログアウト',
                'price': '価格',
                'market': '市場',
                'stock': '株式',
                'crypto': '暗号通貨'
            },
            'zh': {
                'home': '首页',
                'charts': '图表',
                'prediction': '预测',
                'ranking': '排名',
                'events': '活动',
                'subscription': '订阅',
                'login': '登录',
                'register': '注册',
                'logout': '退出',
                'price': '价格',
                'market': '市场',
                'stock': '股票',
                'crypto': '加密货币'
            }
        }
        
        target_dict = translations.get(target_language, {})
        if not target_dict:
            return text
        
        # 단어 단위로 번역 시도
        translated_words = []
        words = text.split()
        
        for word in words:
            translated_word = target_dict.get(word.lower(), word)
            translated_words.append(translated_word)
        
        return ' '.join(translated_words)
    
    @classmethod
    def _detect_language_simple(cls, text: str) -> str:
        """간단한 언어 감지"""
        # 한글 감지
        if re.search(r'[가-힣]', text):
            return 'ko'
        # 일본어 감지
        elif re.search(r'[ひらがなカタカナ]', text):
            return 'ja'
        # 중국어 감지
        elif re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        # 아랍어 감지
        elif re.search(r'[\u0600-\u06ff]', text):
            return 'ar'
        # 기본값은 영어
        else:
            return 'en'


class LanguageDetectionService:
    """언어 감지 서비스"""
    
    @classmethod
    def detect_language(cls, text: str) -> Optional[str]:
        """
        텍스트의 언어 감지
        
        Args:
            text: 감지할 텍스트
            
        Returns:
            감지된 언어 코드
        """
        # 캐시 확인
        cache_key = f"language_detection:{hash(text)}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            # Google Translate API로 언어 감지
            detected_language = cls._google_detect(text)
            
            if not detected_language:
                # 패턴 기반 감지 (백업)
                detected_language = cls._pattern_detect(text)
            
            # 결과 캐시 (1시간)
            if detected_language:
                cache.set(cache_key, detected_language, 3600)
                
            return detected_language
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return None
    
    @classmethod
    def _google_detect(cls, text: str) -> Optional[str]:
        """Google Translate API로 언어 감지"""
        try:
            api_key = getattr(settings, 'GOOGLE_TRANSLATE_API_KEY', None)
            if not api_key:
                return None
            
            url = "https://translation.googleapis.com/language/translate/v2/detect"
            params = {
                'key': api_key,
                'q': text
            }
            
            response = requests.post(url, data=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['data']['detections'][0][0]['language']
                
        except Exception as e:
            logger.warning(f"Google language detection error: {str(e)}")
            
        return None
    
    @classmethod
    def _pattern_detect(cls, text: str) -> Optional[str]:
        """패턴 기반 언어 감지"""
        text_sample = text[:200]  # 처음 200자만 분석
        
        # 각 언어별 문자 개수 계산
        language_scores = {
            'ko': len(re.findall(r'[가-힣]', text_sample)),
            'ja': len(re.findall(r'[ひらがなカタカナ]', text_sample)),
            'zh': len(re.findall(r'[\u4e00-\u9fff]', text_sample)),
            'ar': len(re.findall(r'[\u0600-\u06ff]', text_sample)),
            'ru': len(re.findall(r'[а-яё]', text_sample, re.IGNORECASE)),
            'en': len(re.findall(r'[a-zA-Z]', text_sample))
        }
        
        # 가장 높은 점수의 언어 반환
        max_score = max(language_scores.values())
        if max_score > 0:
            for lang, score in language_scores.items():
                if score == max_score:
                    return lang
        
        return 'en'  # 기본값


class CurrencyService:
    """통화 변환 서비스"""
    
    SUPPORTED_CURRENCIES = {
        'KRW': {'symbol': '₩', 'name': '원', 'locale': 'ko-KR'},
        'USD': {'symbol': '$', 'name': 'Dollar', 'locale': 'en-US'},
        'JPY': {'symbol': '¥', 'name': 'Yen', 'locale': 'ja-JP'},
        'CNY': {'symbol': '¥', 'name': 'Yuan', 'locale': 'zh-CN'},
        'EUR': {'symbol': '€', 'name': 'Euro', 'locale': 'en-EU'},
        'GBP': {'symbol': '£', 'name': 'Pound', 'locale': 'en-GB'}
    }
    
    @classmethod
    def format_currency(cls, amount: float, currency: str = 'KRW', language: str = 'ko') -> str:
        """
        통화 형식 포매팅
        
        Args:
            amount: 금액
            currency: 통화 코드
            language: 언어 코드
            
        Returns:
            포매팅된 통화 문자열
        """
        currency_info = cls.SUPPORTED_CURRENCIES.get(currency, cls.SUPPORTED_CURRENCIES['KRW'])
        symbol = currency_info['symbol']
        
        # 언어별 숫자 포매팅
        if language == 'ko':
            if currency == 'KRW':
                if amount >= 100000000:  # 1억 이상
                    return f"{amount/100000000:.1f}억원"
                elif amount >= 10000:  # 1만 이상
                    return f"{amount/10000:.0f}만원"
                else:
                    return f"{symbol}{amount:,.0f}"
            else:
                return f"{symbol}{amount:,.2f}"
        else:
            return f"{symbol}{amount:,.2f}"
    
    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Optional[float]:
        """
        환율 조회
        
        Args:
            from_currency: 원본 통화
            to_currency: 대상 통화
            
        Returns:
            환율
        """
        cache_key = f"exchange_rate:{from_currency}:{to_currency}"
        cached_rate = cache.get(cache_key)
        
        if cached_rate:
            return cached_rate
        
        try:
            # 무료 환율 API 사용 (예: exchangerate-api.com)
            api_key = getattr(settings, 'EXCHANGE_RATE_API_KEY', None)
            if api_key:
                url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    rate = data.get('conversion_rate')
                    
                    if rate:
                        # 30분 캐시
                        cache.set(cache_key, rate, 1800)
                        return rate
            
            # 기본 환율 (실제로는 정확한 API 사용 필요)
            default_rates = {
                ('USD', 'KRW'): 1300.0,
                ('KRW', 'USD'): 1/1300.0,
                ('JPY', 'KRW'): 9.0,
                ('KRW', 'JPY'): 1/9.0,
                ('EUR', 'KRW'): 1400.0,
                ('KRW', 'EUR'): 1/1400.0,
            }
            
            return default_rates.get((from_currency, to_currency), 1.0)
            
        except Exception as e:
            logger.error(f"Exchange rate error: {str(e)}")
            return 1.0
