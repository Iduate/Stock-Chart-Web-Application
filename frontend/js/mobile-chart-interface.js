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
                        <i class="fas fa-chart-line"></i>
                        <span>StockChart</span>
                    </div>
                    <div class="search-container">
                        <i class="fas fa-search search-icon"></i>
                        <input type="text" class="search-input" placeholder="주식 검색..." autocomplete="off">
                        <div class="search-suggestions"></div>
                    </div>
                </div>
                
                <!-- Chart Container -->
                <div class="chart-container">
                    <div class="chart-header hidden">
                        <div class="stock-info">
                            <div class="stock-symbol"></div>
                            <div class="stock-price"></div>
                            <div class="price-change"></div>
                        </div>
                    </div>
                    
                    <div class="chart-wrapper">
                        <canvas class="chart-canvas"></canvas>
                        
                        <!-- Touch Instructions -->
                        <div class="touch-instructions">
                            <div class="instruction-card">
                                <i class="fas fa-hand-pointer"></i>
                                <h3>터치하여 예측하세요</h3>
                                <p>차트를 터치하여 가격 예측을 추가하세요</p>
                            </div>
                        </div>
                        
                        <!-- Chart Controls -->
                        <div class="chart-controls">
                            <button class="control-btn zoom-out">
                                <i class="fas fa-search-minus"></i>
                            </button>
                            <button class="control-btn zoom-in">
                                <i class="fas fa-search-plus"></i>
                            </button>
                            <button class="control-btn reset">
                                <i class="fas fa-expand"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Predictions Panel -->
                <div class="predictions-panel hidden">
                    <div class="panel-header">
                        <h3>내 예측</h3>
                        <button class="clear-btn">모두 삭제</button>
                    </div>
                    <div class="predictions-list"></div>
                    <button class="share-btn">
                        <i class="fas fa-share-alt"></i>
                        예측 공유하기
                    </button>
                </div>
                
                <!-- Bottom Navigation -->
                <div class="bottom-nav">
                    <button class="nav-btn active" data-tab="chart">
                        <i class="fas fa-chart-line"></i>
                        <span>차트</span>
                    </button>
                    <button class="nav-btn" data-tab="predictions">
                        <i class="fas fa-lightbulb"></i>
                        <span>예측</span>
                    </button>
                    <button class="nav-btn" data-tab="share">
                        <i class="fas fa-share-alt"></i>
                        <span>공유</span>
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
        // Implement enhanced touch gestures
        const canvas = this.container.querySelector('.chart-canvas');
        let isDrawing = false;
        let lastTouch = null;
        
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            isDrawing = true;
            lastTouch = e.touches[0];
            
            // Add haptic feedback if available
            if (navigator.vibrate) {
                navigator.vibrate(10);
            }
        });
        
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!isDrawing || !lastTouch) return;
            
            const touch = e.touches[0];
            // Handle pan/zoom gestures
        });
        
        canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (!isDrawing) return;
            
            isDrawing = false;
            
            // Handle prediction creation
            if (lastTouch) {
                this.handlePredictionTap(lastTouch);
            }
            
            lastTouch = null;
        });
    }
    
    setupSearchInterface() {
        const searchInput = this.container.querySelector('.search-input');
        const suggestions = this.container.querySelector('.search-suggestions');
        
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length >= 1) {
                this.showSearchSuggestions(query);
            } else {
                this.hideSearchSuggestions();
            }
        });
        
        searchInput.addEventListener('focus', () => {
            searchInput.parentElement.style.transform = 'scale(1.02)';
        });
        
        searchInput.addEventListener('blur', () => {
            searchInput.parentElement.style.transform = 'scale(1)';
            setTimeout(() => this.hideSearchSuggestions(), 200);
        });
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