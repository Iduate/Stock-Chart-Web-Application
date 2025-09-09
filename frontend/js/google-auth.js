/**
 * Google OAuth Authentication
 */

// Initialize Google Sign-In
function initGoogleAuth() {
    console.log('Initializing Google Auth...');

    // Make the handler available globally first so it's accessible
    window.handleGoogleCredentialResponse = handleGoogleCredentialResponse;

    // Check if the Google API is already loaded
    if (typeof google !== 'undefined' && google.accounts) {
        console.log('Google API already loaded, initializing client...');
        setupGoogleClient();
        return;
    }

    // Load Google Sign-In API script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;

    script.onload = () => {
        console.log('Google API script loaded');
        setupGoogleClient();
    };

    script.onerror = (e) => {
        console.error('Error loading Google API:', e);
        showNotification('오류', 'Google 로그인 API를 불러올 수 없습니다.', 'error');
    };

    document.head.appendChild(script);
}

// Set up Google client after API loads
function setupGoogleClient() {
    try {
        // Get the current hostname to handle both local and production environments
        const currentOrigin = window.location.origin;
        console.log('Current origin:', currentOrigin);

        google.accounts.id.initialize({
            client_id: '344149544124-0uu1if146t438cae5m8j0veivpf0pl6b.apps.googleusercontent.com',
            callback: handleGoogleCredentialResponse,
            auto_select: false,
            cancel_on_tap_outside: true,
            ux_mode: 'popup',
            context: 'signin'
        });

        console.log('Google client initialized successfully');

        // Create a custom Google Sign-In button that looks better
        const googleButtons = document.querySelectorAll('.btn-google');
        googleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                triggerGoogleSignIn();
            });
        });
    } catch (error) {
        console.error('Error initializing Google client:', error);
        showNotification('오류', 'Google 로그인 설정에 문제가 발생했습니다.', 'error');
    }
}

// Function to trigger Google Sign-In
function triggerGoogleSignIn() {
    // Make this function available globally
    window.triggerGoogleSignIn = triggerGoogleSignIn;
    try {
        console.log('Triggering Google Sign-In...');

        // Show a loading notification
        showNotification('로딩 중', 'Google 로그인을 진행하고 있습니다...', 'info');

        // Prompt the user to select an account
        google.accounts.id.prompt(notification => {
            if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
                console.log('Google Sign-In prompt not displayed:', notification.getNotDisplayedReason() || notification.getSkippedReason());

                // If the prompt failed, create a button programmatically
                const googleOneTabDiv = document.createElement('div');
                googleOneTabDiv.id = 'google-onetap-button';
                googleOneTabDiv.style.position = 'fixed';
                googleOneTabDiv.style.top = '50%';
                googleOneTabDiv.style.left = '50%';
                googleOneTabDiv.style.transform = 'translate(-50%, -50%)';
                googleOneTabDiv.style.zIndex = '9999';
                document.body.appendChild(googleOneTabDiv);

                google.accounts.id.renderButton(
                    googleOneTabDiv,
                    { theme: 'filled_blue', size: 'large', width: 280 }
                );

                // Create a background overlay
                const overlay = document.createElement('div');
                overlay.style.position = 'fixed';
                overlay.style.top = '0';
                overlay.style.left = '0';
                overlay.style.width = '100%';
                overlay.style.height = '100%';
                overlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
                overlay.style.zIndex = '9998';
                overlay.onclick = () => {
                    document.body.removeChild(overlay);
                    document.body.removeChild(googleOneTabDiv);
                };
                document.body.appendChild(overlay);
            }
        });
    } catch (error) {
        console.error('Error triggering Google Sign-In:', error);
        showNotification('오류', 'Google 로그인을 시도하는 중 오류가 발생했습니다.', 'error');
    }
}

// Handle Google Sign-In response
function handleGoogleCredentialResponse(response) {
    console.log('Google Sign-In response received!', response);
    // Make this function available globally
    window.handleGoogleCredentialResponse = handleGoogleCredentialResponse;

    // Check if we have an error
    if (response.error) {
        console.error('Google Sign-In error:', response.error);
        let errorMsg = '알 수 없는 오류가 발생했습니다.';

        switch (response.error) {
            case 'popup_closed_by_user':
                errorMsg = '로그인 창이 닫혔습니다.';
                break;
            case 'access_denied':
                errorMsg = '로그인 접근이 거부되었습니다.';
                break;
            case 'immediate_failed':
                errorMsg = '자동 로그인에 실패했습니다.';
                break;
            case 'invalid_client':
                errorMsg = '클라이언트 ID가 유효하지 않습니다. 개발자에게 문의하세요.';
                break;
        }

        showNotification('로그인 실패', errorMsg, 'error');
        return;
    }

    // Send the ID token to your backend
    const idToken = response.credential;

    fetch('/api/users/google-auth/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id_token: idToken })
    })
        .then(response => response.json())
        .then(data => {
            if (data.access_token) {
                // Save token and user data
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));

                // Show success message
                showNotification('로그인 성공', '구글 계정으로 로그인되었습니다.', 'success');

                // Close login modal
                hideLoginModal();

                // Update UI for logged in user
                updateUserUI();

                // Redirect if it's a new user
                if (data.is_new_user) {
                    showNotification('환영합니다!', '계정이 생성되었습니다.', 'success');
                }
            } else {
                showNotification('로그인 실패', data.message || '구글 로그인에 실패했습니다.', 'error');
            }
        })
        .catch(error => {
            console.error('Google login error:', error);
            showNotification('로그인 오류', '서버 오류가 발생했습니다.', 'error');
        });
}

// Note: The actual loginWithGoogle and registerWithGoogle functions 
// are defined in app.js and they will call the Google Sign-In API

// Initialize Google auth when page loads
document.addEventListener('DOMContentLoaded', () => {
    initGoogleAuth();

    // Add a custom button for Google authentication
    google.accounts.id.renderButton(
        document.getElementById('google-signin-button') || document.createElement('div'),
        { theme: 'outline', size: 'large' }
    );
});
