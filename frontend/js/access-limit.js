// Access Limit Functionality

// Check if we need to show the free access limit alert
function checkFreeAccessLimit() {
    // Get query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const paymentRequired = urlParams.get('payment_required') === 'true';
    const visitCount = parseInt(urlParams.get('visit_count') || '0');
    
    // If this is the subscription page and payment is required
    if (window.location.pathname.includes('subscription.html') && paymentRequired) {
        const freeAccessAlert = document.getElementById('freeAccessAlert');
        const accessCountSpan = document.getElementById('accessCount');
        
        if (freeAccessAlert && accessCountSpan) {
            freeAccessAlert.style.display = 'block';
            accessCountSpan.textContent = `${visitCount}/3`;
        }
    }
}

// Check if user is authenticated
function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}

// Free access tracking
function trackPremiumContentAccess() {
    // Only track if not authenticated
    if (!isAuthenticated()) {
        let accessCount = parseInt(localStorage.getItem('freeAccessCount') || '0');
        accessCount++;
        localStorage.setItem('freeAccessCount', accessCount);
        
        // Check if we need to show a warning
        if (accessCount >= 3) {
            showFreeAccessLimitWarning();
        }
    }
}

// Show warning about free access limits
function showFreeAccessLimitWarning() {
    // Only show if not authenticated
    if (!isAuthenticated() && !window.location.pathname.includes('subscription.html')) {
        // Create a warning banner at the top of the page
        const warningBanner = document.createElement('div');
        warningBanner.className = 'free-access-alert';
        warningBanner.innerHTML = `
            <h3>⚠️ 무료 접근 횟수에 제한이 있습니다</h3>
            <p>무료 사용자는 프리미엄 콘텐츠에 <span class="access-counter">3</span>번의 접근만 가능합니다.</p>
            <p>접근 횟수: <span class="limit-badge">${localStorage.getItem('freeAccessCount')}/3</span></p>
            <a href="subscription.html" class="btn btn-upgrade">구독 알아보기</a>
        `;
        
        // Insert at the top of the content
        const content = document.querySelector('.section');
        if (content && content.parentNode) {
            content.parentNode.insertBefore(warningBanner, content);
        }
    }
}

// Check premium content pages
function isPremiumContentPage() {
    const premiumPages = [
        'charts.html',
        'prediction.html',
        'my-predictions.html',
        'ranking.html'
    ];
    
    return premiumPages.some(page => window.location.pathname.includes(page));
}

// Initialize access tracking
function initializeAccessTracking() {
    // Check if this is a premium content page
    if (isPremiumContentPage()) {
        trackPremiumContentAccess();
    }
    
    // Check if we need to show the free access limit alert on subscription page
    checkFreeAccessLimit();
}

// Add this function to the DOMContentLoaded event handler
document.addEventListener('DOMContentLoaded', function() {
    initializeAccessTracking();
});
