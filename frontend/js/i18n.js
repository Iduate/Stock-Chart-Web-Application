/**
 * StockChart 다국어 지원 클라이언트 라이브러리
 * 
 * 사용법:
 * 1. 페이지 로드 시 I18n.init() 호출
 * 2. 번역: I18n.t('key') 또는 I18n.translate('key')
 * 3. 언어 변경: I18n.setLanguage('en')
 * 4. 자동 번역: I18n.translatePage()
 */

class I18nManager {
    constructor() {
        this.currentLanguage = 'ko';
        this.translations = {};
        this.cache = new Map();
        this.observers = [];
        this.isInitialized = false;

        // 지원 언어 정보
        this.supportedLanguages = {
            'ko': { name: '한국어', flag: '🇰🇷', rtl: false },
            'en': { name: 'English', flag: '🇺🇸', rtl: false },
            'ja': { name: '日本語', flag: '🇯🇵', rtl: false },
            'zh': { name: '中文', flag: '🇨🇳', rtl: false },
            'es': { name: 'Español', flag: '🇪🇸', rtl: false },
            'fr': { name: 'Français', flag: '🇫🇷', rtl: false },
            'de': { name: 'Deutsch', flag: '🇩🇪', rtl: false },
            'pt': { name: 'Português', flag: '🇧🇷', rtl: false },
            'ru': { name: 'Русский', flag: '🇷🇺', rtl: false },
            'ar': { name: 'العربية', flag: '🇸🇦', rtl: true }
        };

        this.bindEvents();
    }

    /**
     * 다국어 시스템 초기화
     */
    async init(language = null) {
        try {
            // 사용자 언어 설정 로드
            await this.loadUserPreference();

            // 언어 설정 (우선순위: 매개변수 > 사용자 설정 > 브라우저 언어 > 기본값)
            const targetLanguage = language ||
                this.getUserLanguage() ||
                this.getBrowserLanguage() ||
                'ko';

            await this.setLanguage(targetLanguage);

            // 페이지 번역 적용
            this.translatePage();

            // 언어 선택기 초기화
            this.initLanguageSelector();

            this.isInitialized = true;
            console.log(`I18n initialized with language: ${this.currentLanguage}`);

        } catch (error) {
            console.error('I18n initialization failed:', error);
            this.currentLanguage = 'ko';
        }
    }

    /**
     * 언어 변경
     */
    async setLanguage(language) {
        if (!this.supportedLanguages[language]) {
            console.warn(`Unsupported language: ${language}`);
            return;
        }

        this.currentLanguage = language;

        // 번역 데이터 로드
        await this.loadTranslations(language);

        // HTML 언어 속성 변경
        document.documentElement.lang = language;

        // RTL 언어 처리
        if (this.supportedLanguages[language].rtl) {
            document.documentElement.dir = 'rtl';
            document.body.classList.add('rtl');
        } else {
            document.documentElement.dir = 'ltr';
            document.body.classList.remove('rtl');
        }

        // 사용자 설정 저장
        await this.saveUserPreference(language);

        // 페이지 재번역
        this.translatePage();

        // 언어 변경 이벤트 발생
        this.notifyLanguageChange(language);

        console.log(`Language changed to: ${language}`);
    }

    /**
     * 번역 데이터 로드
     */
    async loadTranslations(language) {
        const cacheKey = `translations_${language}`;

        // 캐시 확인
        if (this.cache.has(cacheKey)) {
            this.translations = this.cache.get(cacheKey);
            return;
        }

        try {
            const response = await fetch(`/api/i18n/api/translations/by_language/?language=${language}`, {
                headers: {
                    'Accept': 'application/json',
                    'Authorization': this.getAuthHeader()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.translations = data.translations || {};

            // 캐시 저장 (10분)
            this.cache.set(cacheKey, this.translations);
            setTimeout(() => this.cache.delete(cacheKey), 10 * 60 * 1000);

        } catch (error) {
            console.error(`Failed to load translations for ${language}:`, error);

            // 기본 번역 데이터 사용
            this.translations = this.getFallbackTranslations(language);
        }
    }

    /**
     * 번역 함수
     */
    translate(key, params = {}) {
        return this.t(key, params);
    }

    /**
     * 번역 함수 (축약형)
     */
    t(key, params = {}) {
        let translation = this.translations[key] || key;

        // 매개변수 치환
        Object.keys(params).forEach(param => {
            translation = translation.replace(new RegExp(`{{${param}}}`, 'g'), params[param]);
        });

        return translation;
    }

    /**
     * 페이지 전체 번역 적용
     */
    translatePage() {
        // data-i18n 속성을 가진 요소들 번역
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const params = this.parseParams(element.getAttribute('data-i18n-params'));

            if (element.tagName === 'INPUT' && (element.type === 'text' || element.type === 'email' || element.type === 'password')) {
                element.placeholder = this.t(key, params);
            } else {
                element.textContent = this.t(key, params);
            }
        });

        // data-i18n-title 속성을 가진 요소들의 title 번역
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });

        // data-i18n-placeholder 속성을 가진 요소들의 placeholder 번역
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key);
        });
    }

    /**
     * 언어 선택기 초기화
     */
    initLanguageSelector() {
        const selector = document.getElementById('languageSelector');
        if (!selector) return;

        // 현재 언어 표시
        this.updateLanguageSelector(selector);

        // 언어 옵션 생성
        if (!selector.querySelector('.language-options')) {
            this.createLanguageOptions(selector);
        }
    }

    /**
     * 언어 선택기 업데이트
     */
    updateLanguageSelector(selector) {
        const currentLang = this.supportedLanguages[this.currentLanguage];
        const button = selector.querySelector('.language-button');

        if (button) {
            button.innerHTML = `
                <span class="flag">${currentLang.flag}</span>
                <span class="name">${currentLang.name}</span>
                <i class="fas fa-chevron-down"></i>
            `;
        }
    }

    /**
     * 언어 옵션 생성
     */
    createLanguageOptions(selector) {
        const options = document.createElement('div');
        options.className = 'language-options hidden';

        Object.entries(this.supportedLanguages).forEach(([code, info]) => {
            const option = document.createElement('div');
            option.className = 'language-option';
            option.innerHTML = `
                <span class="flag">${info.flag}</span>
                <span class="name">${info.name}</span>
            `;

            option.addEventListener('click', () => {
                this.setLanguage(code);
                options.classList.add('hidden');
            });

            options.appendChild(option);
        });

        selector.appendChild(options);

        // 토글 기능
        const button = selector.querySelector('.language-button');
        if (button) {
            button.addEventListener('click', () => {
                options.classList.toggle('hidden');
            });
        }

        // 외부 클릭 시 닫기
        document.addEventListener('click', (e) => {
            if (!selector.contains(e.target)) {
                options.classList.add('hidden');
            }
        });
    }

    /**
     * 숫자 포맷 (지역별)
     */
    formatNumber(number, options = {}) {
        const locale = this.getLocale(this.currentLanguage);
        return new Intl.NumberFormat(locale, options).format(number);
    }

    /**
     * 통화 포맷
     */
    formatCurrency(amount, currency = 'KRW') {
        const locale = this.getLocale(this.currentLanguage);
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    /**
     * 날짜 포맷
     */
    formatDate(date, options = {}) {
        const locale = this.getLocale(this.currentLanguage);
        return new Intl.DateTimeFormat(locale, options).format(new Date(date));
    }

    /**
     * 상대적 시간 포맷 (예: "2시간 전")
     */
    formatRelativeTime(date) {
        const locale = this.getLocale(this.currentLanguage);
        const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

        const now = new Date();
        const target = new Date(date);
        const diffMs = target.getTime() - now.getTime();
        const diffMins = Math.round(diffMs / (1000 * 60));
        const diffHours = Math.round(diffMs / (1000 * 60 * 60));
        const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

        if (Math.abs(diffMins) < 60) {
            return rtf.format(diffMins, 'minute');
        } else if (Math.abs(diffHours) < 24) {
            return rtf.format(diffHours, 'hour');
        } else {
            return rtf.format(diffDays, 'day');
        }
    }

    /**
     * 언어 변경 관찰자 등록
     */
    onLanguageChange(callback) {
        this.observers.push(callback);
    }

    /**
     * 언어 변경 알림
     */
    notifyLanguageChange(language) {
        this.observers.forEach(callback => {
            try {
                callback(language);
            } catch (error) {
                console.error('Language change observer error:', error);
            }
        });
    }

    /**
     * 사용자 언어 설정 로드
     */
    async loadUserPreference() {
        try {
            const response = await fetch('/api/i18n/api/user/language-preference/', {
                headers: {
                    'Authorization': this.getAuthHeader()
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.language_code;
            }
        } catch (error) {
            console.log('Failed to load user language preference:', error);
        }

        return null;
    }

    /**
     * 사용자 언어 설정 저장
     */
    async saveUserPreference(language) {
        try {
            await fetch('/api/i18n/api/user/language-preference/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': this.getAuthHeader(),
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    language_code: language
                })
            });
        } catch (error) {
            console.log('Failed to save user language preference:', error);
        }
    }

    /**
     * 유틸리티 함수들
     */
    getUserLanguage() {
        return localStorage.getItem('preferred_language');
    }

    getBrowserLanguage() {
        const lang = navigator.language || navigator.languages[0];
        return lang ? lang.split('-')[0] : null;
    }

    getLocale(language) {
        const localeMap = {
            'ko': 'ko-KR',
            'en': 'en-US',
            'ja': 'ja-JP',
            'zh': 'zh-CN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'pt': 'pt-BR',
            'ru': 'ru-RU',
            'ar': 'ar-SA'
        };

        return localeMap[language] || 'en-US';
    }

    parseParams(paramsStr) {
        if (!paramsStr) return {};

        try {
            return JSON.parse(paramsStr);
        } catch {
            return {};
        }
    }

    getAuthHeader() {
        const token = localStorage.getItem('access_token');
        return token ? `Bearer ${token}` : '';
    }

    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    bindEvents() {
        // 페이지 로드 완료 시 자동 초기화
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * 기본 번역 데이터 (API 실패 시 사용)
     */
    getFallbackTranslations(language) {
        const fallbackData = {
            'ko': {
                'nav.home': '홈',
                'nav.charts': '차트',
                'nav.prediction': '예측하기',
                'nav.ranking': '랭킹',
                'nav.events': '이벤트',
                'nav.subscription': '구독',
                'nav.partners': '홍보파트너',
                'btn.login': '로그인',
                'btn.register': '회원가입',
                'btn.logout': '로그아웃',
                'msg.loading': '로딩중...'
            },
            'en': {
                'nav.home': 'Home',
                'nav.charts': 'Charts',
                'nav.prediction': 'Prediction',
                'nav.ranking': 'Ranking',
                'nav.events': 'Events',
                'nav.subscription': 'Subscription',
                'nav.partners': 'Partners',
                'btn.login': 'Login',
                'btn.register': 'Sign Up',
                'btn.logout': 'Logout',
                'msg.loading': 'Loading...'
            },
            'ja': {
                'nav.home': 'ホーム',
                'nav.charts': 'チャート',
                'nav.prediction': '予測',
                'nav.ranking': 'ランキング',
                'nav.events': 'イベント',
                'nav.subscription': '購読',
                'nav.partners': 'パートナー',
                'btn.login': 'ログイン',
                'btn.register': '登録',
                'btn.logout': 'ログアウト',
                'msg.loading': '読み込み中...'
            },
            'zh': {
                'nav.home': '首页',
                'nav.charts': '图表',
                'nav.prediction': '预测',
                'nav.ranking': '排名',
                'nav.events': '活动',
                'nav.subscription': '订阅',
                'nav.partners': '合作伙伴',
                'btn.login': '登录',
                'btn.register': '注册',
                'btn.logout': '退出',
                'msg.loading': '加载中...'
            }
        };

        return fallbackData[language] || fallbackData['en'] || {};
    }
}

// 전역 인스턴스 생성
const I18n = new I18nManager();

// 전역 함수로 노출
window.I18n = I18n;
window.t = I18n.t.bind(I18n);
window.translate = I18n.translate.bind(I18n);

// 모듈 방식 지원
if (typeof module !== 'undefined' && module.exports) {
    module.exports = I18n;
}
