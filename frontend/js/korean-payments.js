/**
 * 한국 결제 시스템 JavaScript 라이브러리
 * 아임포트, 토스페이먼츠, 카카오페이 통합 지원
 */

class KoreanPayments {
    constructor() {
        this.currentPlan = null;
        this.currentAmount = 0;
        this.currentProvider = null;
        this.currentMethod = null;
        this.discountAmount = 0;
        this.finalAmount = 0;

        // API 엔드포인트
        this.apiBase = '/api/korean-payments';

        // 결제 제공업체 설정
        this.providers = {
            iamport: {
                name: 'iamport',
                userCode: 'imp05048233', // 실제 아임포트 가맹점 코드로 변경 필요
                appScheme: 'stockchart'
            },
            toss: {
                name: 'toss',
                clientKey: 'test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eoq', // 실제 토스페이먼츠 클라이언트 키로 변경 필요
                appScheme: 'stockchart'
            },
            kakaopay: {
                name: 'kakaopay',
                appKey: '3f7b3a7c4f8e9d1a2b3c4d5e6f7g8h9i', // 실제 카카오페이 앱 키로 변경 필요
                appScheme: 'stockchart'
            }
        };

        this.init();
    }

    init() {
        this.initializeProviders();
        this.bindEvents();
        this.loadPaymentMethods();
    }

    /**
     * 결제 제공업체 초기화
     */
    initializeProviders() {
        // 아임포트 초기화
        if (typeof IMP !== 'undefined') {
            IMP.init(this.providers.iamport.userCode);
        }

        // 토스페이먼츠 초기화
        if (typeof TossPayments !== 'undefined') {
            this.tossPayments = TossPayments(this.providers.toss.clientKey);
        }

        // 카카오페이 초기화
        if (typeof Kakao !== 'undefined' && !Kakao.isInitialized()) {
            Kakao.init(this.providers.kakaopay.appKey);
        }
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 플랜 선택
        document.querySelectorAll('.plan-select-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const planCard = e.target.closest('.plan-card');
                const plan = planCard.dataset.plan;
                const amount = parseInt(e.target.dataset.amount);
                this.selectPlan(plan, amount);
            });
        });

        // 결제 방법 선택
        document.querySelectorAll('input[name="paymentMethod"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    const option = e.target.closest('.payment-option');
                    const provider = option.dataset.provider;
                    const method = option.dataset.method;
                    this.selectPaymentMethod(provider, method);
                }
            });
        });

        // 할인 코드 적용
        const applyDiscountBtn = document.getElementById('applyDiscountBtn');
        if (applyDiscountBtn) {
            applyDiscountBtn.addEventListener('click', () => {
                this.applyDiscount();
            });
        }

        // 결제 버튼
        const payNowBtn = document.getElementById('payNowBtn');
        if (payNowBtn) {
            payNowBtn.addEventListener('click', () => {
                this.processPayment();
            });
        }

        // 이전 버튼
        const backToMethodsBtn = document.getElementById('backToMethodsBtn');
        if (backToMethodsBtn) {
            backToMethodsBtn.addEventListener('click', () => {
                this.showPaymentMethods();
            });
        }

        // 재시도 버튼
        const retryPaymentBtn = document.getElementById('retryPaymentBtn');
        if (retryPaymentBtn) {
            retryPaymentBtn.addEventListener('click', () => {
                this.showPaymentMethods();
            });
        }
    }

    /**
     * 플랜 선택
     */
    selectPlan(plan, amount) {
        this.currentPlan = plan;
        this.currentAmount = amount;
        this.finalAmount = amount;

        // UI 업데이트
        document.querySelectorAll('.plan-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-plan="${plan}"]`).classList.add('selected');

        // 결제 방법 선택 화면으로 이동
        this.showPaymentMethods();

        // 결제 요약 정보 업데이트
        this.updatePaymentSummary();
    }

    /**
     * 결제 방법 선택
     */
    selectPaymentMethod(provider, method) {
        this.currentProvider = provider;
        this.currentMethod = method;

        // UI 업데이트
        document.querySelectorAll('.payment-option').forEach(option => {
            option.classList.remove('selected');
        });
        document.querySelector(`[data-provider="${provider}"][data-method="${method}"]`).classList.add('selected');

        // 결제 요약 화면으로 이동
        this.showPaymentSummary();

        // 결제 요약 정보 업데이트
        this.updatePaymentSummary();
    }

    /**
     * 화면 전환
     */
    showPaymentMethods() {
        document.getElementById('subscriptionPlans').style.display = 'none';
        document.getElementById('paymentMethods').style.display = 'block';
        document.getElementById('paymentSummary').style.display = 'none';
        document.getElementById('paymentProcessing').style.display = 'none';
        document.getElementById('paymentResult').style.display = 'none';
    }

    showPaymentSummary() {
        document.getElementById('subscriptionPlans').style.display = 'none';
        document.getElementById('paymentMethods').style.display = 'none';
        document.getElementById('paymentSummary').style.display = 'block';
        document.getElementById('paymentProcessing').style.display = 'none';
        document.getElementById('paymentResult').style.display = 'none';
    }

    showPaymentProcessing() {
        document.getElementById('subscriptionPlans').style.display = 'none';
        document.getElementById('paymentMethods').style.display = 'none';
        document.getElementById('paymentSummary').style.display = 'none';
        document.getElementById('paymentProcessing').style.display = 'block';
        document.getElementById('paymentResult').style.display = 'none';
    }

    showPaymentResult(success, data = {}) {
        document.getElementById('subscriptionPlans').style.display = 'none';
        document.getElementById('paymentMethods').style.display = 'none';
        document.getElementById('paymentSummary').style.display = 'none';
        document.getElementById('paymentProcessing').style.display = 'none';
        document.getElementById('paymentResult').style.display = 'block';

        if (success) {
            document.getElementById('resultSuccess').style.display = 'block';
            document.getElementById('resultError').style.display = 'none';

            // 성공 정보 업데이트
            if (data.transactionId) {
                document.getElementById('transactionId').textContent = data.transactionId;
            }
            if (data.plan) {
                document.getElementById('resultPlan').textContent = this.getPlanName(data.plan);
            }
            if (data.amount) {
                document.getElementById('resultAmount').textContent = this.formatAmount(data.amount);
            }
        } else {
            document.getElementById('resultSuccess').style.display = 'none';
            document.getElementById('resultError').style.display = 'block';

            // 오류 정보 업데이트
            if (data.error) {
                document.getElementById('errorMessage').textContent = data.error;
            }
        }
    }

    /**
     * 결제 요약 정보 업데이트
     */
    updatePaymentSummary() {
        if (this.currentPlan) {
            document.getElementById('selectedPlan').textContent = this.getPlanName(this.currentPlan);
        }

        if (this.currentMethod) {
            document.getElementById('selectedMethod').textContent = this.getMethodName(this.currentMethod);
        }

        document.getElementById('paymentAmount').textContent = this.formatAmount(this.finalAmount);
    }

    /**
     * 할인 코드 적용
     */
    async applyDiscount() {
        const discountCode = document.getElementById('discountCode').value.trim();
        const resultDiv = document.getElementById('discountResult');

        if (!discountCode) {
            this.showDiscountResult('할인 코드를 입력해주세요.', false);
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/api/discount/validate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    code: discountCode,
                    amount: this.currentAmount
                })
            });

            const data = await response.json();

            if (response.ok && data.valid) {
                this.discountAmount = data.discount_amount;
                this.finalAmount = this.currentAmount - this.discountAmount;

                this.showDiscountResult(
                    `할인이 적용되었습니다! ${this.formatAmount(this.discountAmount)} 할인`,
                    true
                );

                this.updatePaymentSummary();
            } else {
                this.showDiscountResult(data.message || '유효하지 않은 할인 코드입니다.', false);
            }
        } catch (error) {
            console.error('Discount validation error:', error);
            this.showDiscountResult('할인 코드 확인 중 오류가 발생했습니다.', false);
        }
    }

    /**
     * 할인 결과 표시
     */
    showDiscountResult(message, success) {
        const resultDiv = document.getElementById('discountResult');
        resultDiv.textContent = message;
        resultDiv.className = `discount-result ${success ? 'success' : 'error'}`;
        resultDiv.style.display = 'block';
    }

    /**
     * 결제 처리
     */
    async processPayment() {
        if (!this.currentPlan || !this.currentProvider || !this.currentMethod) {
            alert('결제 정보가 완전하지 않습니다.');
            return;
        }

        this.showPaymentProcessing();

        try {
            // 결제 요청 생성
            const paymentData = await this.createPaymentRequest();

            if (!paymentData.success) {
                throw new Error(paymentData.error || '결제 요청 생성 실패');
            }

            // 제공업체별 결제 처리
            let paymentResult;
            switch (this.currentProvider) {
                case 'iamport':
                    paymentResult = await this.processIamportPayment(paymentData);
                    break;
                case 'toss':
                    paymentResult = await this.processTossPayment(paymentData);
                    break;
                case 'kakaopay':
                    paymentResult = await this.processKakaoPayment(paymentData);
                    break;
                case 'paypal':
                    paymentResult = await this.processPayPalPayment(paymentData);
                    break;
                default:
                    throw new Error('지원하지 않는 결제 제공업체입니다.');
            }

            if (paymentResult.success) {
                // 결제 검증
                const verificationResult = await this.verifyPayment(paymentResult);

                if (verificationResult.success) {
                    this.showPaymentResult(true, verificationResult);
                } else {
                    throw new Error(verificationResult.error || '결제 검증 실패');
                }
            } else {
                throw new Error(paymentResult.error || '결제 처리 실패');
            }

        } catch (error) {
            console.error('Payment processing error:', error);
            this.showPaymentResult(false, { error: error.message });
        }
    }

    /**
     * 결제 요청 생성
     */
    async createPaymentRequest() {
        const user = this.getCurrentUser();

        const requestData = {
            provider: this.currentProvider,
            payment_method: this.currentMethod,
            amount: this.finalAmount,
            name: `${this.getPlanName(this.currentPlan)} 구독`,
            description: `${this.getPlanName(this.currentPlan)} 월간 구독`,
            buyer_name: user?.name || '사용자',
            buyer_email: user?.email || 'user@example.com',
            buyer_tel: user?.phone || '',
            success_url: `${window.location.origin}/payment-success.html`,
            cancel_url: `${window.location.origin}/payment-cancel.html`,
            fail_url: `${window.location.origin}/payment-fail.html`
        };

        const response = await fetch(`${this.apiBase}/api/payment/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            },
            body: JSON.stringify(requestData)
        });

        return await response.json();
    }

    /**
     * 아임포트 결제 처리
     */
    async processIamportPayment(paymentData) {
        return new Promise((resolve) => {
            if (typeof IMP === 'undefined') {
                resolve({ success: false, error: '아임포트 라이브러리가 로드되지 않았습니다.' });
                return;
            }

            const requestData = {
                pg: this.getIamportPG(),
                pay_method: this.currentMethod,
                merchant_uid: paymentData.merchant_uid,
                name: paymentData.name,
                amount: this.finalAmount,
                buyer_email: paymentData.buyer_email,
                buyer_name: paymentData.buyer_name,
                buyer_tel: paymentData.buyer_tel || '',
                buyer_addr: paymentData.buyer_addr || '',
                buyer_postcode: paymentData.buyer_postcode || '',
                m_redirect_url: `${window.location.origin}/payment-mobile-redirect.html`,
                app_scheme: this.providers.iamport.appScheme
            };

            IMP.request_pay(requestData, (rsp) => {
                if (rsp.success) {
                    resolve({
                        success: true,
                        imp_uid: rsp.imp_uid,
                        merchant_uid: rsp.merchant_uid,
                        amount: rsp.paid_amount,
                        status: rsp.status
                    });
                } else {
                    resolve({
                        success: false,
                        error: rsp.error_msg || '결제가 취소되었습니다.'
                    });
                }
            });
        });
    }

    /**
     * 토스페이먼츠 결제 처리
     */
    async processTossPayment(paymentData) {
        try {
            if (typeof TossPayments === 'undefined' || !this.tossPayments) {
                throw new Error('토스페이먼츠 라이브러리가 로드되지 않았습니다.');
            }

            const payment = this.tossPayments.payment({
                amount: this.finalAmount,
                orderId: paymentData.merchant_uid,
                orderName: paymentData.name,
                customerName: paymentData.buyer_name,
                customerEmail: paymentData.buyer_email,
                successUrl: `${window.location.origin}/payment-success.html`,
                failUrl: `${window.location.origin}/payment-fail.html`
            });

            // 결제 방법에 따른 처리
            if (this.currentMethod === 'card') {
                await payment.requestPayment('카드');
            } else if (this.currentMethod === 'transfer') {
                await payment.requestPayment('계좌이체');
            } else if (this.currentMethod === 'vbank') {
                await payment.requestPayment('가상계좌');
            }

            return { success: true };

        } catch (error) {
            return {
                success: false,
                error: error.message || '토스페이먼츠 결제 처리 중 오류가 발생했습니다.'
            };
        }
    }

    /**
     * 카카오페이 결제 처리
     */
    async processKakaoPayment(paymentData) {
        try {
            if (typeof Kakao === 'undefined') {
                throw new Error('카카오 SDK가 로드되지 않았습니다.');
            }

            // 카카오페이 결제 요청
            const response = await fetch(`${this.apiBase}/api/kakaopay/ready/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    partner_order_id: paymentData.merchant_uid,
                    partner_user_id: paymentData.buyer_email,
                    item_name: paymentData.name,
                    quantity: 1,
                    total_amount: this.finalAmount,
                    tax_free_amount: 0,
                    approval_url: `${window.location.origin}/payment-success.html`,
                    cancel_url: `${window.location.origin}/payment-cancel.html`,
                    fail_url: `${window.location.origin}/payment-fail.html`
                })
            });

            const data = await response.json();

            if (data.success) {
                // 카카오페이 결제 페이지로 리다이렉트
                window.location.href = data.next_redirect_pc_url;
                return { success: true };
            } else {
                throw new Error(data.error || '카카오페이 결제 준비 실패');
            }

        } catch (error) {
            return {
                success: false,
                error: error.message || '카카오페이 결제 처리 중 오류가 발생했습니다.'
            };
        }
    }

    /**
     * PayPal 결제 처리
     */
    async processPayPalPayment(paymentData) {
        // PayPal 결제 로직 (기존 payment_system과 연동)
        try {
            const response = await fetch('/api/payments/paypal/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    amount: this.finalAmount,
                    currency: 'USD', // PayPal은 USD 기준
                    description: paymentData.name
                })
            });

            const data = await response.json();

            if (data.success) {
                window.location.href = data.approval_url;
                return { success: true };
            } else {
                throw new Error(data.error || 'PayPal 결제 준비 실패');
            }

        } catch (error) {
            return {
                success: false,
                error: error.message || 'PayPal 결제 처리 중 오류가 발생했습니다.'
            };
        }
    }

    /**
     * 결제 검증
     */
    async verifyPayment(paymentResult) {
        const verificationData = {
            provider: this.currentProvider,
            merchant_uid: paymentResult.merchant_uid,
            amount: this.finalAmount
        };

        // 제공업체별 추가 데이터
        if (paymentResult.imp_uid) {
            verificationData.imp_uid = paymentResult.imp_uid;
        }
        if (paymentResult.payment_key) {
            verificationData.payment_key = paymentResult.payment_key;
        }

        const response = await fetch(`${this.apiBase}/api/payment/verify/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            },
            body: JSON.stringify(verificationData)
        });

        return await response.json();
    }

    /**
     * 결제 방법 로드
     */
    async loadPaymentMethods() {
        try {
            const response = await fetch(`${this.apiBase}/api/methods/`);
            const methods = await response.json();

            // UI 업데이트 로직
            this.updatePaymentMethodsUI(methods);

        } catch (error) {
            console.error('Failed to load payment methods:', error);
        }
    }

    /**
     * 유틸리티 함수들
     */
    getIamportPG() {
        const pgMap = {
            card: 'html5_inicis',
            trans: 'html5_inicis',
            vbank: 'html5_inicis',
            phone: 'danal_tpay'
        };
        return pgMap[this.currentMethod] || 'html5_inicis';
    }

    getPlanName(plan) {
        const planNames = {
            basic: '베이직',
            premium: '프리미엄',
            pro: '프로'
        };
        return planNames[plan] || plan;
    }

    getMethodName(method) {
        const methodNames = {
            card: '신용카드',
            trans: '계좌이체',
            vbank: '가상계좌',
            phone: '휴대폰 결제',
            kakaopay: '카카오페이',
            toss: '토스페이',
            paypal: 'PayPal'
        };
        return methodNames[method] || method;
    }

    formatAmount(amount) {
        return new Intl.NumberFormat('ko-KR', {
            style: 'currency',
            currency: 'KRW'
        }).format(amount);
    }

    getAuthToken() {
        return localStorage.getItem('access_token') || '';
    }

    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }
}

// 전역 인스턴스 생성
window.KoreanPayments = new KoreanPayments();
