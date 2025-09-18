/**
 * 국제 결제 시스템 JavaScript 라이브러리
 * Stripe, PayPal, Crypto 결제 지원
 */

class InternationalPayments {
    constructor() {
        this.apiBase = '/api/payments';
        this.currentPayment = null;
        this.providers = {
            stripe: null,
            paypal: null,
            crypto: null
        };

        // 지원 통화 목록
        this.supportedCurrencies = {
            'USD': { symbol: '$', name: 'US Dollar' },
            'EUR': { symbol: '€', name: 'Euro' },
            'GBP': { symbol: '£', name: 'British Pound' },
            'JPY': { symbol: '¥', name: 'Japanese Yen' },
            'KRW': { symbol: '₩', name: 'Korean Won' }
        };

        this.init();
    }

    init() {
        this.loadProviders();
        this.bindEvents();
        this.loadExchangeRates();
    }

    /**
     * 결제 제공업체 초기화
     */
    async loadProviders() {
        // Stripe 초기화
        if (typeof Stripe !== 'undefined') {
            try {
                this.providers.stripe = Stripe(window.STRIPE_PUBLISHABLE_KEY || 'pk_test_...');
            } catch (error) {
                console.warn('Stripe initialization failed:', error);
            }
        }

        // PayPal 초기화
        if (typeof paypal !== 'undefined') {
            try {
                this.providers.paypal = paypal;
            } catch (error) {
                console.warn('PayPal initialization failed:', error);
            }
        }
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 통화 선택 이벤트
        document.addEventListener('change', (e) => {
            if (e.target.matches('.currency-selector')) {
                this.handleCurrencyChange(e.target);
            }
        });

        // 결제 제공업체 선택 이벤트
        document.addEventListener('change', (e) => {
            if (e.target.matches('input[name="internationalProvider"]')) {
                this.handleProviderChange(e.target.value);
            }
        });

        // 국제 결제 버튼 이벤트
        document.addEventListener('click', (e) => {
            if (e.target.matches('.international-payment-btn')) {
                e.preventDefault();
                this.initiatePayment(e.target);
            }
        });
    }

    /**
     * 환율 정보 로드
     */
    async loadExchangeRates() {
        try {
            const response = await fetch(`${this.apiBase}/exchange-rates/current_rates/?base=KRW&targets=USD,EUR,GBP,JPY`);
            const data = await response.json();

            this.exchangeRates = data.rates;
            this.updateCurrencyDisplay();

        } catch (error) {
            console.error('Failed to load exchange rates:', error);
            // 기본 환율 사용
            this.exchangeRates = {
                'USD': { rate: 0.00075 },
                'EUR': { rate: 0.00068 },
                'GBP': { rate: 0.00059 },
                'JPY': { rate: 0.1 }
            };
        }
    }

    /**
     * 통화 변경 처리
     */
    handleCurrencyChange(selector) {
        const currency = selector.value;
        const amount = this.getCurrentAmount();

        if (amount && this.exchangeRates[currency]) {
            const convertedAmount = amount * this.exchangeRates[currency].rate;
            this.updateAmountDisplay(convertedAmount, currency);
        }
    }

    /**
     * 결제 제공업체 변경 처리
     */
    handleProviderChange(provider) {
        this.currentProvider = provider;
        this.updatePaymentMethodsDisplay(provider);
    }

    /**
     * 결제 시작
     */
    async initiatePayment(button) {
        const paymentData = this.gatherPaymentData(button);

        if (!this.validatePaymentData(paymentData)) {
            return;
        }

        this.showLoadingState(true);

        try {
            // 서버에 결제 생성 요청
            const response = await fetch(`${this.apiBase}/international/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(paymentData)
            });

            const result = await response.json();

            if (response.ok) {
                this.currentPayment = result;
                await this.processPayment(paymentData.provider, result);
            } else {
                throw new Error(result.error || '결제 생성 실패');
            }

        } catch (error) {
            console.error('Payment initiation error:', error);
            this.showError('결제 시작 중 오류가 발생했습니다: ' + error.message);
        } finally {
            this.showLoadingState(false);
        }
    }

    /**
     * 제공업체별 결제 처리
     */
    async processPayment(provider, paymentData) {
        switch (provider) {
            case 'stripe':
                return await this.processStripePayment(paymentData);
            case 'paypal':
                return await this.processPayPalPayment(paymentData);
            case 'crypto':
                return await this.processCryptoPayment(paymentData);
            default:
                throw new Error('지원하지 않는 결제 제공업체입니다.');
        }
    }

    /**
     * Stripe 결제 처리
     */
    async processStripePayment(paymentData) {
        if (!this.providers.stripe) {
            throw new Error('Stripe가 초기화되지 않았습니다.');
        }

        try {
            const elements = this.providers.stripe.elements();
            const cardElement = elements.create('card', {
                style: {
                    base: {
                        fontSize: '16px',
                        color: '#424770',
                        '::placeholder': {
                            color: '#aab7c4',
                        },
                    },
                },
            });

            // 카드 요소가 이미 마운트되어 있지 않은 경우 마운트
            const cardContainer = document.getElementById('stripe-card-element');
            if (cardContainer && !cardContainer.hasChildNodes()) {
                cardElement.mount('#stripe-card-element');
            }

            const { error, paymentIntent } = await this.providers.stripe.confirmCardPayment(
                paymentData.client_secret,
                {
                    payment_method: {
                        card: cardElement,
                        billing_details: {
                            name: paymentData.buyer_name,
                            email: paymentData.buyer_email,
                        },
                    }
                }
            );

            if (error) {
                throw new Error(error.message);
            } else {
                // 결제 성공
                await this.verifyPayment(paymentData.id);
                this.showSuccess('결제가 성공적으로 완료되었습니다!');
                this.redirectToSuccess();
            }

        } catch (error) {
            console.error('Stripe payment error:', error);
            throw error;
        }
    }

    /**
     * PayPal 결제 처리
     */
    async processPayPalPayment(paymentData) {
        if (!this.providers.paypal) {
            throw new Error('PayPal이 초기화되지 않았습니다.');
        }

        try {
            // PayPal 결제 페이지로 리다이렉트
            if (paymentData.payment_url) {
                window.location.href = paymentData.payment_url;
            } else {
                throw new Error('PayPal 결제 URL을 찾을 수 없습니다.');
            }

        } catch (error) {
            console.error('PayPal payment error:', error);
            throw error;
        }
    }

    /**
     * 암호화폐 결제 처리
     */
    async processCryptoPayment(paymentData) {
        try {
            // 암호화폐 결제 페이지로 리다이렉트
            if (paymentData.payment_url) {
                window.location.href = paymentData.payment_url;
            } else {
                throw new Error('암호화폐 결제 URL을 찾을 수 없습니다.');
            }

        } catch (error) {
            console.error('Crypto payment error:', error);
            throw error;
        }
    }

    /**
     * 결제 검증
     */
    async verifyPayment(paymentId) {
        try {
            const response = await fetch(`${this.apiBase}/international/${paymentId}/verify/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || '결제 검증 실패');
            }

            return result;

        } catch (error) {
            console.error('Payment verification error:', error);
            throw error;
        }
    }

    /**
     * 결제 데이터 수집
     */
    gatherPaymentData(button) {
        const form = button.closest('form') || document;

        return {
            provider: form.querySelector('input[name="internationalProvider"]:checked')?.value,
            amount: parseInt(form.querySelector('#paymentAmount')?.textContent.replace(/[^\d]/g, '') || '0'),
            currency: form.querySelector('.currency-selector')?.value || 'USD',
            product_name: form.querySelector('#productName')?.value || '구독 서비스',
            product_description: form.querySelector('#productDescription')?.value || '',
            buyer_name: form.querySelector('#buyerName')?.value || '',
            buyer_email: form.querySelector('#buyerEmail')?.value || '',
            country: form.querySelector('#buyerCountry')?.value || '',
            success_url: `${window.location.origin}/payment-success.html`,
            cancel_url: `${window.location.origin}/payment-cancel.html`,
            metadata: {
                source: 'web',
                user_agent: navigator.userAgent
            }
        };
    }

    /**
     * 결제 데이터 유효성 검사
     */
    validatePaymentData(data) {
        const errors = [];

        if (!data.provider) {
            errors.push('결제 제공업체를 선택해주세요.');
        }

        if (!data.amount || data.amount < 1000) {
            errors.push('최소 결제 금액은 1,000원입니다.');
        }

        if (!data.buyer_name) {
            errors.push('구매자 이름을 입력해주세요.');
        }

        if (!data.buyer_email || !this.isValidEmail(data.buyer_email)) {
            errors.push('유효한 이메일 주소를 입력해주세요.');
        }

        if (errors.length > 0) {
            this.showError(errors.join('\n'));
            return false;
        }

        return true;
    }

    /**
     * 현재 금액 가져오기
     */
    getCurrentAmount() {
        const amountText = document.getElementById('originalAmount')?.textContent || '0';
        return parseInt(amountText.replace(/[^\d]/g, ''));
    }

    /**
     * 금액 표시 업데이트
     */
    updateAmountDisplay(amount, currency) {
        const currencyInfo = this.supportedCurrencies[currency];
        if (!currencyInfo) return;

        const formatted = this.formatCurrency(amount, currency);

        const displayElement = document.getElementById('convertedAmount');
        if (displayElement) {
            displayElement.textContent = formatted;
        }
    }

    /**
     * 통화 표시 업데이트
     */
    updateCurrencyDisplay() {
        document.querySelectorAll('.currency-rate').forEach(element => {
            const currency = element.dataset.currency;
            const rate = this.exchangeRates[currency];

            if (rate) {
                element.textContent = `1 KRW = ${rate.rate.toFixed(6)} ${currency}`;
            }
        });
    }

    /**
     * 결제 방법 표시 업데이트
     */
    updatePaymentMethodsDisplay(provider) {
        document.querySelectorAll('.payment-method-section').forEach(section => {
            section.style.display = 'none';
        });

        const targetSection = document.getElementById(`${provider}-methods`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
    }

    /**
     * 통화 포맷팅
     */
    formatCurrency(amount, currency) {
        const currencyInfo = this.supportedCurrencies[currency];
        if (!currencyInfo) return amount.toString();

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: currency === 'JPY' ? 0 : 2,
            maximumFractionDigits: currency === 'JPY' ? 0 : 2
        }).format(amount);
    }

    /**
     * 로딩 상태 표시
     */
    showLoadingState(show) {
        const button = document.querySelector('.international-payment-btn');
        const spinner = document.querySelector('.payment-spinner');

        if (button) {
            button.disabled = show;
            button.textContent = show ? '처리 중...' : '결제하기';
        }

        if (spinner) {
            spinner.style.display = show ? 'block' : 'none';
        }
    }

    /**
     * 성공 메시지 표시
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * 에러 메시지 표시
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * 알림 표시
     */
    showNotification(message, type) {
        // 기존 알림 제거
        const existing = document.querySelector('.payment-notification');
        if (existing) {
            existing.remove();
        }

        // 새 알림 생성
        const notification = document.createElement('div');
        notification.className = `payment-notification ${type}`;
        notification.textContent = message;

        // 페이지 상단에 추가
        document.body.insertBefore(notification, document.body.firstChild);

        // 자동 제거
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * 성공 페이지로 리다이렉트
     */
    redirectToSuccess() {
        setTimeout(() => {
            window.location.href = '/payment-success.html';
        }, 2000);
    }

    /**
     * 유틸리티 함수들
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    getAuthToken() {
        return localStorage.getItem('access_token') || '';
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// 전역 인스턴스 생성
window.InternationalPayments = new InternationalPayments();
