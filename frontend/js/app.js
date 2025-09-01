// 글로벌 변수
let currentUser = null;
let currentPage = 1;
let totalPages = 1;
let charts = [];
let selectedStock = null;

// API 기본 URL
const API_BASE_URL = 'http://localhost:8000/api';

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeCharts();
    loadCharts();
    loadRanking('accuracy');
    loadEvents();
    setupEventListeners();
});

// 앱 초기화
function initializeApp() {
    // 로그인 상태 확인
    const token = localStorage.getItem('accessToken');
    if (token) {
        validateToken(token);
    }
    
    // 모바일 네비게이션 설정
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });
    
    // 네비게이션 링크 클릭시 메뉴 닫기
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
        });
    });
}

// 차트 초기화
function initializeCharts() {
    // 히어로 섹션 차트
    const heroChartElement = document.getElementById('heroChart');
    if (heroChartElement) {
        const heroChart = LightweightCharts.createChart(heroChartElement, {
            width: heroChartElement.clientWidth,
            height: 400,
            layout: {
                background: { color: 'transparent' },
                textColor: 'white',
            },
            grid: {
                vertLines: { color: 'rgba(255,255,255,0.1)' },
                horzLines: { color: 'rgba(255,255,255,0.1)' },
            },
            rightPriceScale: {
                borderColor: 'rgba(255,255,255,0.2)',
            },
            timeScale: {
                borderColor: 'rgba(255,255,255,0.2)',
            },
        });
        
        // 샘플 데이터
        const sampleData = generateSampleData();
        const lineSeries = heroChart.addLineSeries({
            color: '#ffd700',
            lineWidth: 2,
        });
        lineSeries.setData(sampleData);
    }
    
    // 예측 차트
    const predictionChartElement = document.getElementById('predictionChart');
    if (predictionChartElement) {
        const predictionChart = LightweightCharts.createChart(predictionChartElement, {
            width: predictionChartElement.clientWidth,
            height: 400,
        });
    }
}

// 샘플 데이터 생성
function generateSampleData() {
    const data = [];
    const startPrice = 50000;
    let price = startPrice;
    const startDate = new Date('2024-01-01');
    
    for (let i = 0; i < 100; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        
        price += (Math.random() - 0.5) * 2000;
        data.push({
            time: date.toISOString().split('T')[0],
            value: Math.max(price, 10000)
        });
    }
    
    return data;
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 로그인 폼
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // 회원가입 폼
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // 예측 관련
    const stockSelect = document.getElementById('stockSelect');
    if (stockSelect) {
        loadStocks();
        stockSelect.addEventListener('change', handleStockChange);
    }
    
    // 필터 및 검색
    const marketFilter = document.getElementById('marketFilter');
    const statusFilter = document.getElementById('statusFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (marketFilter) marketFilter.addEventListener('change', filterCharts);
    if (statusFilter) statusFilter.addEventListener('change', filterCharts);
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterCharts, 300));
    }
    
    // 페이지네이션
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    
    if (prevPage) prevPage.addEventListener('click', () => changePage(currentPage - 1));
    if (nextPage) nextPage.addEventListener('click', () => changePage(currentPage + 1));
}

// 토큰 검증
async function validateToken(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            const userData = await response.json();
            currentUser = userData;
            updateUIForLoggedInUser();
        } else {
            localStorage.removeItem('accessToken');
        }
    } catch (error) {
        console.error('토큰 검증 실패:', error);
        localStorage.removeItem('accessToken');
    }
}

// 로그인 처리
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access_token);
            currentUser = data.user;
            updateUIForLoggedInUser();
            hideLoginModal();
            showNotification('로그인에 성공했습니다!', 'success');
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || '로그인에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('로그인 오류:', error);
        showNotification('로그인 중 오류가 발생했습니다.', 'error');
    }
}

// 회원가입 처리
async function handleSignup(event) {
    event.preventDefault();
    
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const passwordConfirm = document.getElementById('signupPasswordConfirm').value;
    const referralCode = document.getElementById('referralCode').value;
    
    if (password !== passwordConfirm) {
        showNotification('비밀번호가 일치하지 않습니다.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password,
                referral_code: referralCode
            }),
        });
        
        if (response.ok) {
            hideSignupModal();
            showNotification('회원가입이 완료되었습니다! 로그인해주세요.', 'success');
            showLoginModal();
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || '회원가입에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('회원가입 오류:', error);
        showNotification('회원가입 중 오류가 발생했습니다.', 'error');
    }
}

// Google 로그인
function loginWithGoogle() {
    // Google OAuth 구현
    showNotification('Google 로그인 기능을 준비중입니다.', 'info');
}

// Apple 로그인
function loginWithApple() {
    // Apple OAuth 구현
    showNotification('Apple 로그인 기능을 준비중입니다.', 'info');
}

// 로그인된 사용자 UI 업데이트
function updateUIForLoggedInUser() {
    const loginBtn = document.querySelector('.login-btn');
    if (loginBtn && currentUser) {
        loginBtn.textContent = `${currentUser.username}님`;
        loginBtn.onclick = showUserMenu;
    }
}

// 종목 목록 로드
async function loadStocks() {
    try {
        const response = await fetch(`${API_BASE_URL}/stocks/`);
        if (response.ok) {
            const stocks = await response.json();
            const stockSelect = document.getElementById('stockSelect');
            
            stockSelect.innerHTML = '<option value="">종목을 선택하세요</option>';
            stocks.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.id;
                option.textContent = `${stock.name} (${stock.symbol})`;
                option.dataset.currentPrice = stock.current_price || 0;
                stockSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('종목 로드 오류:', error);
    }
}

// 종목 변경 처리
function handleStockChange(event) {
    const selectedOption = event.target.selectedOptions[0];
    if (selectedOption && selectedOption.value) {
        selectedStock = {
            id: selectedOption.value,
            name: selectedOption.textContent,
            currentPrice: parseFloat(selectedOption.dataset.currentPrice) || 0
        };
        
        document.getElementById('currentPrice').value = selectedStock.currentPrice;
        loadStockChart(selectedStock.id);
    }
}

// 주식 차트 로드
async function loadStockChart(stockId) {
    try {
        const response = await fetch(`${API_BASE_URL}/stocks/${stockId}/chart/`);
        if (response.ok) {
            const chartData = await response.json();
            updatePredictionChart(chartData);
        }
    } catch (error) {
        console.error('차트 로드 오류:', error);
    }
}

// 예측 차트 업데이트
function updatePredictionChart(data) {
    const chartElement = document.getElementById('predictionChart');
    if (chartElement && data) {
        // 기존 차트 제거
        chartElement.innerHTML = '';
        
        // 새 차트 생성
        const chart = LightweightCharts.createChart(chartElement, {
            width: chartElement.clientWidth,
            height: 400,
        });
        
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        });
        
        candlestickSeries.setData(data);
    }
}

// 예측 저장
async function submitPrediction() {
    if (!currentUser) {
        showNotification('예측을 저장하려면 로그인이 필요합니다.', 'warning');
        showLoginModal();
        return;
    }
    
    const stockId = document.getElementById('stockSelect').value;
    const predictedPrice = document.getElementById('predictedPrice').value;
    const targetDate = document.getElementById('targetDate').value;
    const duration = document.getElementById('duration').value;
    const isPublic = document.getElementById('isPublic').checked;
    
    if (!stockId || !predictedPrice || !targetDate) {
        showNotification('모든 필드를 입력해주세요.', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/predictions/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stock_id: stockId,
                predicted_price: predictedPrice,
                target_date: targetDate,
                duration_days: duration,
                is_public: isPublic
            }),
        });
        
        if (response.ok) {
            showNotification('예측이 성공적으로 저장되었습니다!', 'success');
            clearPredictionForm();
            loadCharts(); // 차트 목록 새로고침
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || '예측 저장에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('예측 저장 오류:', error);
        showNotification('예측 저장 중 오류가 발생했습니다.', 'error');
    }
}

// 예측 폼 초기화
function clearPredictionForm() {
    document.getElementById('stockSelect').value = '';
    document.getElementById('currentPrice').value = '';
    document.getElementById('predictedPrice').value = '';
    document.getElementById('targetDate').value = '';
    document.getElementById('duration').value = '7';
    document.getElementById('isPublic').checked = true;
}

// 차트 목록 로드
async function loadCharts(page = 1) {
    try {
        const marketFilter = document.getElementById('marketFilter').value;
        const statusFilter = document.getElementById('statusFilter').value;
        const searchTerm = document.getElementById('searchInput').value;
        
        let url = `${API_BASE_URL}/predictions/?page=${page}`;
        if (marketFilter) url += `&market=${marketFilter}`;
        if (statusFilter) url += `&status=${statusFilter}`;
        if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
        
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            charts = data.results;
            currentPage = page;
            totalPages = Math.ceil(data.count / 20);
            
            renderCharts();
            updatePagination();
        }
    } catch (error) {
        console.error('차트 로드 오류:', error);
    }
}

// 차트 렌더링
function renderCharts() {
    const chartsGrid = document.getElementById('chartsGrid');
    if (!chartsGrid) return;
    
    chartsGrid.innerHTML = '';
    
    if (charts.length === 0) {
        chartsGrid.innerHTML = '<p class="no-results">검색 결과가 없습니다.</p>';
        return;
    }
    
    charts.forEach(chart => {
        const chartCard = createChartCard(chart);
        chartsGrid.appendChild(chartCard);
    });
}

// 차트 카드 생성
function createChartCard(chart) {
    const card = document.createElement('div');
    card.className = 'chart-card';
    
    const statusClass = chart.status === 'completed' ? 'status-completed' : 'status-pending';
    const statusText = chart.status === 'completed' ? '완료됨' : '예측 중';
    
    const profitRate = chart.profit_rate ? `${chart.profit_rate}%` : '-';
    const accuracy = chart.accuracy_percentage ? `${chart.accuracy_percentage}%` : '-';
    
    card.innerHTML = `
        <div class="chart-header">
            <div class="chart-title">${chart.stock.name} (${chart.stock.symbol})</div>
            <span class="chart-status ${statusClass}">${statusText}</span>
        </div>
        <div class="chart-info">
            <div><span>예측자:</span> <span>${chart.user.username}</span></div>
            <div><span>현재 가격:</span> <span>₩${chart.current_price.toLocaleString()}</span></div>
            <div><span>예측 가격:</span> <span>₩${chart.predicted_price.toLocaleString()}</span></div>
            <div><span>목표일:</span> <span>${new Date(chart.target_date).toLocaleDateString()}</span></div>
            <div><span>수익률:</span> <span>${profitRate}</span></div>
            <div><span>정확도:</span> <span>${accuracy}</span></div>
        </div>
        <div class="chart-actions">
            <span><i class="fas fa-eye"></i> ${chart.views_count}</span>
            <span><i class="fas fa-heart"></i> ${chart.likes_count}</span>
            <span><i class="fas fa-comment"></i> ${chart.comments_count}</span>
            <button class="btn btn-outline btn-sm" onclick="viewChart(${chart.id})">상세보기</button>
        </div>
    `;
    
    return card;
}

// 차트 필터링
function filterCharts() {
    loadCharts(1);
}

// 페이지 변경
function changePage(page) {
    if (page >= 1 && page <= totalPages) {
        loadCharts(page);
    }
}

// 페이지네이션 업데이트
function updatePagination() {
    const pageInfo = document.getElementById('pageInfo');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    
    if (pageInfo) {
        pageInfo.textContent = `${currentPage} / ${totalPages}`;
    }
    
    if (prevPage) {
        prevPage.disabled = currentPage <= 1;
    }
    
    if (nextPage) {
        nextPage.disabled = currentPage >= totalPages;
    }
}

// 랭킹 로드
async function loadRanking(type) {
    try {
        const response = await fetch(`${API_BASE_URL}/rankings/${type}/`);
        if (response.ok) {
            const rankings = await response.json();
            renderRanking(rankings, type);
        }
    } catch (error) {
        console.error('랭킹 로드 오류:', error);
    }
}

// 랭킹 렌더링
function renderRanking(rankings, type) {
    const rankingTable = document.getElementById('rankingTable');
    if (!rankingTable) return;
    
    let headers, getValue;
    
    switch (type) {
        case 'accuracy':
            headers = ['순위', '사용자', '정확도', '예측 수', '평균 수익률'];
            getValue = (user) => [user.rank, user.username, `${user.prediction_accuracy}%`, user.prediction_count, `${user.avg_profit_rate}%`];
            break;
        case 'profit':
            headers = ['순위', '사용자', '총 수익률', '예측 수', '정확도'];
            getValue = (user) => [user.rank, user.username, `${user.total_profit}%`, user.prediction_count, `${user.prediction_accuracy}%`];
            break;
        case 'predictions':
            headers = ['순위', '사용자', '예측 수', '정확도', '평균 수익률'];
            getValue = (user) => [user.rank, user.username, user.prediction_count, `${user.prediction_accuracy}%`, `${user.avg_profit_rate}%`];
            break;
    }
    
    rankingTable.innerHTML = `
        <div class="ranking-header">
            ${headers.map(header => `<span>${header}</span>`).join('')}
        </div>
        ${rankings.map(user => `
            <div class="ranking-row">
                ${getValue(user).map(value => `<span>${value}</span>`).join('')}
            </div>
        `).join('')}
    `;
}

// 랭킹 탭 변경
function showRanking(type) {
    // 탭 버튼 활성화 상태 변경
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadRanking(type);
}

// 이벤트 로드
async function loadEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/events/`);
        if (response.ok) {
            const events = await response.json();
            renderEvents(events);
        }
    } catch (error) {
        console.error('이벤트 로드 오류:', error);
    }
}

// 이벤트 렌더링
function renderEvents(events) {
    const eventsGrid = document.getElementById('eventsGrid');
    if (!eventsGrid) return;
    
    eventsGrid.innerHTML = '';
    
    events.forEach(event => {
        const eventCard = createEventCard(event);
        eventsGrid.appendChild(eventCard);
    });
}

// 이벤트 카드 생성
function createEventCard(event) {
    const card = document.createElement('div');
    card.className = 'event-card';
    
    const statusClass = event.status === 'active' ? 'status-active' : 'status-upcoming';
    const statusText = event.status === 'active' ? '진행중' : '예정';
    
    card.innerHTML = `
        <span class="event-status ${statusClass}">${statusText}</span>
        <h3>${event.title}</h3>
        <p>${event.description}</p>
        <div class="event-info">
            <div><strong>시작일:</strong> ${new Date(event.start_date).toLocaleDateString()}</div>
            <div><strong>종료일:</strong> ${new Date(event.end_date).toLocaleDateString()}</div>
            <div><strong>상금:</strong> ${event.prize_description}</div>
            <div><strong>참가자:</strong> ${event.participants_count}명</div>
        </div>
        <button class="btn btn-primary" onclick="participateEvent(${event.id})">참가하기</button>
    `;
    
    return card;
}

// 이벤트 참가
async function participateEvent(eventId) {
    if (!currentUser) {
        showNotification('이벤트 참가하려면 로그인이 필요합니다.', 'warning');
        showLoginModal();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/events/${eventId}/participate/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            showNotification('이벤트에 성공적으로 참가했습니다!', 'success');
            loadEvents(); // 이벤트 목록 새로고침
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || '이벤트 참가에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('이벤트 참가 오류:', error);
        showNotification('이벤트 참가 중 오류가 발생했습니다.', 'error');
    }
}

// 구독 처리
async function subscribePlan(planType) {
    if (!currentUser) {
        showNotification('구독하려면 로그인이 필요합니다.', 'warning');
        showLoginModal();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/payments/subscribe/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ plan_type: planType }),
        });
        
        if (response.ok) {
            const data = await response.json();
            // PayPal 결제 페이지로 리다이렉트
            window.location.href = data.payment_url;
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || '구독 처리에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('구독 오류:', error);
        showNotification('구독 처리 중 오류가 발생했습니다.', 'error');
    }
}

// 유틸리티 함수들
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

function hideLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function showSignupModal() {
    hideLoginModal();
    document.getElementById('signupModal').style.display = 'block';
}

function hideSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
}

function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({
        behavior: 'smooth'
    });
}

function viewChart(chartId) {
    // 차트 상세 페이지로 이동 또는 모달 표시
    showNotification('차트 상세 보기 기능을 준비중입니다.', 'info');
}

function showNotification(message, type = 'info') {
    // 알림 표시 (토스트 메시지)
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 스타일 적용
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 3000;
        animation: slideIn 0.3s ease;
    `;
    
    // 타입별 배경색
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196F3'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // 3초 후 제거
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .no-results {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin: 2rem 0;
    }
    
    .btn-sm {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
`;
document.head.appendChild(style);
