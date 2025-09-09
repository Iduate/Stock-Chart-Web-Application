// Complete authentication and prediction system integration
class StockChartApp {
    constructor() {
        this.apiBase = '/api';
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || '{}');
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateAuthUI();
        this.initializeAccessTracking();

        // Check if user is trying to access premium content
        if (this.isPremiumPage() && !this.canAccessPremium()) {
            this.showAccessLimitModal();
        }
    }

    setupEventListeners() {
        // Auth forms
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        const signupForm = document.getElementById('signupForm');
        if (signupForm) {
            signupForm.addEventListener('submit', (e) => this.handleSignup(e));
        }

        // Prediction form
        const predictionForm = document.querySelector('.prediction-form');
        if (predictionForm) {
            this.setupPredictionForm();
        }

        // Page load tracking
        this.trackPageAccess();
    }

    async handleLogin(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const loginData = {
            email: formData.get('email') || document.getElementById('loginEmail')?.value,
            password: formData.get('password') || document.getElementById('loginPassword')?.value
        };

        try {
            const response = await this.apiCall('/auth/login/', 'POST', loginData);

            if (response.access_token) {
                this.token = response.access_token;
                this.user = response.user;

                localStorage.setItem('token', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));

                showNotification('로그인 성공!', 'success');
                this.hideModal('loginModal');
                this.updateAuthUI();

                // Redirect if needed
                const redirect = localStorage.getItem('loginRedirect') || '';
                if (redirect) {
                    localStorage.removeItem('loginRedirect');
                    window.location.href = redirect;
                }

                // Refresh page to update access permissions
                window.location.reload();
            }
        } catch (error) {
            showNotification(error.message || '로그인에 실패했습니다.', 'error');
        }
    }

    async handleSignup(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const password = formData.get('password') || document.getElementById('signupPassword')?.value;
        const confirmPassword = formData.get('confirmPassword') || document.getElementById('signupPasswordConfirm')?.value;

        if (password !== confirmPassword) {
            showNotification('비밀번호가 일치하지 않습니다.', 'error');
            return;
        }

        const signupData = {
            username: formData.get('username') || document.getElementById('signupUsername')?.value,
            email: formData.get('email') || document.getElementById('signupEmail')?.value,
            password: password,
            referred_by: formData.get('referralCode') || document.getElementById('referralCode')?.value
        };

        try {
            const response = await this.apiCall('/auth/signup/', 'POST', signupData);
            showNotification('회원가입이 완료되었습니다! 로그인해주세요.', 'success');
            this.hideModal('signupModal');
            this.showModal('loginModal');
        } catch (error) {
            showNotification(error.message || '회원가입에 실패했습니다.', 'error');
        }
    }

    async submitPrediction() {
        if (!this.isAuthenticated()) {
            localStorage.setItem('loginRedirect', window.location.href);
            showNotification('예측을 저장하려면 로그인이 필요합니다.', 'info');
            this.showModal('loginModal');
            return;
        }

        const form = document.querySelector('.prediction-form');
        if (!form) return;

        const formData = this.extractPredictionData(form);
        if (!this.validatePredictionData(formData)) return;

        try {
            const response = await this.apiCall('/charts/predictions/', 'POST', formData);

            showNotification('예측이 성공적으로 저장되었습니다!', 'success');
            this.resetPredictionForm();

            // Navigate to predictions page after delay
            setTimeout(() => {
                window.location.href = 'my-predictions.html';
            }, 2000);

        } catch (error) {
            if (error.payment_required) {
                this.showPaymentModal();
            } else {
                showNotification(error.message || '예측 저장에 실패했습니다.', 'error');
            }
        }
    }

    extractPredictionData(form) {
        const stockSelect = form.querySelector('#stockSelect');
        const currentPrice = form.querySelector('#currentPrice');
        const predictedPrice = form.querySelector('#predictedPrice');
        const targetDate = form.querySelector('#targetDate');
        const reasoning = form.querySelector('#reasoning');
        const confidence = form.querySelector('#confidence');
        const isPublic = form.querySelector('#isPublic');

        return {
            stock_symbol: stockSelect?.value,
            stock_name: stockSelect?.options[stockSelect.selectedIndex]?.text,
            current_price: parseFloat(currentPrice?.value),
            predicted_price: parseFloat(predictedPrice?.value),
            target_date: targetDate?.value,
            reasoning: reasoning?.value || '',
            confidence: parseInt(confidence?.value || '75'),
            is_public: isPublic?.checked ?? true
        };
    }

    validatePredictionData(data) {
        if (!data.stock_symbol) {
            showNotification('종목을 선택해주세요.', 'warning');
            return false;
        }

        if (!data.current_price || isNaN(data.current_price)) {
            showNotification('현재 가격을 확인해주세요.', 'warning');
            return false;
        }

        if (!data.predicted_price || isNaN(data.predicted_price)) {
            showNotification('예측 가격을 입력해주세요.', 'warning');
            return false;
        }

        if (!data.target_date) {
            showNotification('목표 날짜를 선택해주세요.', 'warning');
            return false;
        }

        return true;
    }

    async loadPublicPredictions() {
        try {
            const predictions = await this.apiCall('/charts/predictions/public_predictions/');
            this.displayPredictions(predictions);
        } catch (error) {
            if (error.payment_required) {
                this.showPaymentModal();
            } else {
                showNotification('예측 데이터를 불러올 수 없습니다.', 'error');
            }
        }
    }

    async loadRankings() {
        try {
            const rankings = await this.apiCall('/charts/predictions/rankings/');
            this.displayRankings(rankings);
        } catch (error) {
            if (error.payment_required) {
                this.showPaymentModal();
            } else {
                showNotification('랭킹 데이터를 불러올 수 없습니다.', 'error');
            }
        }
    }

    displayPredictions(predictions) {
        const container = document.getElementById('predictionsContainer');
        if (!container) return;

        container.innerHTML = predictions.map(prediction => `
            <div class="prediction-card">
                <div class="prediction-header">
                    <h4>${prediction.stock_name} (${prediction.user_name})</h4>
                    <span class="prediction-status status-${prediction.status}">
                        ${prediction.status_name}
                    </span>
                </div>
                <div class="prediction-details">
                    <div class="price-info">
                        <span>현재가: $${prediction.current_price}</span>
                        <span>예측가: $${prediction.predicted_price}</span>
                    </div>
                    <div class="prediction-meta">
                        <span>목표일: ${new Date(prediction.target_date).toLocaleDateString()}</span>
                        ${prediction.accuracy_percentage ?
                `<span>정확도: ${prediction.accuracy_percentage}%</span>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    isAuthenticated() {
        return !!(this.token && this.user.id);
    }

    isPremiumPage() {
        const premiumPages = ['charts.html', 'prediction.html', 'my-predictions.html', 'ranking.html'];
        return premiumPages.some(page => window.location.pathname.includes(page));
    }

    canAccessPremium() {
        if (this.isAuthenticated()) {
            return this.user.user_type === 'paid' || this.user.user_type === 'admin' ||
                this.user.free_access_count < 3;
        }

        const freeAccess = parseInt(localStorage.getItem('freeAccessCount') || '0');
        return freeAccess < 3;
    }

    trackPageAccess() {
        if (!this.isPremiumPage()) return;

        if (!this.isAuthenticated()) {
            let count = parseInt(localStorage.getItem('freeAccessCount') || '0');
            count++;
            localStorage.setItem('freeAccessCount', count.toString());
        }
    }

    initializeAccessTracking() {
        // Initialize access tracking system
        if (this.isPremiumPage() && !this.canAccessPremium()) {
            setTimeout(() => {
                window.location.href = 'subscription.html?payment_required=true';
            }, 1000);
        }
    }

    showAccessLimitModal() {
        const modal = document.createElement('div');
        modal.className = 'access-limit-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>무료 접근 한도 도달</h3>
                <p>무료 사용자는 프리미엄 콘텐츠에 3번만 접근할 수 있습니다.</p>
                <p>계속 이용하시려면 구독을 신청해주세요.</p>
                <div class="modal-actions">
                    <button onclick="window.location.href='subscription.html'" class="btn-primary">
                        구독하기
                    </button>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="btn-secondary">
                        닫기
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    showPaymentModal() {
        window.location.href = 'subscription.html?payment_required=true';
    }

    updateAuthUI() {
        const authButtons = document.querySelectorAll('.auth-button, .login-btn');
        const userInfo = document.querySelectorAll('.user-info');
        const logoutButtons = document.querySelectorAll('.logout-btn');

        if (this.isAuthenticated()) {
            authButtons.forEach(btn => btn.style.display = 'none');
            userInfo.forEach(info => {
                info.style.display = 'block';
                info.innerHTML = `환영합니다, ${this.user.username}님!`;
            });
            logoutButtons.forEach(btn => {
                btn.style.display = 'block';
                btn.onclick = () => this.logout();
            });
        } else {
            authButtons.forEach(btn => btn.style.display = 'block');
            userInfo.forEach(info => info.style.display = 'none');
            logoutButtons.forEach(btn => btn.style.display = 'none');
        }
    }

    logout() {
        this.token = null;
        this.user = {};
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('freeAccessCount');
        window.location.href = 'index.html';
    }

    resetPredictionForm() {
        const form = document.querySelector('.prediction-form');
        if (form) {
            form.reset();
            const isPublic = form.querySelector('#isPublic');
            if (isPublic) isPublic.checked = true;
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBase}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.token) {
            options.headers.Authorization = `Bearer ${this.token}`;
        }

        // Add CSRF token if available
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
            options.headers['X-CSRFToken'] = csrfToken;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            if (response.status === 402) {
                result.payment_required = true;
            }
            throw result;
        }

        return result;
    }

    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    setupPredictionForm() {
        // Setup step navigation and validation
        this.setupFormSteps();

        // Setup prediction submission
        const submitButton = document.getElementById('submitPrediction');
        if (submitButton) {
            submitButton.onclick = () => this.submitPrediction();
        }
    }

    setupFormSteps() {
        const steps = document.querySelectorAll('.form-step');
        const nextBtn = document.getElementById('nextStep');
        const prevBtn = document.getElementById('prevStep');
        let currentStep = 0;

        const showStep = (step) => {
            steps.forEach((s, i) => {
                s.style.display = i === step ? 'block' : 'none';
            });

            prevBtn.disabled = step === 0;

            if (step === steps.length - 1) {
                nextBtn.style.display = 'none';
                document.getElementById('submitPrediction').style.display = 'block';
            } else {
                nextBtn.style.display = 'block';
                document.getElementById('submitPrediction').style.display = 'none';
            }

            // Update progress
            const progressFill = document.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = `${((step + 1) / steps.length) * 100}%`;
            }
        };

        if (nextBtn) {
            nextBtn.onclick = () => {
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    showStep(currentStep);
                }
            };
        }

        if (prevBtn) {
            prevBtn.onclick = () => {
                if (currentStep > 0) {
                    currentStep--;
                    showStep(currentStep);
                }
            };
        }

        showStep(0);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.stockChartApp = new StockChartApp();

    // Make key functions available globally for backward compatibility
    window.submitPrediction = () => window.stockChartApp.submitPrediction();
    window.handleLogin = (e) => window.stockChartApp.handleLogin(e);
    window.handleSignup = (e) => window.stockChartApp.handleSignup(e);
});
