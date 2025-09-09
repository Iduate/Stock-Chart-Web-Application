// TradingView Professional Chart Enhancements
// This script makes charts look and feel like professional TradingView charts

document.addEventListener('DOMContentLoaded', function() {
    console.log('TradingView Pro Theme loaded');
    
    // Initialize enhanced theme
    initTradingViewProTheme();
    
    // Setup professional chart appearance
    setupProCharts();
    
    // Add trust indicators
    addTrustIndicators();
    
    // Apply professional animations
    applyProfessionalAnimations();
});

/**
 * Initialize the professional TradingView-inspired theme
 */
function initTradingViewProTheme() {
    // Add custom theme class to body
    document.body.classList.add('tv-pro-theme');
    
    // Create theme toggle
    const themeToggleContainer = document.createElement('div');
    themeToggleContainer.className = 'theme-toggle-container';
    
    const themeToggleBtn = document.createElement('button');
    themeToggleBtn.className = 'theme-toggle';
    themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggleBtn.title = 'Toggle dark/light theme';
    
    themeToggleContainer.appendChild(themeToggleBtn);
    document.body.appendChild(themeToggleContainer);
    
    // Check saved preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Add event listener
    themeToggleBtn.addEventListener('click', function() {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
        themeToggleBtn.innerHTML = isLight ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        
        // Refresh any charts to apply theme
        if (window.refreshCharts && typeof window.refreshCharts === 'function') {
            window.refreshCharts();
        }
    });
}

/**
 * Setup professional chart appearance
 */
function setupProCharts() {
    // Options for TradingView-style charts
    window.tvProChartOptions = {
        layout: {
            background: { color: 'var(--tv-pro-chart-bg)' },
            textColor: 'var(--tv-pro-ui-text)',
            fontSize: 12,
            fontFamily: 'Inter, sans-serif',
        },
        grid: {
            vertLines: { color: 'var(--tv-pro-chart-grid)' },
            horzLines: { color: 'var(--tv-pro-chart-grid)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                width: 1,
                color: '#758696',
                style: LightweightCharts.LineStyle.Dashed,
            },
            horzLine: {
                width: 1,
                color: '#758696',
                style: LightweightCharts.LineStyle.Dashed,
            }
        },
        timeScale: {
            borderColor: 'var(--tv-pro-ui-border)',
            timeVisible: true,
            secondsVisible: false,
            tickMarkFormatter: (time) => {
                const date = new Date(time * 1000);
                return date.getDate() + '/' + (date.getMonth() + 1);
            }
        },
        rightPriceScale: {
            borderColor: 'var(--tv-pro-ui-border)',
            scaleMargins: {
                top: 0.1,
                bottom: 0.1,
            },
        },
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: true,
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
        }
    };
    
    // Line series style
    window.tvProLineSeriesOptions = {
        color: 'var(--tv-pro-bright-blue)',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        lastValueVisible: true,
        priceLineVisible: true,
        priceLineWidth: 1,
        priceLineColor: 'var(--tv-pro-bright-blue)',
        priceLineStyle: LightweightCharts.LineStyle.Dashed,
    };
    
    // Area series style
    window.tvProAreaSeriesOptions = {
        topColor: 'rgba(41, 98, 255, 0.28)',
        bottomColor: 'rgba(41, 98, 255, 0.05)',
        lineColor: 'var(--tv-pro-bright-blue)',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        lastValueVisible: true,
        priceLineVisible: true,
        priceLineWidth: 1,
        priceLineColor: 'var(--tv-pro-bright-blue)',
        priceLineStyle: LightweightCharts.LineStyle.Dashed,
    };
    
    // Candle series style
    window.tvProCandleSeriesOptions = {
        upColor: 'var(--tv-pro-green)',
        downColor: 'var(--tv-pro-red)',
        borderUpColor: 'var(--tv-pro-green)',
        borderDownColor: 'var(--tv-pro-red)',
        wickUpColor: 'var(--tv-pro-green)',
        wickDownColor: 'var(--tv-pro-red)',
        priceLineVisible: true,
        priceLineWidth: 1,
        priceLineColor: '#787B86',
        priceLineStyle: LightweightCharts.LineStyle.Dashed,
    };
    
    // Bar series style
    window.tvProBarSeriesOptions = {
        upColor: 'var(--tv-pro-green)',
        downColor: 'var(--tv-pro-red)',
        priceLineVisible: true,
        priceLineWidth: 1,
        priceLineColor: '#787B86',
        priceLineStyle: LightweightCharts.LineStyle.Dashed,
    };
    
    // Initialize any existing charts with these options
    if (window.initializeCharts && typeof window.initializeCharts === 'function') {
        window.initializeCharts();
    }
}

/**
 * Add trust indicators to the UI
 */
function addTrustIndicators() {
    // Add data source indicators
    const trustElements = document.querySelectorAll('.chart-container');
    
    trustElements.forEach(container => {
        // Create data source indicator
        const dataSourceIndicator = document.createElement('div');
        dataSourceIndicator.className = 'data-source-indicator';
        dataSourceIndicator.innerHTML = '<i class="fas fa-shield-check"></i> Data by Yahoo Finance';
        container.appendChild(dataSourceIndicator);
        
        // Add security badge
        const securityBadge = document.createElement('div');
        securityBadge.className = 'security-badge';
        securityBadge.innerHTML = '<i class="fas fa-lock"></i>';
        securityBadge.title = 'Data protected with enterprise-grade encryption';
        container.appendChild(securityBadge);
    });
    
    // Add main trust bar if homepage is detected
    if (window.location.pathname.includes('home.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/')) {
        const mainContent = document.querySelector('main') || document.querySelector('.content') || document.body;
        
        // Create trust bar
        const trustBar = document.createElement('div');
        trustBar.className = 'trust-bar-container';
        trustBar.innerHTML = `
            <div class="trust-bar-icon">
                <i class="fas fa-shield-check"></i>
            </div>
            <div class="trust-bar-text">
                <div class="trust-bar-title">신뢰할 수 있는 데이터 소스</div>
                <div class="trust-bar-message">전세계 수백만 트레이더들이 신뢰하는 데이터를 사용합니다. 24시간 실시간 업데이트.</div>
            </div>
        `;
        
        // Insert after first chart container or at beginning of main content
        const firstChartContainer = mainContent.querySelector('.chart-container');
        if (firstChartContainer) {
            firstChartContainer.parentNode.insertBefore(trustBar, firstChartContainer.nextSibling);
        } else {
            mainContent.insertBefore(trustBar, mainContent.firstChild);
        }
    }
}

/**
 * Apply professional animations for a premium feel
 */
function applyProfessionalAnimations() {
    // Add animation class to body
    document.body.classList.add('tv-pro-animations');
    
    // Add scroll reveal animations to elements
    const elementsToAnimate = [
        '.card',
        '.chart-container',
        '.data-table',
        '.trust-bar-container',
        '.feature-section',
        '.ranking-item'
    ];
    
    // Simple reveal animation
    elementsToAnimate.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 100 + (index * 50));
        });
    });
    
    // Add chart load animations
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        // Add loading indicator that fades out
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'chart-loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="chart-loading-spinner"></div>
            <div class="chart-loading-text">Loading professional chart...</div>
        `;
        container.appendChild(loadingOverlay);
        
        // Fade out after a short delay
        setTimeout(() => {
            loadingOverlay.style.opacity = '0';
            setTimeout(() => {
                loadingOverlay.remove();
            }, 500);
        }, 800);
    });
}

// Export functions for use in main app
window.tvPro = {
    refreshCharts: function() {
        setupProCharts();
    },
    getChartOptions: function() {
        return window.tvProChartOptions;
    },
    getLineSeriesOptions: function() {
        return window.tvProLineSeriesOptions;
    },
    getAreaSeriesOptions: function() {
        return window.tvProAreaSeriesOptions;
    },
    getCandleSeriesOptions: function() {
        return window.tvProCandleSeriesOptions;
    },
    getBarSeriesOptions: function() {
        return window.tvProBarSeriesOptions;
    }
};
