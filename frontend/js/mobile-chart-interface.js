/**
 * Mobile-First Touch Optimized Chart Interface
 * Designed for seamless touch interactions on mobile devices
 */

class MobileChartInterface {
    constructor(container) {
        this.container = container;
        this.chart = null;
        this.searchInput = null;
        
        this.init();
    }
    
    init() {
        this.createMobileInterface();
        this.setupTouchHandlers();
        this.setupSearchInterface();
    }
    
    createMobileInterface() {
        this.container.innerHTML = `
            <div class="mobile-chart-app">
                <!-- Mobile Header -->
                <div class="mobile-header">
                    <div class="logo">
                        <div class="logo-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="logo-text">
                            <span class="logo-title">StockChart</span>
                            <span class="logo-subtitle">Pro</span>
                        </div>
                    </div>
                    <div class="header-actions">
                        <button class="header-btn notification-btn">
                            <i class="fas fa-bell"></i>
                            <span class="notification-dot"></span>
                        </button>
                        <button class="header-btn profile-btn">
                            <i class="fas fa-user-circle"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Search Bar -->
                <div class="search-section">
                    <div class="search-container">
                        <i class="fas fa-search search-icon"></i>
                        <input type="text" class="search-input" placeholder="주식 검색 (예: 삼성전자, AAPL)" autocomplete="off">
                        <button class="voice-search-btn">
                            <i class="fas fa-microphone"></i>
                        </button>
                        <div class="search-suggestions"></div>
                    </div>
                </div>
                
                <!-- Chart Container -->
                <div class="chart-container">
                    <div class="stock-info-card">
                        <div class="stock-header">
                            <div class="stock-symbol">AAPL</div>
                            <div class="market-status">
                                <span class="status-dot"></span>
                                <span class="status-text">실시간</span>
                            </div>
                        </div>
                        <div class="stock-price">$175.43</div>
                        <div class="price-change positive">
                            <span class="change-amount">+2.15</span>
                            <span class="change-percent">(+1.24%)</span>
                        </div>
                        <div class="price-indicators">
                            <div class="indicator">
                                <span class="label">시가</span>
                                <span class="value">$173.28</span>
                            </div>
                            <div class="indicator">
                                <span class="label">고가</span>
                                <span class="value">$176.12</span>
                            </div>
                            <div class="indicator">
                                <span class="label">저가</span>
                                <span class="value">$172.85</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chart-wrapper">
                        <canvas class="chart-canvas"></canvas>
                        
                        <!-- Touch Instructions -->
                        <div class="touch-instructions">
                            <div class="instruction-card">
                                <div class="instruction-icon">
                                    <i class="fas fa-hand-pointer"></i>
                                </div>
                                <div class="instruction-content">
                                    <h3>터치하여 예측하세요</h3>
                                    <p>차트를 터치하여 AI 기반 가격 예측을 추가하세요</p>
                                    <div class="instruction-features">
                                        <span class="feature">• 실시간 분석</span>
                                        <span class="feature">• 정확한 예측</span>
                                        <span class="feature">• 수익률 추적</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Chart Controls -->
                        <div class="chart-controls">
                            <div class="control-group left">
                                <button class="control-btn zoom-out" title="축소">
                                    <i class="fas fa-search-minus"></i>
                                </button>
                                <button class="control-btn zoom-in" title="확대">
                                    <i class="fas fa-search-plus"></i>
                                </button>
                                <button class="control-btn reset" title="리셋">
                                    <i class="fas fa-expand"></i>
                                </button>
                            </div>
                            <div class="control-group right">
                                <button class="control-btn indicator-btn" title="지표">
                                    <i class="fas fa-chart-bar"></i>
                                </button>
                                <button class="control-btn settings-btn" title="설정">
                                    <i class="fas fa-cog"></i>
                                </button>
                            </div>
                        </div>
                        
                        <!-- Time Frame Selector -->
                        <div class="timeframe-selector">
                            <button class="timeframe-btn active" data-timeframe="1D">1일</button>
                            <button class="timeframe-btn" data-timeframe="1W">1주</button>
                            <button class="timeframe-btn" data-timeframe="1M">1개월</button>
                            <button class="timeframe-btn" data-timeframe="3M">3개월</button>
                            <button class="timeframe-btn" data-timeframe="1Y">1년</button>
                        </div>
                    </div>
                </div>
                
                <!-- Predictions Panel -->
                <div class="predictions-panel hidden">
                    <div class="panel-header">
                        <div class="panel-title">
                            <h3>내 예측</h3>
                            <span class="prediction-count">3개</span>
                        </div>
                        <div class="panel-actions">
                            <button class="action-btn sort-btn">
                                <i class="fas fa-sort"></i>
                            </button>
                            <button class="action-btn clear-btn">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="predictions-stats">
                        <div class="stat-card">
                            <span class="stat-label">총 수익률</span>
                            <span class="stat-value positive">+12.5%</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">적중률</span>
                            <span class="stat-value">73%</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">평균 수익</span>
                            <span class="stat-value positive">+4.2%</span>
                        </div>
                    </div>
                    
                    <div class="predictions-list">
                        <!-- Predictions will be dynamically added here -->
                    </div>
                    
                    <div class="panel-footer">
                        <button class="premium-btn">
                            <i class="fas fa-crown"></i>
                            프리미엄으로 업그레이드
                        </button>
                        <button class="share-btn">
                            <i class="fas fa-share-alt"></i>
                            예측 공유하기
                        </button>
                    </div>
                </div>
                
                <!-- Bottom Navigation -->
                <div class="bottom-nav">
                    <button class="nav-btn active" data-tab="chart">
                        <div class="nav-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <span class="nav-label">차트</span>
                        <div class="nav-indicator"></div>
                    </button>
                    <button class="nav-btn" data-tab="predictions">
                        <div class="nav-icon">
                            <i class="fas fa-brain"></i>
                            <span class="nav-badge">3</span>
                        </div>
                        <span class="nav-label">예측</span>
                        <div class="nav-indicator"></div>
                    </button>
                    <button class="nav-btn" data-tab="portfolio">
                        <div class="nav-icon">
                            <i class="fas fa-briefcase"></i>
                        </div>
                        <span class="nav-label">포트폴리오</span>
                        <div class="nav-indicator"></div>
                    </button>
                    <button class="nav-btn" data-tab="social">
                        <div class="nav-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <span class="nav-label">소셜</span>
                        <div class="nav-indicator"></div>
                    </button>
                    <button class="nav-btn" data-tab="more">
                        <div class="nav-icon">
                            <i class="fas fa-ellipsis-h"></i>
                        </div>
                        <span class="nav-label">더보기</span>
                        <div class="nav-indicator"></div>
                    </button>
                </div>
                
                <!-- Toast Container -->
                <div class="toast-container"></div>
            </div>
        `;
        
        this.applyMobileStyles();
    }
    
    applyMobileStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .mobile-chart-app {
                height: 100vh;
                display: flex;
                flex-direction: column;
                background: #1e222d;
                color: #d1d4dc;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                overflow: hidden;
            }
            
            .mobile-header {
                background: #2a2e39;
                padding: 12px 16px;
                border-bottom: 1px solid #363a45;
                position: relative;
                z-index: 100;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: bold;
                color: #2962ff;
                margin-bottom: 12px;
            }
            
            .search-container {
                position: relative;
                background: #363a45;
                border-radius: 12px;
                display: flex;
                align-items: center;
                padding: 12px 16px;
                transition: all 0.2s ease;
            }
            
            .search-container:focus-within {
                background: #404653;
                box-shadow: 0 0 0 2px rgba(41, 98, 255, 0.3);
            }
            
            .search-icon {
                color: #868993;
                margin-right: 12px;
            }
            
            .search-input {
                flex: 1;
                background: transparent;
                border: none;
                outline: none;
                color: #d1d4dc;
                font-size: 16px;
                font-weight: 500;
            }
            
            .search-input::placeholder {
                color: #868993;
            }
            
            .search-suggestions {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: #2a2e39;
                border-radius: 8px;
                margin-top: 4px;
                max-height: 200px;
                overflow-y: auto;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                z-index: 1000;
                display: none;
            }
            
            .suggestion-item {
                padding: 16px;
                border-bottom: 1px solid #363a45;
                cursor: pointer;
                transition: background 0.1s ease;
            }
            
            .suggestion-item:last-child {
                border-bottom: none;
            }
            
            .suggestion-item:active {
                background: #363a45;
            }
            
            .suggestion-symbol {
                font-weight: 600;
                color: #2962ff;
                font-size: 16px;
            }
            
            .suggestion-name {
                color: #868993;
                font-size: 14px;
                margin-top: 2px;
            }
            
            .chart-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chart-header {
                background: #2a2e39;
                padding: 16px;
                border-bottom: 1px solid #363a45;
            }
            
            .stock-info {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .stock-symbol {
                font-size: 20px;
                font-weight: 700;
                color: #2962ff;
            }
            
            .stock-price {
                font-size: 18px;
                font-weight: 600;
            }
            
            .price-up {
                color: #26a69a;
            }
            
            .price-down {
                color: #ef5350;
            }
            
            .chart-wrapper {
                flex: 1;
                position: relative;
                background: #1e222d;
            }
            
            .chart-canvas {
                width: 100%;
                height: 100%;
                touch-action: none;
                cursor: crosshair;
            }
            
            .touch-instructions {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                pointer-events: none;
                z-index: 10;
            }
            
            .instruction-card {
                background: rgba(42, 46, 57, 0.95);
                padding: 24px;
                border-radius: 16px;
                border: 1px solid #363a45;
                backdrop-filter: blur(10px);
            }
            
            .instruction-card i {
                font-size: 32px;
                color: #2962ff;
                margin-bottom: 12px;
                display: block;
            }
            
            .instruction-card h3 {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            .instruction-card p {
                color: #868993;
                font-size: 14px;
            }
            
            .chart-controls {
                position: absolute;
                top: 16px;
                right: 16px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .control-btn {
                width: 44px;
                height: 44px;
                background: rgba(42, 46, 57, 0.9);
                border: 1px solid #363a45;
                border-radius: 8px;
                color: #d1d4dc;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
                backdrop-filter: blur(10px);
            }
            
            .control-btn:active {
                background: #363a45;
                transform: scale(0.95);
            }
            
            .predictions-panel {
                background: #2a2e39;
                border-top: 1px solid #363a45;
                padding: 20px;
                max-height: 300px;
                overflow-y: auto;
            }
            
            .panel-header {
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 16px;
            }
            
            .panel-header h3 {
                font-size: 18px;
                font-weight: 600;
                margin: 0;
            }
            
            .clear-btn {
                background: none;
                border: none;
                color: #ef5350;
                font-size: 14px;
                cursor: pointer;
                padding: 4px 8px;
            }
            
            .predictions-list {
                space-y: 12px;
                margin-bottom: 20px;
            }
            
            .prediction-item {
                background: #363a45;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 12px;
                display: flex;
                justify-content: between;
                align-items: center;
            }
            
            .prediction-date {
                font-size: 14px;
                color: #868993;
            }
            
            .prediction-price {
                font-size: 16px;
                font-weight: 600;
                margin: 4px 0;
            }
            
            .prediction-change {
                font-size: 14px;
                font-weight: 500;
            }
            
            .remove-btn {
                background: none;
                border: none;
                color: #ef5350;
                font-size: 16px;
                cursor: pointer;
                padding: 8px;
                border-radius: 6px;
            }
            
            .remove-btn:active {
                background: rgba(239, 83, 80, 0.1);
            }
            
            .share-btn {
                width: 100%;
                background: linear-gradient(90deg, #2962ff, #1e88e5);
                border: none;
                color: white;
                padding: 16px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: all 0.2s ease;
            }
            
            .share-btn:active {
                transform: scale(0.98);
            }
            
            .bottom-nav {
                background: #2a2e39;
                border-top: 1px solid #363a45;
                display: flex;
                padding: 8px 0;
            }
            
            .nav-btn {
                flex: 1;
                background: none;
                border: none;
                color: #868993;
                padding: 12px 8px;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 4px;
                transition: color 0.2s ease;
            }
            
            .nav-btn.active {
                color: #2962ff;
            }
            
            .nav-btn i {
                font-size: 18px;
            }
            
            .nav-btn span {
                font-size: 12px;
                font-weight: 500;
            }
            
            .toast-container {
                position: fixed;
                top: 20px;
                left: 20px;
                right: 20px;
                z-index: 9999;
                pointer-events: none;
            }
            
            .toast {
                background: #2a2e39;
                border: 1px solid #363a45;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 12px;
                transform: translateY(-100px);
                opacity: 0;
                transition: all 0.3s ease;
                pointer-events: auto;
            }
            
            .toast.show {
                transform: translateY(0);
                opacity: 1;
            }
            
            .toast.success {
                border-left: 4px solid #26a69a;
            }
            
            .toast.error {
                border-left: 4px solid #ef5350;
            }
            
            .toast.info {
                border-left: 4px solid #2962ff;
            }
            
            .hidden {
                display: none !important;
            }
            
            /* Smooth scrolling */
            .predictions-panel,
            .search-suggestions {
                -webkit-overflow-scrolling: touch;
            }
            
            /* Safe area handling for notched devices */
            @supports (padding-top: env(safe-area-inset-top)) {
                .mobile-header {
                    padding-top: calc(12px + env(safe-area-inset-top));
                }
                
                .bottom-nav {
                    padding-bottom: calc(8px + env(safe-area-inset-bottom));
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    setupTouchHandlers() {
        // Enhanced touch handlers for modern fintech experience
        this.setupNavigationHandlers();
        this.setupChartInteractions();
        this.setupAdvancedTouchGestures();
        this.setupPredictionPanelHandlers();
        console.log('Enhanced touch handlers setup completed');
    }
    
    setupNavigationHandlers() {
        const navButtons = this.container.querySelectorAll('.nav-btn');
        const panels = {
            chart: this.container.querySelector('.chart-container'),
            predictions: this.container.querySelector('.predictions-panel')
        };
        
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active state from all buttons
                navButtons.forEach(b => b.classList.remove('active'));
                
                // Add active state to clicked button
                btn.classList.add('active');
                
                const tab = btn.dataset.tab;
                this.switchToTab(tab, panels);
                
                // Haptic feedback
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            });
        });
    }
    
    setupChartInteractions() {
        const controlBtns = this.container.querySelectorAll('.control-btn');
        const timeframeBtns = this.container.querySelectorAll('.timeframe-btn');
        
        // Chart control handlers
        controlBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                
                const action = btn.classList.contains('zoom-in') ? 'zoomIn' :
                              btn.classList.contains('zoom-out') ? 'zoomOut' :
                              btn.classList.contains('reset') ? 'reset' :
                              btn.classList.contains('indicator-btn') ? 'indicators' :
                              btn.classList.contains('settings-btn') ? 'settings' : null;
                
                if (action) {
                    this.handleChartAction(action);
                    
                    // Visual feedback
                    btn.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        btn.style.transform = '';
                    }, 150);
                    
                    // Haptic feedback
                    if (navigator.vibrate) {
                        navigator.vibrate(30);
                    }
                }
            });
        });
        
        // Timeframe selector handlers
        timeframeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active state from all timeframe buttons
                timeframeBtns.forEach(b => b.classList.remove('active'));
                
                // Add active state to clicked button
                btn.classList.add('active');
                
                const timeframe = btn.dataset.timeframe;
                this.changeTimeframe(timeframe);
                
                // Haptic feedback
                if (navigator.vibrate) {
                    navigator.vibrate(40);
                }
            });
        });
    }
    
    setupAdvancedTouchGestures() {
        const canvas = this.container.querySelector('.chart-canvas');
        let touchStartX, touchStartY, touchStartTime;
        let isTouch = false;
        let lastTap = 0;
        
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            isTouch = true;
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            touchStartTime = Date.now();
            
            // Double tap detection
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTap;
            if (tapLength < 500 && tapLength > 0) {
                this.handleDoubleTap(e.touches[0]);
            }
            lastTap = currentTime;
        }, { passive: false });
        
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!isTouch) return;
            
            const deltaX = e.touches[0].clientX - touchStartX;
            const deltaY = e.touches[0].clientY - touchStartY;
            
            // Handle chart panning
            this.handleChartPan(deltaX, deltaY);
        }, { passive: false });
        
        canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (!isTouch) return;
            
            const touchEndTime = Date.now();
            const touchDuration = touchEndTime - touchStartTime;
            
            // Quick tap for prediction
            if (touchDuration < 300) {
                const rect = canvas.getBoundingClientRect();
                const x = e.changedTouches[0].clientX - rect.left;
                const y = e.changedTouches[0].clientY - rect.top;
                
                this.addPrediction(x, y);
                
                // Strong haptic feedback for prediction
                if (navigator.vibrate) {
                    navigator.vibrate(100);
                }
            }
            
            isTouch = false;
        }, { passive: false });
    }
    
    setupPredictionPanelHandlers() {
        const clearBtn = this.container.querySelector('.clear-btn');
        const sortBtn = this.container.querySelector('.sort-btn');
        const shareBtn = this.container.querySelector('.share-btn');
        const premiumBtn = this.container.querySelector('.premium-btn');
        
        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearAllPredictions();
            });
        }
        
        if (sortBtn) {
            sortBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.sortPredictions();
            });
        }
        
        if (shareBtn) {
            shareBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.sharePredictions();
            });
        }
        
        if (premiumBtn) {
            premiumBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showPremiumUpgrade();
            });
        }
    }
    
    setupSearchInterface() {
        const searchInput = this.container.querySelector('.search-input');
        const suggestions = this.container.querySelector('.search-suggestions');
        const voiceBtn = this.container.querySelector('.voice-search-btn');
        
        // Enhanced search with debouncing
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = e.target.value.trim();
                if (query.length >= 1) {
                    this.showSearchSuggestions(query);
                } else {
                    this.hideSearchSuggestions();
                }
            }, 300);
        });
        
        // Voice search
        if (voiceBtn) {
            voiceBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.startVoiceSearch();
            });
        }
        
        // Focus/blur effects with smooth animations
        searchInput.addEventListener('focus', () => {
            searchInput.parentElement.classList.add('focused');
        });
        
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                searchInput.parentElement.classList.remove('focused');
                this.hideSearchSuggestions();
            }, 200);
        });
    }
    
    // Enhanced method implementations
    switchToTab(activeTab, panels) {
        // Hide all panels with smooth transitions
        Object.values(panels).forEach(panel => {
            if (panel) {
                panel.classList.add('hidden');
                panel.style.transform = 'translateX(100%)';
            }
        });
        
        // Show active panel with animation
        switch (activeTab) {
            case 'chart':
                if (panels.chart) {
                    panels.chart.classList.remove('hidden');
                    panels.chart.style.transform = 'translateX(0)';
                }
                break;
            case 'predictions':
                if (panels.predictions) {
                    panels.predictions.classList.remove('hidden');
                    panels.predictions.style.transform = 'translateX(0)';
                    this.loadPredictions();
                }
                break;
            case 'portfolio':
                this.showComingSoon('포트폴리오');
                break;
            case 'social':
                this.showComingSoon('소셜 트레이딩');
                break;
            case 'more':
                this.showMoreMenu();
                break;
        }
    }
    
    handleChartAction(action) {
        console.log(`Chart action: ${action}`);
        
        switch (action) {
            case 'zoomIn':
                this.zoomChart(1.2);
                break;
            case 'zoomOut':
                this.zoomChart(0.8);
                break;
            case 'reset':
                this.resetChart();
                break;
            case 'indicators':
                this.showIndicatorsMenu();
                break;
            case 'settings':
                this.showChartSettings();
                break;
        }
    }
    
    changeTimeframe(timeframe) {
        console.log(`Changing timeframe to: ${timeframe}`);
        
        // Show loading state
        this.showChartLoading();
        
        // Simulate API call
        setTimeout(() => {
            this.loadChartData(timeframe);
            this.hideChartLoading();
        }, 1000);
    }
    
    handleChartPan(deltaX, deltaY) {
        // Implement chart panning logic
        console.log(`Panning chart: ${deltaX}, ${deltaY}`);
    }
    
    handleDoubleTap(touch) {
        console.log('Double tap detected - auto zoom');
        this.autoZoomToArea(touch);
        
        // Enhanced haptic feedback
        if (navigator.vibrate) {
            navigator.vibrate([50, 50, 50]);
        }
    }
    
    addPrediction(x, y) {
        console.log(`Adding prediction at: ${x}, ${y}`);
        
        // Create prediction point with animation
        const predictionPoint = document.createElement('div');
        predictionPoint.className = 'prediction-point';
        predictionPoint.style.left = `${x}px`;
        predictionPoint.style.top = `${y}px`;
        
        const canvas = this.container.querySelector('.chart-canvas');
        canvas.parentElement.appendChild(predictionPoint);
        
        // Animate in
        setTimeout(() => {
            predictionPoint.classList.add('active');
        }, 10);
        
        // Update predictions panel
        this.updatePredictionsCount();
    }
    
    startVoiceSearch() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.lang = 'ko-KR';
            recognition.onresult = (event) => {
                const result = event.results[0][0].transcript;
                const searchInput = this.container.querySelector('.search-input');
                searchInput.value = result;
                this.showSearchSuggestions(result);
            };
            
            recognition.start();
            
            // Visual feedback
            const voiceBtn = this.container.querySelector('.voice-search-btn');
            voiceBtn.classList.add('listening');
            
            recognition.onend = () => {
                voiceBtn.classList.remove('listening');
            };
        } else {
            this.showToast('음성 검색을 지원하지 않는 브라우저입니다');
        }
    }
    
    showComingSoon(feature) {
        this.showToast(`${feature} 기능이 곧 출시됩니다!`);
    }
    
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    showSearchSuggestions(query) {
        const suggestions = this.container.querySelector('.search-suggestions');
        
        // Filter popular stocks
        const filtered = this.getPopularStocks().filter(stock =>
            stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        );
        
        if (filtered.length === 0) {
            suggestions.style.display = 'none';
            return;
        }
        
        const html = filtered.slice(0, 5).map(stock => `
            <div class="suggestion-item" data-symbol="${stock.symbol}">
                <div class="suggestion-symbol">${stock.symbol}</div>
                <div class="suggestion-name">${stock.name}</div>
            </div>
        `).join('');
        
        suggestions.innerHTML = html;
        suggestions.style.display = 'block';
        
        // Add click handlers
        suggestions.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectStock(item.dataset.symbol);
            });
        });
    }
    
    hideSearchSuggestions() {
        const suggestions = this.container.querySelector('.search-suggestions');
        suggestions.style.display = 'none';
    }
    
    getPopularStocks() {
        return [
            { symbol: 'AAPL', name: 'Apple Inc.' },
            { symbol: 'TSLA', name: 'Tesla Inc.' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.' },
            { symbol: 'MSFT', name: 'Microsoft Corp.' },
            { symbol: 'AMZN', name: 'Amazon.com Inc.' },
            { symbol: 'NVDA', name: 'NVIDIA Corp.' },
            { symbol: 'BTC-USD', name: 'Bitcoin' },
            { symbol: 'ETH-USD', name: 'Ethereum' },
            { symbol: '005930.KS', name: '삼성전자' },
            { symbol: '000660.KS', name: 'SK하이닉스' }
        ];
    }
    
    selectStock(symbol) {
        this.hideSearchSuggestions();
        
        const searchInput = this.container.querySelector('.search-input');
        searchInput.value = symbol;
        
        this.loadStockChart(symbol);
        this.showToast(`${symbol} 차트를 로드하고 있습니다...`, 'info');
    }
    
    loadStockChart(symbol) {
        // Initialize chart with TradingView engine
        const canvas = this.container.querySelector('.chart-canvas');
        
        if (this.chart) {
            this.chart = null;
        }
        
        this.chart = new TradingViewChart(canvas);
        
        // Generate sample data
        const data = this.generateSampleData();
        this.chart.setData(data);
        
        // Update UI
        this.updateStockInfo(symbol, data);
        this.showChart();
        
        // Hide instructions
        const instructions = this.container.querySelector('.touch-instructions');
        instructions.style.display = 'none';
        
        this.showToast(`${symbol} 차트가 로드되었습니다!`, 'success');
    }
    
    generateSampleData() {
        const data = [];
        const startPrice = 100 + Math.random() * 100;
        let currentPrice = startPrice;
        
        for (let i = 0; i < 60; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (60 - i));
            
            const change = (Math.random() - 0.5) * 5;
            currentPrice = Math.max(10, currentPrice + change);
            
            const high = currentPrice + Math.random() * 3;
            const low = currentPrice - Math.random() * 3;
            const open = currentPrice + (Math.random() - 0.5) * 2;
            const close = currentPrice;
            
            data.push({
                timestamp: date.getTime(),
                open: open,
                high: high,
                low: low,
                close: close,
                volume: Math.random() * 1000000
            });
        }
        
        return data;
    }
    
    updateStockInfo(symbol, data) {
        const lastCandle = data[data.length - 1];
        const prevCandle = data[data.length - 2];
        
        const currentPrice = lastCandle.close;
        const changeAmount = currentPrice - prevCandle.close;
        const changePercent = (changeAmount / prevCandle.close) * 100;
        
        const stockSymbol = this.container.querySelector('.stock-symbol');
        const stockPrice = this.container.querySelector('.stock-price');
        const priceChange = this.container.querySelector('.price-change');
        
        stockSymbol.textContent = symbol;
        stockPrice.textContent = `$${currentPrice.toFixed(2)}`;
        
        const isUp = changeAmount >= 0;
        const changeClass = isUp ? 'price-up' : 'price-down';
        const changeSymbol = isUp ? '▲' : '▼';
        
        stockPrice.className = `stock-price ${changeClass}`;
        priceChange.textContent = `${changeSymbol} ${Math.abs(changeAmount).toFixed(2)} (${changePercent.toFixed(2)}%)`;
        priceChange.className = `price-change ${changeClass}`;
    }
    
    showChart() {
        const chartHeader = this.container.querySelector('.chart-header');
        chartHeader.classList.remove('hidden');
    }
    
    handlePredictionTap(touch) {
        if (!this.chart) return;
        
        const canvas = this.container.querySelector('.chart-canvas');
        const rect = canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        // Convert to chart coordinates and create prediction
        const { date, price } = this.chart.screenToData(x, y);
        
        if (date && price) {
            this.chart.addPrediction(date, price);
            this.chart.draw();
            
            this.showToast(`예측 추가: $${price.toFixed(2)}`, 'success');
            this.updatePredictionsList();
            
            // Haptic feedback
            if (navigator.vibrate) {
                navigator.vibrate([10, 50, 10]);
            }
        }
    }
    
    updatePredictionsList() {
        if (!this.chart || this.chart.predictions.length === 0) {
            this.container.querySelector('.predictions-panel').classList.add('hidden');
            return;
        }
        
        this.container.querySelector('.predictions-panel').classList.remove('hidden');
        
        const predictionsList = this.container.querySelector('.predictions-list');
        const html = this.chart.predictions.map(pred => `
            <div class="prediction-item">
                <div>
                    <div class="prediction-date">${new Date(pred.date).toLocaleDateString('ko-KR')}</div>
                    <div class="prediction-price">$${pred.price.toFixed(2)}</div>
                    <div class="prediction-change price-up">📈 +2.5%</div>
                </div>
                <button class="remove-btn" onclick="this.removePrediction(${pred.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
        
        predictionsList.innerHTML = html;
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        const container = this.container.querySelector('.toast-container');
        container.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Hide and remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Export
window.MobileChartInterface = MobileChartInterface;