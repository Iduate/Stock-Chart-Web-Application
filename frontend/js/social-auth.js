/**
 * 소셜 로그인 인증 JavaScript 라이브러리
 * Stock Chart Web Application
 */

class SocialAuthManager {
    constructor(options = {}) {
        this.baseUrl = options.baseUrl || '/api/users/auth';
        this.csrfToken = this.getCSRFToken();
        this.providers = [];
        this.currentProvider = null;
        this.popupWindow = null;
        this.callbacks = {
            onSuccess: options.onSuccess || this.defaultSuccessHandler,
            onError: options.onError || this.defaultErrorHandler,
            onStart: options.onStart || this.defaultStartHandler
        };

        this.init();
    }

    /**
     * 초기화
     */
    async init() {
        try {
            await this.loadProviders();
            this.setupEventListeners();
            this.renderSocialButtons();
        } catch (error) {
            console.error('소셜 인증 초기화 오류:', error);
        }
    }

    /**
     * 사용 가능한 소셜 제공업체 로드
     */
    async loadProviders() {
        try {
            const response = await fetch(`${this.baseUrl}/social/providers/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) {
                throw new Error('제공업체 목록 로드 실패');
            }

            const data = await response.json();
            this.providers = data.providers || [];

        } catch (error) {
            console.error('제공업체 로드 오류:', error);
            throw error;
        }
    }

    /**
     * 소셜 로그인 시작
     */
    async startSocialLogin(providerName, options = {}) {
        try {
            this.currentProvider = providerName;
            this.callbacks.onStart(providerName);

            // 인증 URL 요청
            const response = await fetch(`${this.baseUrl}/social/${providerName}/login/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) {
                throw new Error('인증 URL 생성 실패');
            }

            const data = await response.json();

            if (options.redirect) {
                // 리다이렉트 방식
                window.location.href = data.auth_url;
            } else {
                // 팝업 방식 (기본값)
                this.openPopup(data.auth_url, providerName);
            }

        } catch (error) {
            console.error('소셜 로그인 시작 오류:', error);
            this.callbacks.onError(error, providerName);
        }
    }

    /**
     * 팝업 창 열기
     */
    openPopup(authUrl, providerName) {
        const popupFeatures = 'width=600,height=700,scrollbars=yes,resizable=yes,status=yes,location=yes';

        // 팝업 URL에 프론트엔드 리다이렉트 파라미터 추가
        const url = new URL(authUrl);
        url.searchParams.set('redirect_to_frontend', 'true');

        this.popupWindow = window.open(url.toString(), `social_login_${providerName}`, popupFeatures);

        if (!this.popupWindow) {
            throw new Error('팝업이 차단되었습니다. 팝업 차단을 해제해주세요.');
        }

        // 팝업 상태 모니터링
        this.monitorPopup(providerName);
    }

    /**
     * 팝업 상태 모니터링
     */
    monitorPopup(providerName) {
        const checkClosed = setInterval(() => {
            if (this.popupWindow && this.popupWindow.closed) {
                clearInterval(checkClosed);
                this.callbacks.onError(new Error('사용자가 인증을 취소했습니다.'), providerName);
            }
        }, 1000);

        // 메시지 리스너 설정 (팝업에서 부모 창으로 메시지 전송)
        const messageListener = (event) => {
            if (event.origin !== window.location.origin) return;

            if (event.data.type === 'SOCIAL_AUTH_SUCCESS') {
                clearInterval(checkClosed);
                window.removeEventListener('message', messageListener);

                if (this.popupWindow) {
                    this.popupWindow.close();
                }

                this.handleAuthSuccess(event.data.result);
            } else if (event.data.type === 'SOCIAL_AUTH_ERROR') {
                clearInterval(checkClosed);
                window.removeEventListener('message', messageListener);

                if (this.popupWindow) {
                    this.popupWindow.close();
                }

                this.callbacks.onError(new Error(event.data.error), providerName);
            }
        };

        window.addEventListener('message', messageListener);
    }

    /**
     * 인증 성공 처리
     */
    handleAuthSuccess(result) {
        // 토큰 저장
        if (result.tokens) {
            this.saveTokens(result.tokens);
        }

        // 사용자 정보 저장
        if (result.user) {
            this.saveUserInfo(result.user);
        }

        this.callbacks.onSuccess(result);
    }

    /**
     * 토큰 저장
     */
    saveTokens(tokens) {
        if (tokens.access) {
            localStorage.setItem('access_token', tokens.access);
        }
        if (tokens.refresh) {
            localStorage.setItem('refresh_token', tokens.refresh);
        }
    }

    /**
     * 사용자 정보 저장
     */
    saveUserInfo(user) {
        localStorage.setItem('user_info', JSON.stringify(user));
    }

    /**
     * 소셜 계정 연결
     */
    async connectSocialAccount(providerName) {
        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                throw new Error('로그인이 필요합니다.');
            }

            const response = await fetch(`${this.baseUrl}/social/accounts/connect/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ provider: providerName })
            });

            if (!response.ok) {
                throw new Error('계정 연결 요청 실패');
            }

            const data = await response.json();
            this.openPopup(data.auth_url, providerName);

        } catch (error) {
            console.error('계정 연결 오류:', error);
            this.callbacks.onError(error, providerName);
        }
    }

    /**
     * 소셜 계정 연결 해제
     */
    async disconnectSocialAccount(providerName, socialId = null) {
        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                throw new Error('로그인이 필요합니다.');
            }

            const response = await fetch(`${this.baseUrl}/social/accounts/disconnect/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    provider: providerName,
                    social_id: socialId
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '계정 연결 해제 실패');
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('계정 연결 해제 오류:', error);
            throw error;
        }
    }

    /**
     * 사용자 소셜 계정 목록 조회
     */
    async getUserSocialAccounts() {
        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                throw new Error('로그인이 필요합니다.');
            }

            const response = await fetch(`${this.baseUrl}/social/accounts/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) {
                throw new Error('소셜 계정 목록 조회 실패');
            }

            const data = await response.json();
            return data.social_accounts || [];

        } catch (error) {
            console.error('소셜 계정 목록 조회 오류:', error);
            throw error;
        }
    }

    /**
     * 소셜 로그아웃
     */
    async socialLogout(sessionId = null) {
        try {
            const accessToken = localStorage.getItem('access_token');

            const response = await fetch(`${this.baseUrl}/social/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': accessToken ? `Bearer ${accessToken}` : '',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ session_id: sessionId })
            });

            // 로컬 토큰 제거
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_info');

            return response.ok;

        } catch (error) {
            console.error('소셜 로그아웃 오류:', error);
            return false;
        }
    }

    /**
     * 소셜 로그인 버튼 렌더링
     */
    renderSocialButtons() {
        const containers = document.querySelectorAll('[data-social-login-container]');

        containers.forEach(container => {
            const providersToShow = container.dataset.providers
                ? container.dataset.providers.split(',')
                : this.providers.map(p => p.name);

            const buttonsHtml = this.providers
                .filter(provider => providersToShow.includes(provider.name))
                .map(provider => this.createButtonHtml(provider))
                .join('');

            container.innerHTML = buttonsHtml;

            // 버튼 이벤트 리스너 설정
            container.querySelectorAll('[data-social-provider]').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    const providerName = button.dataset.socialProvider;
                    const redirect = button.dataset.redirect === 'true';
                    this.startSocialLogin(providerName, { redirect });
                });
            });
        });
    }

    /**
     * 소셜 로그인 버튼 HTML 생성
     */
    createButtonHtml(provider) {
        const iconHtml = provider.icon_url
            ? `<img src="${provider.icon_url}" alt="${provider.display_name}" class="social-icon" />`
            : '';

        return `
            <button 
                type="button" 
                class="social-login-btn social-login-btn-${provider.name}"
                data-social-provider="${provider.name}"
                data-redirect="false"
            >
                ${iconHtml}
                <span>${provider.display_name}로 로그인</span>
            </button>
        `;
    }

    /**
     * 이벤트 리스너 설정
     */
    setupEventListeners() {
        // URL 파라미터에서 소셜 로그인 성공 처리
        this.handleUrlParams();
    }

    /**
     * URL 파라미터 처리 (리다이렉트 방식 로그인 결과)
     */
    handleUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);

        if (urlParams.has('token') && urlParams.has('provider')) {
            const token = urlParams.get('token');
            const refreshToken = urlParams.get('refresh');
            const provider = urlParams.get('provider');
            const created = urlParams.get('created') === 'true';

            // 토큰 저장
            if (token) {
                localStorage.setItem('access_token', token);
            }
            if (refreshToken) {
                localStorage.setItem('refresh_token', refreshToken);
            }

            // URL 정리
            window.history.replaceState({}, document.title, window.location.pathname);

            // 성공 콜백 호출
            this.callbacks.onSuccess({
                provider,
                user_created: created,
                tokens: { access: token, refresh: refreshToken }
            });
        }
    }

    /**
     * CSRF 토큰 획득
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }

        // Meta 태그에서 CSRF 토큰 획득
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }

        return null;
    }

    /**
     * 기본 성공 핸들러
     */
    defaultSuccessHandler(result) {
        console.log('소셜 로그인 성공:', result);

        // 페이지 리다이렉트 또는 UI 업데이트
        if (result.user_created) {
            alert('회원가입이 완료되었습니다!');
        } else {
            alert('로그인되었습니다!');
        }

        // 메인 페이지로 리다이렉트
        window.location.href = '/';
    }

    /**
     * 기본 오류 핸들러
     */
    defaultErrorHandler(error, provider) {
        console.error('소셜 로그인 오류:', error, provider);
        alert(`소셜 로그인 중 오류가 발생했습니다: ${error.message}`);
    }

    /**
     * 기본 시작 핸들러
     */
    defaultStartHandler(provider) {
        console.log('소셜 로그인 시작:', provider);
    }
}

// 유틸리티 함수들

/**
 * 소셜 계정 관리 UI 생성
 */
function createSocialAccountManager(containerId, socialAuth) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // 소셜 계정 목록 로드 및 렌더링
    socialAuth.getUserSocialAccounts()
        .then(accounts => {
            const html = `
                <div class="social-accounts-manager">
                    <h3>연결된 소셜 계정</h3>
                    <div class="social-accounts-list">
                        ${accounts.map(account => `
                            <div class="social-account-item">
                                <div class="account-info">
                                    <img src="${account.provider.icon_url || ''}" alt="${account.provider_display_name}" class="provider-icon" />
                                    <div class="account-details">
                                        <div class="provider-name">${account.provider_display_name}</div>
                                        <div class="account-email">${account.email}</div>
                                    </div>
                                </div>
                                <div class="account-actions">
                                    ${account.is_primary ? '<span class="primary-badge">주 계정</span>' : ''}
                                    <button type="button" class="disconnect-btn" data-provider="${account.provider_name}" data-social-id="${account.social_id}">
                                        연결 해제
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="add-social-account">
                        <h4>계정 연결 추가</h4>
                        <div data-social-login-container data-connect-mode="true"></div>
                    </div>
                </div>
            `;

            container.innerHTML = html;

            // 연결 해제 버튼 이벤트
            container.querySelectorAll('.disconnect-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const provider = e.target.dataset.provider;
                    const socialId = e.target.dataset.socialId;

                    if (confirm('정말로 이 계정 연결을 해제하시겠습니까?')) {
                        try {
                            await socialAuth.disconnectSocialAccount(provider, socialId);
                            location.reload(); // 페이지 새로고침
                        } catch (error) {
                            alert(`연결 해제 실패: ${error.message}`);
                        }
                    }
                });
            });

            // 소셜 로그인 버튼 다시 렌더링 (연결 모드)
            socialAuth.renderSocialButtons();
        })
        .catch(error => {
            console.error('소셜 계정 목록 로드 오류:', error);
            container.innerHTML = '<p>소셜 계정 정보를 불러올 수 없습니다.</p>';
        });
}

// 전역 객체로 노출
window.SocialAuthManager = SocialAuthManager;
window.createSocialAccountManager = createSocialAccountManager;
