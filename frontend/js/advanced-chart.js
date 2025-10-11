/**
 * Advanced Trading Chart for Korean Stock Platform
 * Version: 2025.10.08
 */

let currentWidget = null;
let currentPeriod = new Date();
let selectedPoints = [];
let mobilePredictionChart = null;
let mobilePredictionSeries = null;
let activeMobileSymbol = 'BTC/USD';

const mobilePredictionData = {
    'BTC/USD': [
        { time: '2025-10-01', value: 42000 },
        { time: '2025-10-02', value: 43050 },
        { time: '2025-10-03', value: 43780 },
        { time: '2025-10-04', value: 43210 },
        { time: '2025-10-05', value: 43990 }
    ],
    'ETH/USD': [
        { time: '2025-10-01', value: 2780 },
        { time: '2025-10-02', value: 2825 },
        { time: '2025-10-03', value: 2880 },
        { time: '2025-10-04', value: 2840 },
        { time: '2025-10-05', value: 2905 }
    ],
    'AAPL': [
        { time: '2025-10-01', value: 184 },
        { time: '2025-10-02', value: 186 },
        { time: '2025-10-03', value: 188 },
        { time: '2025-10-04', value: 187 },
        { time: '2025-10-05', value: 189 }
    ],
    'TSLA': [
        { time: '2025-10-01', value: 242 },
        { time: '2025-10-02', value: 248 },
        { time: '2025-10-03', value: 252 },
        { time: '2025-10-04', value: 247 },
        { time: '2025-10-05', value: 255 }
    ],
    'MSFT': [
        { time: '2025-10-01', value: 336 },
        { time: '2025-10-02', value: 338 },
        { time: '2025-10-03', value: 340 },
        { time: '2025-10-04', value: 339 },
        { time: '2025-10-05', value: 342 }
    ],
    'GOOGL': [
        { time: '2025-10-01', value: 132 },
        { time: '2025-10-02', value: 134 },
        { time: '2025-10-03', value: 133 },
        { time: '2025-10-04', value: 135 },
        { time: '2025-10-05', value: 136 }
    ]
};

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

function initializeMobilePredictionChart(symbol = 'BTC/USD') {
    if (mobilePredictionChart || typeof LightweightCharts === 'undefined') {
        return;
    }

    const container = document.getElementById('mobilePredictionChart');
    if (!container) {
        return;
    }

    const rect = container.getBoundingClientRect();
    const width = Math.max(240, Math.floor(rect.width || container.offsetWidth || window.innerWidth - 32));

    mobilePredictionChart = LightweightCharts.createChart(container, {
        width,
        height: 190,
        layout: {
            background: { type: 'solid', color: '#0a1024' },
            textColor: '#f6f8ff'
        },
        grid: {
            vertLines: { color: 'rgba(255,255,255,0.05)' },
            horzLines: { color: 'rgba(255,255,255,0.05)' }
        },
        rightPriceScale: {
            borderColor: 'rgba(255,255,255,0.08)'
        },
        timeScale: {
            borderColor: 'rgba(255,255,255,0.08)',
            timeVisible: true,
            secondsVisible: false
        }
    });

    mobilePredictionSeries = mobilePredictionChart.addAreaSeries({
        lineColor: '#0A84FF',
        topColor: 'rgba(10, 132, 255, 0.45)',
        bottomColor: 'rgba(10, 132, 255, 0.08)',
        lineWidth: 3
    });

    updateMobilePredictionChart(symbol);

    window.addEventListener('resize', () => {
        if (!mobilePredictionChart) return;
        const bounds = container.getBoundingClientRect();
        const newWidth = Math.max(240, Math.floor(bounds.width || container.offsetWidth || window.innerWidth - 32));
        mobilePredictionChart.applyOptions({ width: newWidth });
    });
}

function updateMobilePredictionChart(symbol) {
    const container = document.getElementById('mobilePredictionChart');
    if (!container || !mobilePredictionSeries) {
        return;
    }

    const normalized = symbol.replace(/\s+/g, '').toUpperCase();
    let datasetKey = Object.keys(mobilePredictionData).find(key => key.replace(/\s+/g, '').toUpperCase() === normalized);

    if (!datasetKey) {
        datasetKey = Object.keys(mobilePredictionData).find(key => key.replace(/\s+|\/USD/gi, '').toUpperCase() === normalized);
    }

    if (!datasetKey && normalized && !normalized.includes('/')) {
        datasetKey = Object.keys(mobilePredictionData).find(key => key.replace(/\s+/g, '').toUpperCase() === `${normalized}/USD`);
    }

    const data = mobilePredictionData[datasetKey || 'BTC/USD'];
    mobilePredictionSeries.setData(data);
    mobilePredictionChart.timeScale().fitContent();
    activeMobileSymbol = datasetKey || 'BTC/USD';
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
                    updateMobilePredictionChart(symbol);
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
    initializeMobilePredictionChart(activeMobileSymbol);
    updateMobilePredictionChart(activeMobileSymbol);
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
                updateMobilePredictionChart(symbol);
            }
        });
    }

    document.querySelectorAll('.mobile-timeframe-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mobile-timeframe-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateMobilePredictionChart(activeMobileSymbol);
        });
    });

    const mobileMediaQuery = window.matchMedia('(max-width: 768px)');
    const ensureMobileChart = () => {
        if (mobileMediaQuery.matches) {
            initializeMobilePredictionChart(activeMobileSymbol);
            updateMobilePredictionChart(activeMobileSymbol);
        }
    };

    ensureMobileChart();
    mobileMediaQuery.addEventListener('change', ensureMobileChart);
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