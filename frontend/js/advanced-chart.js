/**
 * Advanced Trading Chart for Korean Stock Platform
 * Version: 2025.10.08
 */

let currentWidget = null;
let currentPeriod = new Date();
let selectedPoints = [];

// Initialize Advanced TradingView Chart
function initializeAdvancedChart(symbol = 'AAPL', interval = 'D') {
    if (currentWidget) {
        currentWidget.remove();
    }
    
    currentWidget = new TradingView.widget({
        "width": "100%",
        "height": 600,
        "symbol": symbol,
        "interval": interval,
        "timezone": "Asia/Seoul",
        "theme": "dark",
        "style": "1",
        "locale": "ko",
        "toolbar_bg": "#1a1a1a",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "hide_legend": false,
        "save_image": false,
        "container_id": "advanced_tradingview_chart",
        "studies": [
            "MASimple@tv-basicstudies",
            "RSI@tv-basicstudies",
            "Volume@tv-basicstudies"
        ],
        "overrides": {
            "paneProperties.background": "#1a1a1a",
            "paneProperties.vertGridProperties.color": "#2a2a2a",
            "paneProperties.horzGridProperties.color": "#2a2a2a",
            "symbolWatermarkProperties.transparency": 90,
            "scalesProperties.textColor": "#888888",
            "scalesProperties.lineColor": "#2a2a2a",
            "mainSeriesProperties.candleStyle.upColor": "#00FFA3",
            "mainSeriesProperties.candleStyle.downColor": "#FF4747",
            "mainSeriesProperties.candleStyle.borderUpColor": "#00FFA3",
            "mainSeriesProperties.candleStyle.borderDownColor": "#FF4747",
            "mainSeriesProperties.candleStyle.wickUpColor": "#00FFA3",
            "mainSeriesProperties.candleStyle.wickDownColor": "#FF4747",
            "paneProperties.vertGridProperties.style": 1,
            "paneProperties.horzGridProperties.style": 1
        },
        "disabled_features": [],
        "enabled_features": ["study_templates"]
    });
}

// Chart Search Functionality
function setupChartSearch() {
    const searchInput = document.getElementById('chartSearchInput');
    const symbolName = document.getElementById('chartSymbolName');
    
    if (searchInput && symbolName) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const symbol = this.value.toUpperCase().trim();
                if (symbol) {
                    symbolName.textContent = symbol;
                    const activeInterval = document.querySelector('.timeframe-control-btn.active')?.dataset.period || 'D';
                    initializeAdvancedChart(symbol, convertPeriodToInterval(activeInterval));
                    updatePriceInfo(symbol);
                }
            }
        });
    }
}

// Convert period format to TradingView interval
function convertPeriodToInterval(period) {
    const mapping = {
        '5M': '5',
        '1H': '60',
        '1D': 'D',
        '1W': 'W',
        '1M': 'M',
        '1Y': '12M'
    };
    return mapping[period] || 'D';
}

// Time Navigation Functions
function setupTimeNavigation() {
    const prevYear = document.getElementById('prevYear');
    const prevMonth = document.getElementById('prevMonth');
    const nextMonth = document.getElementById('nextMonth');
    const nextYear = document.getElementById('nextYear');
    const currentPeriodSpan = document.getElementById('currentPeriod');
    const timeSlider = document.getElementById('timeSlider');
    
    function updatePeriodDisplay() {
        if (currentPeriodSpan) {
            const year = currentPeriod.getFullYear();
            const month = currentPeriod.getMonth() + 1;
            currentPeriodSpan.textContent = `${year}년 ${month}월`;
        }
    }
    
    if (prevYear) {
        prevYear.addEventListener('click', () => {
            currentPeriod.setFullYear(currentPeriod.getFullYear() - 1);
            updatePeriodDisplay();
            updateChartPeriod();
        });
    }
    
    if (prevMonth) {
        prevMonth.addEventListener('click', () => {
            currentPeriod.setMonth(currentPeriod.getMonth() - 1);
            updatePeriodDisplay();
            updateChartPeriod();
        });
    }
    
    if (nextMonth) {
        nextMonth.addEventListener('click', () => {
            currentPeriod.setMonth(currentPeriod.getMonth() + 1);
            updatePeriodDisplay();
            updateChartPeriod();
        });
    }
    
    if (nextYear) {
        nextYear.addEventListener('click', () => {
            currentPeriod.setFullYear(currentPeriod.getFullYear() + 1);
            updatePeriodDisplay();
            updateChartPeriod();
        });
    }
    
    // Time slider for past/present/future navigation
    if (timeSlider) {
        timeSlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            const today = new Date();
            const daysDiff = value - 280; // 280 represents current day
            
            const newDate = new Date(today);
            newDate.setDate(today.getDate() + daysDiff);
            
            currentPeriod = newDate;
            updatePeriodDisplay();
            updateChartPeriod();
        });
    }
    
    updatePeriodDisplay();
}

function updateChartPeriod() {
    const symbolName = document.getElementById('chartSymbolName');
    const symbol = symbolName ? symbolName.textContent : 'AAPL';
    const activeInterval = document.querySelector('.timeframe-control-btn.active')?.dataset.period || 'D';
    initializeAdvancedChart(symbol, convertPeriodToInterval(activeInterval));
}

// Chart Drawing Tools
function setupDrawingTools() {
    const addPointBtn = document.getElementById('addPoint');
    const drawLineBtn = document.getElementById('drawLine');
    const addNoteBtn = document.getElementById('addNote');
    const clearAllBtn = document.getElementById('clearAll');
    
    let isAddingPoint = false;
    
    if (addPointBtn) {
        addPointBtn.addEventListener('click', function() {
            isAddingPoint = !isAddingPoint;
            this.classList.toggle('active');
            
            if (isAddingPoint) {
                document.body.style.cursor = 'crosshair';
            } else {
                document.body.style.cursor = 'default';
            }
        });
    }
    
    // Add click listener to chart for point placement
    document.addEventListener('click', function(e) {
        if (isAddingPoint && e.target.closest('#advanced_tradingview_chart')) {
            addChartPoint(e.clientX, e.clientY);
        }
    });
    
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            selectedPoints.forEach(point => point.remove());
            selectedPoints = [];
        });
    }
}

function addChartPoint(x, y) {
    const chartContainer = document.getElementById('advanced_tradingview_chart');
    if (!chartContainer) return;
    
    const rect = chartContainer.getBoundingClientRect();
    
    const point = document.createElement('div');
    point.className = 'chart-point';
    point.style.left = (x - rect.left - 4) + 'px';
    point.style.top = (y - rect.top - 4) + 'px';
    
    // Create delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'point-delete-btn';
    deleteBtn.innerHTML = '×';
    deleteBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        point.remove();
        selectedPoints = selectedPoints.filter(p => p !== point);
    });
    
    point.appendChild(deleteBtn);
    chartContainer.appendChild(point);
    selectedPoints.push(point);
}

// Update price information
function updatePriceInfo(symbol) {
    // Simulate price data - in real implementation, fetch from API
    const prices = {
        'AAPL': { price: 189.45, change: 2.34, percent: 1.25 },
        'TSLA': { price: 242.67, change: -3.21, percent: -1.31 },
        'BTC': { price: 28450.00, change: 1250.00, percent: 4.59 },
        'MSFT': { price: 338.11, change: 5.67, percent: 1.71 }
    };
    
    const data = prices[symbol] || prices['AAPL'];
    const priceElement = document.getElementById('currentChartPrice');
    const changeElement = document.getElementById('priceChangeDisplay');
    
    if (priceElement) {
        priceElement.textContent = `$${data.price.toLocaleString()}`;
    }
    
    if (changeElement) {
        changeElement.textContent = `${data.change >= 0 ? '+' : ''}${data.change} (${data.change >= 0 ? '+' : ''}${data.percent}%)`;
        changeElement.className = `price-change ${data.change >= 0 ? 'positive' : 'negative'}`;
    }
}

// Volume bars animation
function animateVolumeBars() {
    const volumeBars = document.querySelectorAll('.volume-bar');
    if (volumeBars.length > 0) {
        setInterval(() => {
            volumeBars.forEach(bar => {
                const randomHeight = Math.random() * 80 + 20;
                bar.style.height = randomHeight + '%';
            });
        }, 5000);
    }
}

// Initialize everything when page loads
function initializeAdvancedChartSystem() {
    initializeAdvancedChart();
    setupChartSearch();
    setupTimeNavigation();
    setupDrawingTools();
    animateVolumeBars();
    
    // Form tabs functionality
    document.querySelectorAll('.form-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.form-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Timeframe control buttons
    document.querySelectorAll('.timeframe-control-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.timeframe-control-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const period = this.dataset.period;
            const symbolName = document.getElementById('chartSymbolName');
            const symbol = symbolName ? symbolName.textContent : 'AAPL';
            initializeAdvancedChart(symbol, convertPeriodToInterval(period));
        });
    });
    
    // Update chart when symbol changes in prediction form
    const symbolSelect = document.getElementById('symbolSelect');
    if (symbolSelect) {
        symbolSelect.addEventListener('change', function() {
            const symbol = this.value;
            if (symbol) {
                const symbolName = document.getElementById('chartSymbolName');
                if (symbolName) {
                    symbolName.textContent = symbol;
                }
                const activeInterval = document.querySelector('.timeframe-control-btn.active')?.dataset.period || 'D';
                initializeAdvancedChart(symbol, convertPeriodToInterval(activeInterval));
                updatePriceInfo(symbol);
            }
        });
    }
}

// Auto-initialize when TradingView is loaded
function waitForTradingView() {
    if (typeof TradingView !== 'undefined') {
        initializeAdvancedChartSystem();
    } else {
        // Wait for TradingView to load
        setTimeout(waitForTradingView, 100);
    }
}

// Start checking for TradingView availability
document.addEventListener('DOMContentLoaded', waitForTradingView);

// Also try after window load as fallback
window.addEventListener('load', () => {
    if (typeof TradingView !== 'undefined') {
        initializeAdvancedChartSystem();
    }
});