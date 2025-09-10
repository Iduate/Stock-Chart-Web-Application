// Stock Chart Web Application - Main JavaScript File
// API Base URL Configuration - Auto-detect environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000/api'
    : '/api';  // Use relative path for production
console.log('App.js loaded - Production API fix version 1.4 - ' + new Date().getTime());
console.log('API Base URL:', API_BASE_URL);

// Test function to manually call crypto
window.testCrypto = function () {
    console.log('Manual crypto test called');
    loadCryptoData();
};

// Global variables for chart instances
let heroChart = null;
let predictionChart = null;
let currentSeries = null;

// Authentication state
let authState = {
    isAuthenticated: false,
    user: null,
    token: null
};

// Initialize authentication state
function initializeAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (token && user.id) {
        authState.isAuthenticated = true;
        authState.user = user;
        authState.token = token;
    }

    updateAuthUI();
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded, checking LightweightCharts...');

    // Initialize authentication first
    initializeAuth();

    // Check if LightweightCharts is available
    if (typeof LightweightCharts === 'undefined') {
        console.error('LightweightCharts library not loaded! Please check if the script is included.');
        // Try to load it dynamically
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js';
        script.onload = function () {
            console.log('LightweightCharts loaded dynamically');
            initializeApp();
            initializeCharts();
            loadMarketData();
            startRealTimeUpdates();
        };
        document.head.appendChild(script);
        return;
    }

    // Check if TradingView Pro theme is available
    if (window.tvPro) {
        console.log('TradingView Pro theme detected and will be used');
    } else {
        console.log('TradingView Pro theme not detected, loading basic charts');
    }

    // Load chart controls if script exists
    if (!window.chartControlsLoaded) {
        try {
            const controlsScript = document.createElement('script');
            controlsScript.src = 'js/chart-controls.js';
            controlsScript.onload = function () {
                console.log('Chart controls loaded successfully');
                window.chartControlsLoaded = true;
            };
            document.head.appendChild(controlsScript);

            // Add chart controls CSS
            const controlsCSS = document.createElement('link');
            controlsCSS.rel = 'stylesheet';
            controlsCSS.href = 'css/chart-controls.css';
            document.head.appendChild(controlsCSS);
        } catch (e) {
            console.error('Error loading chart controls:', e);
        }
    }

    initializeApp();
    initializeCharts();
    loadMarketData();
    startRealTimeUpdates();

    // Add trust elements after charts are loaded
    setTimeout(addTrustElements, 500);

    // Enhance mini charts for my-predictions page
    setTimeout(enhanceMiniCharts, 1000);
});

// Initialize main application features
// Add trust elements to make the application appear more professional
function addTrustElements() {
    // Add trust indicators to chart containers
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        // Add data source badge
        const sourceBadge = document.createElement('div');
        sourceBadge.className = 'data-source-indicator';
        sourceBadge.innerHTML = '<i class="fas fa-shield-check"></i> Yahoo Finance 실시간 데이터';
        container.appendChild(sourceBadge);

        // Add security badge
        const securityBadge = document.createElement('div');
        securityBadge.className = 'security-badge';
        securityBadge.innerHTML = '<i class="fas fa-lock"></i>';
        securityBadge.title = '보안 연결 - 데이터는 암호화되어 있습니다';
        container.appendChild(securityBadge);
    });

    // Add trust bar to appropriate pages
    if (document.querySelector('.content-section') || document.querySelector('.main-content')) {
        const contentSection = document.querySelector('.content-section') || document.querySelector('.main-content');
        const trustBar = document.createElement('div');
        trustBar.className = 'trust-bar-container';
        trustBar.innerHTML = `
            <div class="trust-bar-icon">
                <i class="fas fa-shield-check"></i>
            </div>
            <div class="trust-bar-text">
                <div class="trust-bar-title">전문가급 차트 시스템</div>
                <div class="trust-bar-message">전세계 수백만 트레이더들이 신뢰하는 동일한 차트 기술을 사용합니다.</div>
            </div>
        `;

        if (contentSection.firstChild) {
            contentSection.insertBefore(trustBar, contentSection.firstChild.nextSibling);
        } else {
            contentSection.appendChild(trustBar);
        }
    }

    // Add verified badges to key metrics
    const metricValues = document.querySelectorAll('.metric-value');
    metricValues.forEach(metric => {
        const verifiedBadge = document.createElement('span');
        verifiedBadge.className = 'verified-badge';
        verifiedBadge.innerHTML = '<i class="fas fa-check"></i> 검증됨';
        metric.appendChild(verifiedBadge);
    });
}

function initializeApp() {
    // Check login status
    const token = localStorage.getItem('accessToken');
    if (token) {
        validateToken(token);
    }

    // Setup mobile navigation
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function () {
            navMenu.classList.toggle('active');
        });
    }

    // Setup navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function (e) {
            if (navMenu) navMenu.classList.remove('active');

            const href = this.getAttribute('href');
            if (href && href.startsWith('#') && href !== '#') {
                e.preventDefault();
                const sectionId = href.substring(1);
                scrollToSection(sectionId);
            }
        });
    });

    // Update active navigation
    updateActiveNavigation();
    window.addEventListener('scroll', debounce(updateActiveNavigation, 100));

    // Initialize stock selector
    initializeStockSelector();

    // Initialize predictions display
    initMyPredictions();

    // Load market data
    loadMarketData();

    // Load charts for chart board
    loadCharts();

    // Add API testing UI
    addAPITestingUI();
}

// Initialize charts with professional TradingView styling
function initializeCharts() {
    console.log('Initializing charts with professional styling...');

    // Register chart refresh function for theme toggling
    window.refreshCharts = function () {
        if (window.heroChart) {
            const options = getTradingViewProChartOptions();
            window.heroChart.applyOptions(options);
        }

        if (window.predictionChart) {
            const options = getTradingViewProChartOptions();
            window.predictionChart.applyOptions(options);
        }
    };

    // Initialize hero chart
    const heroChartElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
    console.log('Hero chart element:', heroChartElement);

    if (heroChartElement && typeof LightweightCharts !== 'undefined') {
        console.log('Creating professional TradingView-style hero chart...');

        try {
            // Mobile-specific initialization fixes
            const isMobile = window.innerWidth <= 768;
            const isSmallMobile = window.innerWidth <= 480;

            // Ensure the element has proper dimensions with mobile-specific handling
            if (heroChartElement.clientWidth === 0 || isMobile) {
                heroChartElement.style.position = 'relative';
                heroChartElement.style.width = '100%';
                heroChartElement.style.height = isSmallMobile ? '280px' : (isMobile ? '300px' : '400px');
                heroChartElement.style.display = 'block';
                heroChartElement.style.visibility = 'visible';
                heroChartElement.style.opacity = '1';

                // Force a reflow to calculate width
                heroChartElement.offsetHeight;

                // Wait for DOM to settle on mobile
                if (isMobile) {
                    setTimeout(() => {
                        console.log('Mobile DOM settled, continuing chart initialization...');
                    }, 100);
                }
            }

            // Calculate responsive dimensions with mobile fallbacks
            let containerWidth = heroChartElement.clientWidth || heroChartElement.offsetWidth;
            const viewportWidth = window.innerWidth;

            // Mobile fallback if width calculation fails
            if (!containerWidth || containerWidth === 0) {
                if (isSmallMobile) {
                    containerWidth = Math.min(viewportWidth - 32, 350);
                } else if (isMobile) {
                    containerWidth = Math.min(viewportWidth - 40, 500);
                } else {
                    containerWidth = 800;
                }
                console.log(`Using fallback width: ${containerWidth}px for mobile: ${isMobile}`);
            }

            let chartWidth = containerWidth;
            let chartHeight = 400;

            // Responsive sizing with mobile optimizations
            if (isSmallMobile) {
                chartWidth = Math.min(containerWidth, viewportWidth - 20);
                chartHeight = 280;
            } else if (isMobile) {
                chartWidth = Math.min(containerWidth, viewportWidth - 30);
                chartHeight = 300;
            } else {
                chartWidth = containerWidth;
                chartHeight = 400;
            }

            // Ensure minimum sizes but respect mobile constraints
            chartWidth = Math.max(chartWidth, isMobile ? 280 : 300);
            chartHeight = Math.max(chartHeight, isMobile ? 250 : 300);

            console.log(`Mobile-optimized chart dimensions: ${chartWidth}x${chartHeight} (viewport: ${viewportWidth}, mobile: ${isMobile})`);

            // Use TradingView Pro options with mobile optimizations
            const chartOptions = getTradingViewProChartOptions(chartWidth, chartHeight);

            // Mobile-specific chart options
            if (isMobile) {
                chartOptions.handleScroll = {
                    mouseWheel: true,
                    pressedMouseMove: true,
                    horzTouchDrag: true,
                    vertTouchDrag: true,
                };
                chartOptions.handleScale = {
                    axisPressedMouseMove: {
                        time: true,
                        price: true,
                    },
                    mouseWheel: true,
                    pinch: true,
                };
                // Ensure chart fits mobile viewport
                chartOptions.width = chartWidth;
                chartOptions.height = chartHeight;
            }

            window.heroChart = LightweightCharts.createChart(heroChartElement, chartOptions);

            console.log('Mobile-optimized professional hero chart created');

            // Add professional loading animation
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'chart-loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="chart-loading-spinner"></div>
                <div class="chart-loading-text">Loading professional chart data...</div>
            `;
            heroChartElement.appendChild(loadingOverlay);

            // Load chart data with enhanced styling - delay slightly on mobile for better rendering
            const loadDelay = isMobile ? 300 : 0;
            setTimeout(() => {
                if (typeof window.heroChart.addLineSeries === 'function') {
                    loadStockChart('BTC', true, true); // Use BTC instead of bitcoin for better API compatibility

                    // Remove loading overlay after data is loaded
                    setTimeout(() => {
                        if (loadingOverlay && loadingOverlay.parentNode) {
                            loadingOverlay.style.opacity = '0';
                            setTimeout(() => {
                                if (loadingOverlay.parentNode) {
                                    loadingOverlay.remove();
                                }
                            }, 500);
                        }
                    }, 1500);
                } else {
                    console.error('Chart created but addLineSeries method is missing');
                    setTimeout(() => {
                        loadStockChart('BTC', true, true);
                        if (loadingOverlay.parentNode) {
                            loadingOverlay.remove();
                        }
                    }, 100);
                }
            }, loadDelay);
        } catch (error) {
            console.error('Failed to create professional hero chart:', error);
        }
    } else {
        console.error('Hero chart element not found or LightweightCharts not available');
    }

    // Initialize prediction chart
    const predictionChartElement = document.getElementById('predictionChart');
    if (predictionChartElement && typeof LightweightCharts !== 'undefined') {
        console.log('Creating prediction chart...');

        try {
            // Ensure the element has proper dimensions
            if (predictionChartElement.clientWidth === 0) {
                predictionChartElement.style.width = '100%';
                predictionChartElement.style.height = window.innerWidth <= 480 ? '200px' : (window.innerWidth <= 768 ? '250px' : '300px');
            }

            const chartWidth = predictionChartElement.clientWidth || (window.innerWidth <= 768 ? window.innerWidth - 40 : 600);
            const chartHeight = window.innerWidth <= 480 ? 200 : (window.innerWidth <= 768 ? 250 : 300);

            window.predictionChart = LightweightCharts.createChart(predictionChartElement, getMobileChartConfig(chartWidth, chartHeight));

            console.log('Prediction chart created:', window.predictionChart);
        } catch (error) {
            console.error('Failed to create prediction chart:', error);
        }
    }

    // Add responsive chart resize handling
    addChartResizeHandler();
}

// Enhanced chart resize handler to prevent cut-off issues
function addChartResizeHandler() {
    let resizeTimeout;

    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            console.log('Window resized, updating charts...');

            const isMobile = window.innerWidth <= 768;
            const isSmallMobile = window.innerWidth <= 480;

            // Update hero chart with mobile optimizations
            if (window.heroChart) {
                const heroElement = document.getElementById('featuredChart') || document.getElementById('heroChart');
                if (heroElement) {
                    // Ensure container has proper styling for mobile
                    if (isMobile) {
                        heroElement.style.position = 'relative';
                        heroElement.style.width = '100%';
                        heroElement.style.height = isSmallMobile ? '280px' : '300px';
                        heroElement.style.display = 'block';
                        heroElement.style.visibility = 'visible';
                        heroElement.style.overflow = 'hidden';
                    }

                    let containerWidth = heroElement.clientWidth || heroElement.offsetWidth;
                    const viewportWidth = window.innerWidth;

                    // Mobile fallback for width calculation
                    if (!containerWidth || containerWidth === 0) {
                        if (isSmallMobile) {
                            containerWidth = Math.min(viewportWidth - 20, 350);
                        } else if (isMobile) {
                            containerWidth = Math.min(viewportWidth - 30, 500);
                        } else {
                            containerWidth = 800;
                        }
                    }

                    let chartWidth = containerWidth;
                    let chartHeight = 400;

                    if (isSmallMobile) {
                        chartWidth = Math.min(containerWidth, viewportWidth - 20);
                        chartHeight = 280;
                    } else if (isMobile) {
                        chartWidth = Math.min(containerWidth, viewportWidth - 30);
                        chartHeight = 300;
                    }

                    chartWidth = Math.max(chartWidth, isMobile ? 280 : 300);
                    chartHeight = Math.max(chartHeight, isMobile ? 250 : 300);

                    console.log(`Resizing hero chart to: ${chartWidth}x${chartHeight} (mobile: ${isMobile})`);

                    try {
                        window.heroChart.applyOptions({
                            width: chartWidth,
                            height: chartHeight
                        });

                        // Force chart to fit content on mobile after resize
                        if (isMobile) {
                            setTimeout(() => {
                                if (window.heroChart && window.heroChart.timeScale) {
                                    window.heroChart.timeScale().fitContent();
                                }
                            }, 100);
                        }
                    } catch (error) {
                        console.error('Error resizing hero chart:', error);
                    }
                }
            }

            // Update prediction chart
            if (window.predictionChart) {
                const predictionElement = document.getElementById('predictionChart');
                if (predictionElement) {
                    const containerWidth = predictionElement.clientWidth || predictionElement.offsetWidth;
                    const viewportWidth = window.innerWidth;

                    let chartWidth = containerWidth || (viewportWidth <= 768 ? viewportWidth - 40 : 600);
                    let chartHeight = viewportWidth <= 480 ? 200 : (viewportWidth <= 768 ? 250 : 300);

                    chartWidth = Math.max(chartWidth, 300);
                    chartHeight = Math.max(chartHeight, 200);

                    console.log(`Resizing prediction chart to: ${chartWidth}x${chartHeight}`);
                    window.predictionChart.applyOptions({
                        width: chartWidth,
                        height: chartHeight
                    });
                }
            }
        }, 150);
    });
}

// Mobile chart debugging function
function debugMobileChart() {
    const isMobile = window.innerWidth <= 768;
    const isSmallMobile = window.innerWidth <= 480;

    console.log('=== MOBILE CHART DEBUG ===');
    console.log(`Screen: ${window.innerWidth}x${window.innerHeight}`);
    console.log(`Mobile: ${isMobile}, Small Mobile: ${isSmallMobile}`);

    const heroElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
    if (heroElement) {
        const rect = heroElement.getBoundingClientRect();
        console.log('Hero element:', {
            width: heroElement.clientWidth,
            height: heroElement.clientHeight,
            offsetWidth: heroElement.offsetWidth,
            offsetHeight: heroElement.offsetHeight,
            rect: rect,
            display: getComputedStyle(heroElement).display,
            position: getComputedStyle(heroElement).position,
            visibility: getComputedStyle(heroElement).visibility
        });

        const canvases = heroElement.querySelectorAll('canvas');
        console.log(`Found ${canvases.length} canvas elements`);
        canvases.forEach((canvas, i) => {
            console.log(`Canvas ${i}:`, {
                width: canvas.width,
                height: canvas.height,
                clientWidth: canvas.clientWidth,
                clientHeight: canvas.clientHeight,
                display: getComputedStyle(canvas).display,
                visibility: getComputedStyle(canvas).visibility,
                opacity: getComputedStyle(canvas).opacity
            });
        });
    }

    if (window.heroChart) {
        console.log('Hero chart object exists:', typeof window.heroChart);
        console.log('Chart methods available:', Object.getOwnPropertyNames(window.heroChart));
    }

    console.log('=========================');
}

// Call debug function on mobile devices
if (window.innerWidth <= 768) {
    setTimeout(() => debugMobileChart(), 2000);
}

// Mobile-specific chart initialization
function initializeMobileCharts() {
    const isMobile = window.innerWidth <= 768;
    const isSmallMobile = window.innerWidth <= 480;

    if (!isMobile) return;

    console.log('Initializing mobile chart optimizations...');

    // Force proper viewport if not set
    let viewport = document.querySelector('meta[name="viewport"]');
    if (!viewport) {
        viewport = document.createElement('meta');
        viewport.name = 'viewport';
        document.head.appendChild(viewport);
    }
    viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';

    // Add mobile chart classes to body
    document.body.classList.add('mobile-charts');
    if (isSmallMobile) {
        document.body.classList.add('small-mobile');
    }

    // Ensure all chart containers have proper mobile styles
    const chartContainers = document.querySelectorAll('.featured-chart-container, .chart-container-hero, #heroChart, #featuredChart');
    chartContainers.forEach(container => {
        if (container) {
            container.style.position = 'relative';
            container.style.width = '100%';
            container.style.height = isSmallMobile ? '280px' : '300px';
            container.style.display = 'block';
            container.style.visibility = 'visible';
            container.style.opacity = '1';
            container.style.overflow = 'hidden';
            container.style.background = '#ffffff';
            container.style.border = '1px solid #e1e5e9';
            container.style.borderRadius = '8px';
            container.style.touchAction = 'pan-x pan-y';
        }
    });

    // Force redraw of charts after mobile initialization
    setTimeout(() => {
        if (window.heroChart && window.heroChart.timeScale) {
            try {
                window.heroChart.timeScale().fitContent();
            } catch (e) {
                console.log('Chart fitContent failed:', e);
            }
        }
    }, 500);
}

// Initialize mobile optimizations on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMobileCharts);
} else {
    initializeMobileCharts();
}

// Mobile-optimized chart configuration
function getMobileChartConfig(width, height) {
    const baseConfig = {
        width: width,
        height: height,
        layout: {
            backgroundColor: '#ffffff',
            textColor: '#333333',
        },
        grid: {
            vertLines: { color: '#f0f0f0' },
            horzLines: { color: '#f0f0f0' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#cccccc',
            autoScale: true,
        },
        timeScale: {
            borderColor: '#cccccc',
            timeVisible: true,
            secondsVisible: false,
        },
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
        },
    };

    // Mobile-specific adjustments
    if (width <= 480) {
        baseConfig.rightPriceScale.visible = false;
        baseConfig.timeScale.visible = false;
        baseConfig.crosshair.mode = LightweightCharts.CrosshairMode.Hidden;
    }

    return baseConfig;
}

// Enhanced chart resize handler to prevent cut-off issues
function addChartResizeHandler() {
    let resizeTimeout;

    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            console.log('Window resized, updating charts...');

            // Update hero chart
            if (window.heroChart) {
                const heroChartElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
                if (heroChartElement) {
                    const containerWidth = heroChartElement.clientWidth || heroChartElement.offsetWidth;
                    const viewportWidth = window.innerWidth;

                    let chartWidth = containerWidth;
                    let chartHeight = 400;

                    // Responsive sizing (same logic as initialization)
                    if (viewportWidth <= 480) {
                        chartWidth = Math.min(containerWidth, viewportWidth - 32);
                        chartHeight = 250;
                    } else if (viewportWidth <= 768) {
                        chartWidth = Math.min(containerWidth, viewportWidth - 40);
                        chartHeight = 300;
                    } else {
                        chartWidth = containerWidth || 800;
                        chartHeight = 400;
                    }

                    // Ensure minimum sizes
                    chartWidth = Math.max(chartWidth, 300);
                    chartHeight = Math.max(chartHeight, 200);

                    console.log(`Resizing hero chart to: ${chartWidth}x${chartHeight}`);

                    window.heroChart.applyOptions({
                        width: chartWidth,
                        height: chartHeight
                    });
                }
            }

            // Also resize prediction chart if it exists
            if (window.predictionChart) {
                const predictionChartElement = document.getElementById('predictionChart');
                if (predictionChartElement) {
                    const width = predictionChartElement.clientWidth || 300;
                    const height = window.innerWidth <= 480 ? 200 : (window.innerWidth <= 768 ? 250 : 300);

                    console.log(`Resizing prediction chart to: ${width}x${height}`);

                    window.predictionChart.applyOptions({
                        width: width,
                        height: height
                    });
                }
            }
        }, 250); // Debounce resize events
    });
}

// Chart validation and debug function
function validateChartDisplay() {
    console.log('=== Chart Display Validation ===');

    const heroChartElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
    if (heroChartElement) {
        console.log('Chart container found:', {
            id: heroChartElement.id,
            width: heroChartElement.clientWidth,
            height: heroChartElement.clientHeight,
            offsetWidth: heroChartElement.offsetWidth,
            offsetHeight: heroChartElement.offsetHeight,
            style: {
                width: heroChartElement.style.width,
                height: heroChartElement.style.height,
                overflow: heroChartElement.style.overflow
            }
        });

        if (window.heroChart) {
            console.log('Chart instance exists');
            console.log('Current series:', window.currentSeries ? 'Yes' : 'No');
            console.log('Prediction series:', window.predictionSeries ? 'Yes' : 'No');
        } else {
            console.warn('Chart instance not found');
        }
    } else {
        console.error('Chart container element not found');
    }

    console.log('Viewport width:', window.innerWidth);
    console.log('=== End Validation ===');
}

// Call validation after page load
setTimeout(validateChartDisplay, 2000);

// Load stock chart with multiple API fallback and dual-line support
async function loadStockChart(symbol, useProfessionalStyle = true, showPredictions = true) {
    console.log(`Loading professional stock chart for ${symbol}...`);

    // Verify chart object exists and has required methods
    if (!window.heroChart) {
        console.error('Hero chart not initialized');
        return;
    }

    // Clear any existing series
    if (window.currentSeries) {
        window.heroChart.removeSeries(window.currentSeries);
    }
    if (window.predictionSeries) {
        window.heroChart.removeSeries(window.predictionSeries);
    }

    const cryptoSymbols = ['BTC', 'ETH', 'ADA', 'BNB', 'DOT', 'MATIC', 'SOL', 'LTC', 'XRP', 'DOGE', 'AVAX', 'LINK', 'UNI', 'ATOM',
        'btc', 'eth', 'ada', 'bnb', 'dot', 'matic', 'sol', 'ltc', 'xrp', 'doge', 'avax', 'link', 'uni', 'atom'];

    const isCrypto = cryptoSymbols.includes(symbol);
    const marketParam = isCrypto ? '?market=crypto' : '';

    const apiSources = [
        { name: 'CoinGecko', endpoint: `coingecko/${symbol}/` },
        { name: 'Primary Historical', endpoint: `historical/${symbol}/${marketParam}` },
        { name: 'Crypto API', endpoint: `crypto/${symbol}/` },
        { name: 'Tiingo', endpoint: `tiingo/${symbol}/` },
        { name: 'Marketstack', endpoint: `marketstack/${symbol}/` },
        { name: 'Enhanced', endpoint: `enhanced/${symbol}/` }
    ]; let data = null;
    let usedSource = null;

    for (const source of apiSources) {
        try {
            console.log(`Trying ${source.name} API...`);
            const response = await fetch(`${API_BASE_URL}/market-data/${source.endpoint}`);
            if (response.ok) {
                const apiData = await response.json();
                if (apiData && (Array.isArray(apiData) || apiData.data)) {
                    data = Array.isArray(apiData) ? apiData : apiData.data;
                    usedSource = source.name;
                    console.log(`Successfully loaded data from ${source.name}:`, data);
                    break;
                }
            }
        } catch (error) {
            console.log(`${source.name} API failed:`, error.message);
        }
    }

    try {
        if (data && window.heroChart) {
            console.log('Adding line series to chart...');

            // Check if heroChart has the addLineSeries method
            if (typeof window.heroChart.addLineSeries !== 'function') {
                console.error('heroChart.addLineSeries is not a function. Chart object:', window.heroChart);
                console.error('Available methods:', Object.getOwnPropertyNames(window.heroChart));

                // Try to recreate the chart
                const heroChartElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
                if (heroChartElement) {
                    console.log('Attempting to recreate chart...');
                    window.heroChart = LightweightCharts.createChart(heroChartElement, {
                        width: heroChartElement.clientWidth || 800,
                        height: 400,
                        layout: {
                            backgroundColor: '#ffffff',
                            textColor: '#333',
                        },
                        grid: {
                            vertLines: { color: '#f0f0f0' },
                            horzLines: { color: '#f0f0f0' },
                        },
                        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
                        rightPriceScale: { borderColor: '#cccccc' },
                        timeScale: { borderColor: '#cccccc' },
                    });
                    console.log('Chart recreated:', window.heroChart);
                }

                if (typeof window.heroChart.addLineSeries !== 'function') {
                    throw new Error('Invalid chart object - addLineSeries method not available after recreation');
                }
            }

            // Remove existing series
            try {
                if (window.currentSeries) {
                    window.heroChart.removeSeries(window.currentSeries);
                }
            } catch (e) {
                console.log('No existing series to remove');
            }

            // Use professional styling options if available
            let seriesOptions;

            if (useProfessionalStyle && window.tvPro && window.tvPro.getAreaSeriesOptions) {
                seriesOptions = window.tvPro.getAreaSeriesOptions();
            } else {
                seriesOptions = {
                    topColor: 'rgba(41, 98, 255, 0.28)',
                    bottomColor: 'rgba(41, 98, 255, 0.05)',
                    lineColor: '#2962FF',
                    lineWidth: 2,
                    priceFormat: {
                        type: 'price',
                        precision: 2,
                        minMove: 0.01,
                    },
                    lastValueVisible: true,
                    priceLineVisible: true,
                };
            }

            // Use area series for actual data (more professional look)
            const areaSeries = window.heroChart.addAreaSeries(seriesOptions);
            window.currentSeries = areaSeries;

            // Add prediction line series if predictions are enabled
            if (showPredictions) {
                const predictionSeriesOptions = {
                    color: '#ff6b35', // Orange color for predictions
                    lineWidth: 3,
                    lineStyle: 2, // Dashed line
                    priceFormat: {
                        type: 'price',
                        precision: 2,
                        minMove: 0.01,
                    },
                    lastValueVisible: true,
                    priceLineVisible: true,
                };

                const predictionLineSeries = window.heroChart.addLineSeries(predictionSeriesOptions);
                window.predictionSeries = predictionLineSeries;
            }

            // Add chart legend for dual lines
            addDualLineChartLegend(symbol, usedSource, showPredictions);

            // Add professional trust badge
            const heroChartElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
            if (heroChartElement) {
                // Remove existing badge if present
                const existingBadge = heroChartElement.querySelector('.data-source-indicator');
                if (existingBadge) {
                    existingBadge.remove();
                }

                const trustBadge = document.createElement('div');
                trustBadge.className = 'data-source-indicator';
                trustBadge.innerHTML = `<i class="fas fa-shield-check"></i> ${usedSource} 데이터`;
                heroChartElement.appendChild(trustBadge);
            }

            // Format data
            console.log('Raw data before formatting:', data.length, 'items');

            const formattedData = data.map((item, index) => {
                // More comprehensive field checking
                const time = item.date || item.time || item.datetime || item.timestamp;
                const value = parseFloat(
                    item.close || item.price || item.value || item.c ||
                    item.Close || item.Price || item.Value || item.adjusted_close
                );

                if (index < 2) {
                    console.log(`Item ${index}:`, {
                        extractedTime: time,
                        extractedValue: value
                    });
                }

                // Convert date string to timestamp if needed
                let processedTime = time;
                if (typeof time === 'string') {
                    // Try to parse as date
                    const parsed = new Date(time);
                    if (!isNaN(parsed.getTime())) {
                        processedTime = Math.floor(parsed.getTime() / 1000); // Convert to seconds
                    }
                } else if (typeof time === 'number' && time > 1000000000000) {
                    // If it's a millisecond timestamp, convert to seconds
                    processedTime = Math.floor(time / 1000);
                }

                return { time: processedTime, value, originalIndex: index };
            }).filter((item) => {
                const isValid = item.time && !isNaN(item.value) && item.value > 0;
                if (!isValid && item.originalIndex < 3) {
                    console.log(`Filtered out item ${item.originalIndex}:`, item);
                }
                return isValid;
            });

            console.log('Formatted data for chart:', formattedData.slice(0, 5));
            console.log('Total formatted data points:', formattedData.length);

            // Set actual data to the area series
            areaSeries.setData(formattedData);
            console.log('Chart data set successfully');

            // Generate and set prediction data if enabled
            if (showPredictions && window.predictionSeries) {
                const predictionData = await generatePredictionData(formattedData, symbol);
                window.predictionSeries.setData(predictionData);
                console.log('Prediction data set successfully');
            }

            if (formattedData.length > 0) {
                window.heroChart.timeScale().fitContent();
                console.log('Chart time scale fitted');
            }

            updateChartTitle(symbol, data[data.length - 1]);
        } else {
            console.error('No data or chart not available');
            // Use sample data as fallback
            if (window.heroChart && typeof window.heroChart.addLineSeries === 'function') {
                const sampleData = generateSampleData();

                try {
                    if (window.currentSeries) {
                        window.heroChart.removeSeries(window.currentSeries);
                    }
                } catch (e) {
                    console.log('No existing series to remove');
                }

                const lineSeries = window.heroChart.addLineSeries({
                    color: '#ffd700',
                    lineWidth: 2,
                });
                window.currentSeries = lineSeries;
                lineSeries.setData(sampleData);
                console.log('Sample data loaded as fallback');
            }
        }
    } catch (error) {
        console.error('Stock chart load error:', error);
        // Fallback to sample data
        if (window.heroChart && typeof window.heroChart.addLineSeries === 'function') {
            const sampleData = generateSampleData();

            try {
                if (window.currentSeries) {
                    window.heroChart.removeSeries(window.currentSeries);
                }
            } catch (e) {
                console.log('No existing series to remove');
            }

            const lineSeries = window.heroChart.addLineSeries({
                color: '#ffd700',
                lineWidth: 2,
            });
            window.currentSeries = lineSeries;
            lineSeries.setData(sampleData);
            console.log('Sample data loaded as error fallback');
        }
    }
}

// Generate sample data for fallback
function generateSampleData() {
    const data = [];
    const startPrice = 150;
    let price = startPrice;
    const startDate = new Date('2024-01-01');

    for (let i = 0; i < 100; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);

        price += (Math.random() - 0.5) * 5;
        price = Math.max(price, startPrice * 0.7);
        price = Math.min(price, startPrice * 1.5);

        data.push({
            time: date.toISOString().split('T')[0],
            value: parseFloat(price.toFixed(2))
        });
    }

    return data;
}

// Generate prediction data based on actual data
async function generatePredictionData(actualData, symbol) {
    if (!actualData || actualData.length === 0) {
        return [];
    }

    // Try to fetch real prediction data from API first
    try {
        const response = await fetch(`${API_BASE_URL}/charts/predictions/${symbol}/`);
        if (response.ok) {
            const predictionData = await response.json();
            if (predictionData && predictionData.length > 0) {
                return predictionData.map(item => ({
                    time: item.time || item.date,
                    value: parseFloat(item.predicted_price || item.value)
                }));
            }
        }
    } catch (error) {
        console.log('Could not fetch prediction data, generating sample predictions:', error);
    }

    // Generate sample prediction data based on actual data
    const predictionData = [];
    const startIndex = Math.max(0, actualData.length - 30); // Show predictions for last 30 days

    for (let i = startIndex; i < actualData.length; i++) {
        const actualPoint = actualData[i];
        // Generate prediction with some variance from actual price
        const variance = (Math.random() - 0.5) * 0.1; // ±10% variance
        const predictedValue = actualPoint.value * (1 + variance);

        predictionData.push({
            time: actualPoint.time,
            value: parseFloat(predictedValue.toFixed(2))
        });
    }

    // Extend predictions into the future (next 7 days)
    const lastActualPoint = actualData[actualData.length - 1];
    const lastTime = typeof lastActualPoint.time === 'string'
        ? new Date(lastActualPoint.time + 'T00:00:00Z')
        : new Date(lastActualPoint.time * 1000);

    for (let i = 1; i <= 7; i++) {
        const futureDate = new Date(lastTime);
        futureDate.setDate(futureDate.getDate() + i);

        const trend = (Math.random() - 0.5) * 0.05; // ±5% daily trend
        const lastPrediction = predictionData[predictionData.length - 1];
        const futureValue = lastPrediction.value * (1 + trend);

        predictionData.push({
            time: Math.floor(futureDate.getTime() / 1000),
            value: parseFloat(futureValue.toFixed(2))
        });
    }

    return predictionData;
}

// Add dual-line chart legend
function addDualLineChartLegend(symbol, dataSource, showPredictions) {
    const heroChartElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
    if (!heroChartElement) return;

    // Remove existing legend
    const existingLegend = heroChartElement.querySelector('.chart-legend');
    if (existingLegend) {
        existingLegend.remove();
    }

    const legend = document.createElement('div');
    legend.className = 'chart-legend';
    legend.innerHTML = `
        <div class="legend-item">
            <div class="legend-color actual-color"></div>
            <span>실제 데이터 (${symbol})</span>
        </div>
        ${showPredictions ? `
        <div class="legend-item">
            <div class="legend-color prediction-color"></div>
            <span>예측 데이터</span>
        </div>
        ` : ''}
        <div class="legend-source">
            <i class="fas fa-info-circle"></i>
            <span>출처: ${dataSource}</span>
        </div>
    `;

    heroChartElement.appendChild(legend);
}

// Update chart title
function updateChartTitle(symbol, latestData) {
    const titleElement = document.querySelector('.chart-title');
    if (titleElement && latestData) {
        const price = latestData.close || latestData.price || latestData.value || 0;
        titleElement.textContent = `${symbol} - $${price.toFixed(2)}`;
    }
}

// Load market data
async function loadMarketData() {
    console.log('Loading market data...');
    try {
        console.log('Loading popular stocks...');
        await loadPopularStocks();

        console.log('Loading crypto data...');
        await loadCryptoData();

        console.log('Loading market indices...');
        await loadMarketIndices();
    } catch (error) {
        console.error('Error in loadMarketData:', error);
    }
    console.log('Market data loading completed');
}

// Load popular stocks
async function loadPopularStocks() {
    try {
        console.log('Loading popular stocks...');
        const symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN'];
        const stockData = [];

        for (const symbol of symbols) {
            try {
                const response = await fetch(`${API_BASE_URL}/market-data/quote/${symbol}/`);
                if (response.ok) {
                    const data = await response.json();
                    stockData.push({ symbol, ...data });
                } else {
                    console.error(`Failed to fetch ${symbol} data`);
                    stockData.push({ symbol, error: true });
                }
            } catch (error) {
                console.error(`Error loading ${symbol}:`, error);
                stockData.push({ symbol, error: true });
            }
        }

        console.log('Stock data loaded:', stockData);
        displayPopularStocks(stockData);
    } catch (error) {
        console.error('Popular stocks load error:', error);
    }
}

// Display popular stocks
function displayPopularStocks(stockData) {
    const container = document.querySelector('.popular-stocks');
    if (!container) {
        console.error('Popular stocks container not found');
        return;
    }

    console.log('Stock data received:', stockData);

    const html = stockData.map(stock => {
        if (stock.error) {
            console.error('Stock error:', stock.symbol, stock.error);
            return '';
        }

        console.log('Processing stock:', stock);

        const price = stock.price || stock.current_price || stock.close || stock.value || 0;
        const change = stock.change || stock.change_percent || stock.percent_change || 0;
        const isPositive = change >= 0;

        return `
            <div class="stock-item" data-symbol="${stock.symbol}">
                <div class="stock-info">
                    <h4>${stock.symbol}</h4>
                    <p class="stock-price">$${price.toFixed(2)}</p>
                </div>
                <div class="stock-change ${isPositive ? 'positive' : 'negative'}">
                    ${isPositive ? '+' : ''}${change.toFixed(2)}%
                </div>
            </div>
        `;
    }).join('');

    console.log('Generated HTML:', html);
    container.innerHTML = html || '<p>Loading stock data...</p>';
}

// Load crypto data
async function loadCryptoData() {
    console.log('🚀 CRYPTO DATA FUNCTION CALLED!');
    console.log('loadCryptoData started...');
    const container = document.querySelector('.popular-cryptos');
    if (!container) {
        console.error('❌ Crypto container not found!');
        return;
    }

    console.log('✅ Crypto container found:', container);

    // Show loading state
    container.innerHTML = '<div class="loading-message">Loading cryptocurrency data...</div>';
    console.log('📊 Loading state set');

    try {
        const symbols = ['BTC', 'ETH', 'ADA', 'BNB'];
        const cryptoData = [];

        for (const symbol of symbols) {
            try {
                console.log(`Loading crypto data for ${symbol}...`);
                const response = await fetch(`${API_BASE_URL}/market-data/crypto/${symbol}/`);

                if (response.ok) {
                    const data = await response.json();
                    console.log(`Successfully loaded ${symbol}:`, data);
                    cryptoData.push({ symbol, ...data, success: true });
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    console.warn(`Failed to load ${symbol}:`, response.status, errorData);
                    cryptoData.push({
                        symbol,
                        error: true,
                        errorMessage: errorData.error || `Failed to load ${symbol} data`,
                        status: response.status
                    });
                }
            } catch (error) {
                console.error(`${symbol} crypto data error:`, error);
                cryptoData.push({
                    symbol,
                    error: true,
                    errorMessage: `Network error loading ${symbol}`,
                    networkError: true
                });
            }
        }

        displayCryptoData(cryptoData);
        console.log('✅ displayCryptoData called with:', cryptoData.length, 'items');
    } catch (error) {
        console.error('Crypto data load error:', error);
        container.innerHTML = `
            <div class="error-message">
                <h3>Error Loading Cryptocurrency Data</h3>
                <p>Unable to load cryptocurrency data at this time. Please try again later.</p>
                <button onclick="loadCryptoData()" class="retry-btn">Retry</button>
            </div>
        `;
    }
}

// Display crypto data
function displayCryptoData(cryptoData) {
    console.log('🎯 displayCryptoData function called!');
    console.log('📊 Crypto data to display:', cryptoData);

    const container = document.querySelector('.popular-cryptos');
    if (!container) {
        console.error('❌ Crypto container not found in displayCryptoData!');
        return;
    }

    console.log('✅ Container found in display function:', container);

    console.log('Crypto data received:', cryptoData);

    // Check if we have any successful data
    const successfulData = cryptoData.filter(crypto => crypto.success);
    const failedData = cryptoData.filter(crypto => crypto.error);

    if (successfulData.length === 0) {
        // All APIs failed
        container.innerHTML = `
            <div class="error-state">
                <h3>Cryptocurrency Data Unavailable</h3>
                <p>All cryptocurrency APIs are currently unavailable. Please try again later.</p>
                <button onclick="loadCryptoData()" class="retry-btn">Retry</button>
                <div class="error-details">
                    ${failedData.map(crypto =>
            `<small>${crypto.symbol}: ${crypto.errorMessage}</small>`
        ).join('<br>')}
                </div>
            </div>
        `;
        return;
    }

    // Mix of successful and failed data
    const html = cryptoData.map(crypto => {
        if (crypto.error) {
            return `
                <div class="crypto-item error">
                    <div class="crypto-info">
                        <h4>${crypto.symbol}</h4>
                        <p class="crypto-error">Data unavailable</p>
                        <small>${crypto.errorMessage}</small>
                    </div>
                    <div class="crypto-status error">
                        Error
                    </div>
                </div>
            `;
        }

        const price = crypto.price || crypto.current_price || 0;
        const change = crypto.change || crypto.change_percent || 0;
        const isPositive = change >= 0;
        const source = crypto.source || 'unknown';

        return `
            <div class="crypto-item success">
                <div class="crypto-info">
                    <h4>${crypto.symbol}</h4>
                    <p class="crypto-price">$${price.toFixed(2)}</p>
                    <small class="data-source">Source: ${source}</small>
                </div>
                <div class="crypto-change ${isPositive ? 'positive' : 'negative'}">
                    ${isPositive ? '+' : ''}${change.toFixed(2)}%
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// Load market indices
async function loadMarketIndices() {
    try {
        const response = await fetch(`${API_BASE_URL}/market-data/indices/`);
        if (response.ok) {
            const data = await response.json();
            displayMarketIndices(data);
        }
    } catch (error) {
        console.error('Market indices load error:', error);
    }
}

// Display market indices
function displayMarketIndices(indicesData) {
    const container = document.querySelector('.market-indices');
    if (!container) return;

    console.log('Indices data received:', indicesData);

    // Check if data is an array or needs to be converted
    let dataArray = [];
    if (Array.isArray(indicesData)) {
        dataArray = indicesData;
    } else if (indicesData && typeof indicesData === 'object') {
        // If it's an object, try to extract array or create sample data
        if (indicesData.data && Array.isArray(indicesData.data)) {
            dataArray = indicesData.data;
        } else {
            // Create sample data if API doesn't return proper format
            dataArray = [
                { name: 'S&P 500', value: '4,450.12', change: 0.75 },
                { name: 'NASDAQ', value: '13,850.45', change: -0.32 },
                { name: 'DOW', value: '34,580.23', change: 0.45 }
            ];
        }
    } else {
        // Fallback to sample data
        dataArray = [
            { name: 'S&P 500', value: '4,450.12', change: 0.75 },
            { name: 'NASDAQ', value: '13,850.45', change: -0.32 },
            { name: 'DOW', value: '34,580.23', change: 0.45 }
        ];
    }

    const html = dataArray.map(index => {
        const isPositive = index.change >= 0;
        return `
            <div class="index-item">
                <div class="index-info">
                    <h4>${index.name}</h4>
                    <p class="index-value">${index.value}</p>
                </div>
                <div class="index-change ${isPositive ? 'positive' : 'negative'}">
                    ${isPositive ? '+' : ''}${index.change}%
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// Navigation and UI functions
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function updateActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// Initialize stock selector dropdown
function initializeStockSelector() {
    console.log('Initializing stock selector...');
    const stockSelect = document.getElementById('stockSelect');
    const currentPriceInput = document.getElementById('currentPrice');

    console.log('Stock select element:', stockSelect);

    if (!stockSelect) {
        console.error('Stock select element not found!');
        return;
    }

    // Popular stocks to populate the dropdown
    const popularStocks = [
        // US Stocks
        { symbol: 'AAPL', name: 'Apple Inc.' },
        { symbol: 'GOOGL', name: 'Alphabet Inc.' },
        { symbol: 'MSFT', name: 'Microsoft Corporation' },
        { symbol: 'AMZN', name: 'Amazon.com Inc.' },
        { symbol: 'TSLA', name: 'Tesla Inc.' },
        { symbol: 'META', name: 'Meta Platforms Inc.' },
        { symbol: 'NVDA', name: 'NVIDIA Corporation' },
        { symbol: 'NFLX', name: 'Netflix Inc.' },
        { symbol: 'JPM', name: 'JPMorgan Chase & Co.' },
        { symbol: 'V', name: 'Visa Inc.' },
        // Korean Stocks (KRX)
        { symbol: '005930.KS', name: '삼성전자' },
        { symbol: '000660.KS', name: 'SK하이닉스' },
        { symbol: '035420.KS', name: 'NAVER' },
        { symbol: '207940.KS', name: '삼성바이오로직스' },
        { symbol: '006400.KS', name: '삼성SDI' },
        { symbol: '051910.KS', name: 'LG화학' },
        { symbol: '005380.KS', name: '현대차' },
        { symbol: '012330.KS', name: '현대모비스' },
        // Crypto (for demonstration)
        { symbol: 'BTC-USD', name: 'Bitcoin USD' },
        { symbol: 'ETH-USD', name: 'Ethereum USD' }
    ];

    // Clear existing options except the first one
    while (stockSelect.children.length > 1) {
        stockSelect.removeChild(stockSelect.lastChild);
    }

    console.log('Adding stock options...');

    // Add stock options
    popularStocks.forEach(stock => {
        const option = document.createElement('option');
        option.value = stock.symbol;
        option.textContent = `${stock.symbol} - ${stock.name}`;
        stockSelect.appendChild(option);
    });

    console.log(`Added ${popularStocks.length} stock options to dropdown`);

    // Add event listener for stock selection
    stockSelect.addEventListener('change', async function () {
        const selectedSymbol = this.value;
        if (selectedSymbol) {
            console.log('Selected stock:', selectedSymbol);

            // Load current price
            try {
                const priceData = await fetchStockPrice(selectedSymbol);
                if (priceData && priceData.price) {
                    currentPriceInput.value = priceData.price.toFixed(2);
                } else {
                    currentPriceInput.value = 'N/A';
                }
            } catch (error) {
                console.error('Error fetching stock price:', error);
                currentPriceInput.value = 'Error';
            }
        } else {
            currentPriceInput.value = '';
        }
    });
}

// Fetch current stock price
async function fetchStockPrice(symbol) {
    try {
        // Use the existing Django API endpoints
        const response = await fetch(`/api/market-data/quote/${symbol}/`);
        if (response.ok) {
            const data = await response.json();
            console.log('Stock price data:', data);
            // Extract price from the response (adjust based on actual API response format)
            if (data.price) {
                return { price: parseFloat(data.price) };
            } else if (data.current_price) {
                return { price: parseFloat(data.current_price) };
            } else if (data.close) {
                return { price: parseFloat(data.close) };
            }
        }
        throw new Error('Price not found in API response');
    } catch (error) {
        console.error('Error fetching stock price:', error);
        return null;
    }
}

// Remove the other API functions since we're using the Django endpoints
async function fetchFromAlphaVantage(symbol) {
    throw new Error('Use Django API instead');
}

async function fetchFromYahooFinance(symbol) {
    throw new Error('Use Django API instead');
}

async function fetchFromTwelveData(symbol) {
    throw new Error('Use Django API instead');
}

// Authentication functions
async function validateToken(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ token })
        });

        if (response.ok) {
            const userData = await response.json();
            updateUIForLoggedInUser(userData);
        } else {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        }
    } catch (error) {
        console.error('Token validation error:', error);
    }
}

function updateUIForLoggedInUser(userData) {
    // Update UI to show user is logged in
    const loginBtn = document.querySelector('.login-btn');
    const signupBtn = document.querySelector('.signup-btn');

    if (loginBtn) loginBtn.style.display = 'none';
    if (signupBtn) signupBtn.style.display = 'none';

    // Add user menu or profile section
    console.log('User logged in:', userData);
}

// Chart and ranking functions
async function loadCharts() {
    console.log('Loading charts...');

    try {
        const response = await fetch(`${API_BASE_URL}/charts/`);
        console.log('Charts API response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Charts API response data:', data);

            // Handle different response formats
            let charts = data;
            if (data && typeof data === 'object' && !Array.isArray(data)) {
                // If response is an object, look for common array properties
                if (Array.isArray(data.results)) {
                    charts = data.results;
                    console.log('Using data.results array');
                } else if (Array.isArray(data.charts)) {
                    charts = data.charts;
                    console.log('Using data.charts array');
                } else if (Array.isArray(data.data)) {
                    charts = data.data;
                    console.log('Using data.data array');
                } else {
                    console.log('Response is object but no array found, using sample charts');
                    displaySampleCharts();
                    return;
                }
            }

            displayCharts(charts);
        } else {
            console.log('Charts API failed with status:', response.status, 'using sample charts');
            displaySampleCharts();
        }
    } catch (error) {
        console.error('Charts load error:', error);
        displaySampleCharts();
    }
}

function displayCharts(charts) {
    const chartsGrid = document.getElementById('chartsGrid');
    if (!chartsGrid) return;

    console.log('Charts data received:', charts);
    console.log('Charts data type:', typeof charts);
    console.log('Charts is array:', Array.isArray(charts));

    if (!Array.isArray(charts)) {
        console.error('Charts data is not an array:', charts);
        chartsGrid.innerHTML = '<div class="no-results">차트 데이터 형식 오류</div>';
        return;
    }

    if (charts.length === 0) {
        chartsGrid.innerHTML = '<div class="no-results">표시할 차트가 없습니다</div>';
        return;
    }

    try {
        const chartsHTML = charts.map((chart, index) => {
            console.log(`Processing chart ${index}:`, chart);

            // Validate required fields with fallbacks
            const stockName = chart.stock_name || 'Unknown Stock';
            const stockSymbol = chart.stock_symbol || 'N/A';
            const username = (chart.user && chart.user.username) ? chart.user.username : 'Anonymous';
            const currentPrice = chart.current_price || 0;
            const predictedPrice = chart.predicted_price || 0;
            const status = chart.status || 'pending';
            const targetDate = chart.target_date || new Date().toISOString().split('T')[0];
            const createdAt = chart.created_at || new Date().toISOString().split('T')[0];

            return `
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>${stockName} (${stockSymbol})</h3>
                        <span class="chart-status ${status}">${getStatusText(status)}</span>
                    </div>
                    <div class="chart-preview-area">
                        <div class="mini-chart-container">
                            <canvas class="dynamic-mini-chart" width="250" height="100" data-symbol="${stockSymbol}" data-current="${currentPrice}" data-predicted="${predictedPrice}"></canvas>
                        </div>
                    </div>
                    <div class="chart-info">
                        <div class="price-info">
                            <div class="price-item">
                                <span class="label">현재가:</span>
                                <span class="value">${formatPrice(currentPrice)}</span>
                            </div>
                            <div class="price-item">
                                <span class="label">예측가:</span>
                                <span class="value predicted">${formatPrice(predictedPrice)}</span>
                            </div>
                        </div>
                        <div class="chart-meta">
                            <p class="user">예측자: ${username}</p>
                            <p class="date">목표일: ${formatDate(targetDate)}</p>
                            <p class="created">생성일: ${formatDate(createdAt)}</p>
                        </div>
                    </div>
                    <div class="chart-actions">
                        <button class="btn btn-sm btn-outline" onclick="viewChart(${chart.id || 0})">
                            상세보기
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        chartsGrid.innerHTML = chartsHTML;
        console.log('Charts successfully displayed');

        // Initialize dynamic mini charts after HTML is inserted
        setTimeout(() => {
            const dynamicCharts = document.querySelectorAll('.dynamic-mini-chart');
            dynamicCharts.forEach(canvas => {
                const symbol = canvas.getAttribute('data-symbol');
                const currentPrice = parseFloat(canvas.getAttribute('data-current')) || 100;
                const predictedPrice = parseFloat(canvas.getAttribute('data-predicted')) || 105;

                initializeDynamicMiniChart(canvas, symbol, currentPrice, predictedPrice);
            });
        }, 100);

    } catch (error) {
        console.error('Error generating charts HTML:', error);
        chartsGrid.innerHTML = '<div class="no-results">차트 표시 중 오류 발생</div>';
    }
}

function displaySampleCharts() {
    const sampleCharts = [
        {
            id: 1,
            user: { username: '투자왕' },
            stock_name: '애플',
            stock_symbol: 'AAPL',
            predicted_price: 185.50,
            current_price: 182.30,
            target_date: '2025-09-15',
            created_at: '2025-09-01',
            status: 'pending'
        },
        {
            id: 2,
            user: { username: '구글러' },
            stock_name: '구글',
            stock_symbol: 'GOOGL',
            predicted_price: 145.75,
            current_price: 142.20,
            target_date: '2025-09-20',
            created_at: '2025-08-30',
            status: 'pending'
        }
    ];

    displayCharts(sampleCharts);
}

// Utility functions
function getStatusText(status) {
    const statusMap = {
        'pending': '예측중',
        'completed': '완료됨',
        'expired': '만료됨'
    };
    return statusMap[status] || status;
}

function formatPrice(price) {
    return typeof price === 'number' ? `$${price.toFixed(2)}` : '$0.00';
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

function viewChart(chartId) {
    // For now, just show an alert with chart details
    alert(`Chart details for ID: ${chartId}\n\nThis feature will show detailed chart analysis and prediction history.`);
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

// Real-time updates
function startRealTimeUpdates() {
    setInterval(() => {
        loadMarketData();
    }, 30000); // Update every 30 seconds
}

// API Integration Functions for Tiingo and Marketstack
async function loadTiingoData(symbol) {
    try {
        console.log(`Loading Tiingo data for ${symbol}...`);
        const response = await fetch(`${API_BASE_URL}/market-data/tiingo/${symbol}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Tiingo data received:', data);
        return data;
    } catch (error) {
        console.error(`Tiingo API error for ${symbol}:`, error);
        return null;
    }
}

async function loadMarketstackData(symbol) {
    try {
        console.log(`Loading Marketstack data for ${symbol}...`);
        const response = await fetch(`${API_BASE_URL}/market-data/marketstack/${symbol}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Marketstack data received:', data);
        return data;
    } catch (error) {
        console.error(`Marketstack API error for ${symbol}:`, error);
        return null;
    }
}

async function loadEnhancedMarketData() {
    console.log('Loading enhanced market data with multiple APIs...');

    const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA'];
    const apiSources = [
        { name: 'CoinGecko', endpoint: 'coingecko' },
        { name: 'Alpha Vantage', endpoint: 'quote' },
        { name: 'Tiingo', endpoint: 'tiingo' },
        { name: 'Marketstack', endpoint: 'marketstack' },
        { name: 'Crypto API', endpoint: 'crypto' }
    ];

    const container = document.querySelector('.api-comparison .api-results');
    if (!container) {
        console.log('API comparison container not found');
        return;
    }

    let html = '<div class="api-grid">';

    for (const symbol of symbols) {
        html += `<div class="symbol-section"><h4>${symbol}</h4>`;

        for (const api of apiSources) {
            try {
                const response = await fetch(`${API_BASE_URL}/market-data/${api.endpoint}/${symbol}/`);
                const data = await response.json();

                if (data && !data.error) {
                    const price = data.price || data.current_price || data.close || 'N/A';
                    const change = data.change || data.change_percent || 'N/A';

                    html += `
                        <div class="api-result">
                            <strong>${api.name}:</strong> 
                            $${typeof price === 'number' ? price.toFixed(2) : price}
                            <span class="change">(${typeof change === 'number' ? change.toFixed(2) : change}%)</span>
                        </div>
                    `;
                } else {
                    html += `<div class="api-result error"><strong>${api.name}:</strong> Error loading data</div>`;
                }
            } catch (error) {
                html += `<div class="api-result error"><strong>${api.name}:</strong> ${error.message}</div>`;
            }
        }

        html += '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
}

async function testAllAPIs(symbol = 'AAPL') {
    console.log(`Testing all APIs for ${symbol}...`);

    const apis = [
        { name: 'Alpha Vantage', url: `${API_BASE_URL}/market-data/quote/${symbol}/` },
        { name: 'Twelve Data', url: `${API_BASE_URL}/market-data/quote/${symbol}/` },
        { name: 'Finnhub', url: `${API_BASE_URL}/market-data/enhanced/${symbol}/` },
        { name: 'Polygon', url: `${API_BASE_URL}/market-data/polygon/historical/${symbol}/` },
        { name: 'Tiingo', url: `${API_BASE_URL}/market-data/tiingo/${symbol}/` },
        { name: 'Marketstack', url: `${API_BASE_URL}/market-data/marketstack/${symbol}/` }
    ];

    const results = {};

    for (const api of apis) {
        try {
            console.log(`Testing ${api.name}...`);
            const response = await fetch(api.url);
            const data = await response.json();
            results[api.name] = {
                status: response.status,
                success: response.ok,
                data: data,
                price: data.price || data.current_price || data.close || 'N/A'
            };
        } catch (error) {
            results[api.name] = {
                status: 'Error',
                success: false,
                error: error.message
            };
        }
    }

    console.log('API Test Results:', results);

    // Display results
    const container = document.querySelector('.api-comparison .api-results');
    if (container) {
        let html = `<h4>API Test Results for ${symbol}</h4><div class="test-results">`;

        Object.entries(results).forEach(([apiName, result]) => {
            const statusClass = result.success ? 'success' : 'error';
            html += `
                <div class="api-result ${statusClass}">
                    <strong>${apiName}:</strong> 
                    Status: ${result.status} | 
                    Price: $${result.price}
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    return results;
}

function addAPITestingUI() {
    const marketSection = document.querySelector('#market');
    if (!marketSection) return;

    if (!document.querySelector('.api-comparison')) {
        const apiContainer = document.createElement('div');
        apiContainer.className = 'api-comparison';
        apiContainer.innerHTML = `
            <div class="api-testing-header">
                <h3>Multi-API Market Data Testing</h3>
                <div class="api-controls">
                    <button onclick="loadEnhancedMarketData()" class="btn btn-primary">Test All APIs</button>
                    <button onclick="testAllAPIs('AAPL')" class="btn btn-secondary">Test AAPL APIs</button>
                    <button onclick="testAllAPIs('GOOGL')" class="btn btn-secondary">Test GOOGL APIs</button>
                    <button onclick="testAllAPIs('TSLA')" class="btn btn-secondary">Test TSLA APIs</button>
                </div>
            </div>
            <div class="api-results">
                <p>Click buttons above to test different API sources for market data.</p>
            </div>
        `;

        const marketData = document.querySelector('.market-data');
        if (marketData) {
            marketData.parentNode.insertBefore(apiContainer, marketData.nextSibling);
        }
    }
}

// Initialize everything when the page loads
window.addEventListener('load', function () {
    console.log('Page fully loaded, initializing application...');
    if (typeof LightweightCharts === 'undefined') {
        console.error('LightweightCharts library not loaded!');
    }
});

// Login Modal Functions
function showLoginModal() {
    console.log('Login modal requested');

    // Create modal HTML using existing CSS classes
    const modalHTML = `
        <div id="loginModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeLoginModal()">&times;</span>
                <h2>로그인</h2>
                <div class="social-login">
                    <p>소셜 로그인</p>
                    <button class="btn-google" onclick="loginWithGoogle()">
                        <span>Google로 로그인</span>
                    </button>
                    <button class="btn-apple" onclick="loginWithApple()">
                        <span>Apple로 로그인</span>
                    </button>
                </div>
                <form id="loginForm" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label for="loginEmail">이메일</label>
                        <input type="email" id="loginEmail" name="email" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="loginPassword">비밀번호</label>
                        <input type="password" id="loginPassword" name="password" class="form-input" required>
                    </div>
                    <button type="submit" class="btn-primary">로그인</button>
                </form>
                <div class="modal-footer">
                    <p>계정이 없으신가요? <a href="#" onclick="showRegisterModal()">회원가입</a></p>
                </div>
            </div>
        </div>
    `;

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Show modal
    const modal = document.getElementById('loginModal');
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling

    // Add event listener to close modal when clicking outside
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeLoginModal();
        }
    });
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = ''; // Restore scrolling
    }
}

function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    console.log('Login attempt:', email);

    // TODO: Implement actual login logic with backend
    alert('로그인 기능은 현재 개발 중입니다.');
    closeLoginModal();
}

function showRegisterModal() {
    closeLoginModal();

    const modalHTML = `
        <div id="registerModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeRegisterModal()">&times;</span>
                <h2>회원가입</h2>
                <div class="social-login">
                    <p>소셜 회원가입</p>
                    <button class="btn-google" onclick="registerWithGoogle()">
                        <span>Google로 회원가입</span>
                    </button>
                    <button class="btn-apple" onclick="registerWithApple()">
                        <span>Apple로 회원가입</span>
                    </button>
                </div>
                <form id="registerForm" onsubmit="handleRegister(event)">
                    <div class="form-group">
                        <label for="regName">이름</label>
                        <input type="text" id="regName" name="name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="regEmail">이메일</label>
                        <input type="email" id="regEmail" name="email" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="regPassword">비밀번호</label>
                        <input type="password" id="regPassword" name="password" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="regConfirmPassword">비밀번호 확인</label>
                        <input type="password" id="regConfirmPassword" name="confirmPassword" class="form-input" required>
                    </div>
                    <button type="submit" class="btn-primary">회원가입</button>
                </form>
                <div class="modal-footer">
                    <p>이미 계정이 있으신가요? <a href="#" onclick="showLoginModal()">로그인</a></p>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Show modal
    const modal = document.getElementById('registerModal');
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling

    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeRegisterModal();
        }
    });
}

function closeRegisterModal() {
    const modal = document.getElementById('registerModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = ''; // Restore scrolling
    }
}

function handleRegister(event) {
    event.preventDefault();
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;

    if (password !== confirmPassword) {
        alert('비밀번호가 일치하지 않습니다.');
        return;
    }

    // TODO: Implement actual registration logic
    alert('회원가입 기능은 현재 개발 중입니다.');
    closeRegisterModal();
}

function loginWithGoogle() {
    console.log('Login with Google clicked');
    // Check if our triggerGoogleSignIn function exists
    if (typeof window.triggerGoogleSignIn === 'function') {
        window.triggerGoogleSignIn();
    } else {
        console.log('Google Sign-In function not available, initializing...');
        showNotification('로딩 중', 'Google 로그인을 초기화하고 있습니다...', 'info');

        // Make sure Google auth is initialized
        if (typeof initGoogleAuth === 'function') {
            initGoogleAuth();

            // Wait a moment for initialization then retry
            setTimeout(() => {
                if (typeof window.triggerGoogleSignIn === 'function') {
                    window.triggerGoogleSignIn();
                } else {
                    console.log('Still no Google Sign-In function available after initialization');
                    showNotification('오류', 'Google 로그인을 불러올 수 없습니다. 페이지를 새로고침해 주세요.', 'error');
                }
            }, 1000);
        } else {
            console.error('Google authentication module not loaded');
            showNotification('오류', 'Google 로그인 모듈을 찾을 수 없습니다.', 'error');
        }
    }
} function loginWithApple() {
    // TODO: Implement Apple OAuth  
    showNotification('준비중', 'Apple 로그인 기능은 현재 개발 중입니다.', 'info');
}

function registerWithGoogle() {
    // Google OAuth handles both login and registration through the same flow
    loginWithGoogle();

    // Optionally show a different notification for signup
    showNotification('회원가입', 'Google 계정으로 가입을 진행합니다...', 'info');
}

function registerWithApple() {
    // TODO: Implement Apple OAuth for registration
    showNotification('준비중', 'Apple 회원가입 기능은 현재 개발 중입니다.', 'info');
}

// Prediction Functions
function startPrediction() {
    console.log('Start prediction clicked');
    alert('예측 기능은 현재 개발 중입니다. 곧 출시 예정입니다!');
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Utility function to validate token
function validateToken(token) {
    // TODO: Implement token validation with backend
    console.log('Validating token:', token);
}

// Add responsive chart resize handler
function addChartResizeHandler() {
    let resizeTimeout;

    function resizeCharts() {
        const isMobile = window.innerWidth <= 768;
        const isVerySmall = window.innerWidth <= 480;

        // Resize hero chart
        const heroChartElement = document.getElementById('heroChart');
        if (heroChartElement && window.heroChart) {
            // Calculate safe dimensions that won't overflow
            const containerWidth = heroChartElement.parentElement.clientWidth || window.innerWidth;
            const safeWidth = Math.min(containerWidth - 20, window.innerWidth - 20);
            const safeHeight = isVerySmall ? 250 : (isMobile ? 300 : 400);

            try {
                window.heroChart.applyOptions({
                    width: safeWidth,
                    height: safeHeight
                });

                // Update chart element dimensions
                heroChartElement.style.width = safeWidth + 'px';
                heroChartElement.style.height = safeHeight + 'px';
            } catch (error) {
                console.error('Error resizing hero chart:', error);
            }
        }

        // Resize prediction chart
        const predictionChartElement = document.getElementById('predictionChart');
        if (predictionChartElement && window.predictionChart) {
            // Calculate safe dimensions
            const containerWidth = predictionChartElement.parentElement.clientWidth || window.innerWidth;
            const safeWidth = Math.min(containerWidth - 20, window.innerWidth - 20);
            const safeHeight = isVerySmall ? 250 : (isMobile ? 280 : 300);

            try {
                window.predictionChart.applyOptions({
                    width: newWidth,
                    height: newHeight
                });

                // Update chart element height
                predictionChartElement.style.height = newHeight + 'px';
            } catch (error) {
                console.error('Error resizing prediction chart:', error);
            }
        }
    }

    // Add window resize event listener with debouncing
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(resizeCharts, 250);
    });

    // Add orientation change event listener for mobile devices
    window.addEventListener('orientationchange', function () {
        setTimeout(resizeCharts, 500); // Delay to allow orientation change to complete
    });
}

// Initialize mobile-optimized chart configuration
// Helper function to get TradingView Pro chart options
function getTradingViewProChartOptions(width, height) {
    // Use tvPro options if available, otherwise use our custom defined options
    if (window.tvPro && window.tvPro.getChartOptions) {
        const options = window.tvPro.getChartOptions();
        if (width) options.width = width;
        if (height) options.height = height;
        return options;
    }

    // If tvPro is not available, use enhanced TradingView-like options
    const isDarkMode = !document.body.classList.contains('light-theme');
    const isMobile = window.innerWidth <= 768;
    const isVerySmall = window.innerWidth <= 480;

    // Ensure chart is never wider than screen
    const safeWidth = width ? Math.min(width, window.innerWidth - 20) : 'auto';
    const safeHeight = height ? (isVerySmall ? 250 : (isMobile ? 300 : height)) : 400;

    return {
        width: safeWidth,
        height: safeHeight,
        layout: {
            background: { type: 'solid', color: isDarkMode ? '#131722' : '#FFFFFF' },
            textColor: isDarkMode ? '#d1d4dc' : '#131722',
            fontSize: isVerySmall ? 10 : (isMobile ? 11 : 12),
            fontFamily: "'Inter', 'Noto Sans KR', sans-serif",
        },
        grid: {
            vertLines: {
                color: isDarkMode ? 'rgba(42, 46, 57, 0.6)' : 'rgba(42, 46, 57, 0.1)',
                visible: !isVerySmall,
            },
            horzLines: {
                color: isDarkMode ? 'rgba(42, 46, 57, 0.6)' : 'rgba(42, 46, 57, 0.1)',
                visible: !isVerySmall,
            },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                width: 1,
                color: isDarkMode ? '#758696' : '#9DB2BD',
                style: LightweightCharts.LineStyle.Dashed,
            },
            horzLine: {
                width: 1,
                color: isDarkMode ? '#758696' : '#9DB2BD',
                style: LightweightCharts.LineStyle.Dashed,
            }
        },
        rightPriceScale: {
            borderColor: isDarkMode ? '#242732' : '#E0E3EB',
            scaleMargins: {
                top: 0.1,
                bottom: 0.1,
            },
            minimumWidth: isMobile ? 40 : 60,
        },
        timeScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
            timeVisible: true,
            secondsVisible: false,
            fixLeftEdge: true,
            fixRightEdge: true,
        },
        handleScroll: {
            mouseWheel: !isMobile,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: isMobile,
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: !isMobile,
            pinch: isMobile,
        },
        kineticScroll: {
            touch: isMobile,
            mouse: false,
        },
    };
}

// Prediction submission functionality
async function submitPrediction() {
    console.log('Submit prediction clicked');

    // Check if user is authenticated
    const token = localStorage.getItem('token');
    if (!token) {
        alert('예측을 저장하려면 로그인이 필요합니다.');
        showLoginModal();
        return;
    }

    // Get form values
    const stockSelect = document.getElementById('stockSelect');
    const currentPrice = document.getElementById('currentPrice');
    const predictedPrice = document.getElementById('predictedPrice');
    const targetDate = document.getElementById('targetDate');
    const duration = document.getElementById('duration');
    const sharePublicly = document.getElementById('isPublic');
    const reasoning = document.getElementById('reasoning');
    const confidence = document.getElementById('confidence');

    // Validate required fields
    if (!stockSelect.value) {
        alert('종목을 선택해주세요.');
        return;
    }

    if (!currentPrice.value || currentPrice.value === 'N/A' || currentPrice.value === 'Error') {
        alert('현재 가격이 로드되지 않았습니다. 다른 종목을 선택해보세요.');
        return;
    }

    if (!predictedPrice.value) {
        alert('예측 가격을 입력해주세요.');
        return;
    }

    if (!targetDate.value) {
        alert('목표 날짜를 선택해주세요.');
        return;
    }

    // Calculate target date
    const now = new Date();
    const target = new Date(targetDate.value);
    const durationDays = Math.ceil((target - now) / (1000 * 60 * 60 * 24));

    // Create prediction object for API
    const predictionData = {
        stock_symbol: stockSelect.value,
        stock_name: stockSelect.options[stockSelect.selectedIndex].text,
        current_price: parseFloat(currentPrice.value),
        predicted_price: parseFloat(predictedPrice.value),
        target_date: targetDate.value,
        duration_days: durationDays,
        is_public: sharePublicly ? sharePublicly.checked : true,
        reasoning: reasoning ? reasoning.value : '',
        confidence: confidence ? parseInt(confidence.value) : 75
    };

    console.log('Prediction data:', predictionData);

    try {
        // Submit to backend API
        const response = await fetch('/api/charts/predictions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(predictionData)
        });

        if (response.status === 402) {
            // Payment required
            const data = await response.json();
            alert('무료 접근 횟수를 모두 사용했습니다. 구독이 필요합니다.');
            window.location.href = 'subscription.html?payment_required=true';
            return;
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || '예측 저장에 실패했습니다.');
        }

        const data = await response.json();
        console.log('Prediction saved:', data);

        // Show success message
        showNotification('예측이 성공적으로 저장되었습니다! 공개 차트 보드에서 확인할 수 있습니다.', 'success');

        // Reset form
        resetPredictionForm();

        // Redirect to my predictions page
        setTimeout(() => {
            window.location.href = 'my-predictions.html';
        }, 2000);

    } catch (error) {
        console.error('Error submitting prediction:', error);
        alert('예측 저장 중 오류가 발생했습니다: ' + error.message);
    }
}

// Helper function to get CSRF token
function getCsrfToken() {
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
    return cookieValue || '';
}

// Helper function to reset prediction form
function resetPredictionForm() {
    const form = document.querySelector('.prediction-form');
    if (form) {
        // Reset all form inputs
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = input.id === 'isPublic'; // Keep isPublic checked by default
            } else {
                input.value = '';
            }
        });

        // Reset to first step
        const steps = form.querySelectorAll('.form-step');
        steps.forEach((step, index) => {
            step.style.display = index === 0 ? 'block' : 'none';
        });

        // Reset progress bar
        const progressFill = form.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = '25%';
        }

        // Reset step indicators
        const stepIndicators = form.querySelectorAll('.progress-step');
        stepIndicators.forEach((indicator, index) => {
            indicator.className = index === 0 ? 'progress-step active' : 'progress-step';
        });
    }
}

// Enhanced authentication functions
async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        alert('이메일과 비밀번호를 모두 입력해주세요.');
        return;
    }

    try {
        const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            showNotification('로그인 성공!', 'success');
            hideLoginModal();
            updateAuthUI();

            // Redirect to where they were trying to go
            const redirectUrl = localStorage.getItem('redirectAfterLogin') || 'index.html';
            localStorage.removeItem('redirectAfterLogin');
            window.location.href = redirectUrl;
        } else {
            alert(data.message || '로그인에 실패했습니다.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('로그인 중 오류가 발생했습니다.');
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupPasswordConfirm').value;
    const referralCode = document.getElementById('referralCode').value;

    if (password !== confirmPassword) {
        alert('비밀번호가 일치하지 않습니다.');
        return;
    }

    try {
        const requestData = {
            username,
            email,
            password
        };

        if (referralCode) {
            requestData.referred_by = referralCode;
        }

        const response = await fetch('/api/auth/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('회원가입 완료! 로그인해주세요.', 'success');
            hideSignupModal();
            showLoginModal();
        } else {
            alert(data.message || '회원가입에 실패했습니다.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('회원가입 중 오류가 발생했습니다.');
    }
}

// Update auth UI based on login status
function updateAuthUI() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // Update navigation buttons
    const loginBtns = document.querySelectorAll('.btn-login, .login-btn');
    const registerBtns = document.querySelectorAll('.btn-register, .register-btn');
    const userInfo = document.querySelectorAll('.user-info');
    const logoutBtns = document.querySelectorAll('.logout-btn');

    if (token && user.id) {
        // User is logged in
        loginBtns.forEach(btn => btn.style.display = 'none');
        registerBtns.forEach(btn => btn.style.display = 'none');
        logoutBtns.forEach(btn => btn.style.display = 'inline-block');

        userInfo.forEach(info => {
            info.style.display = 'block';
            info.innerHTML = `
                <span class="user-welcome">환영합니다, ${user.username}님!</span>
                <span class="user-type ${user.user_type}">${user.user_type === 'free' ? '무료' : user.user_type === 'paid' ? '프리미엄' : '관리자'}</span>
                ${user.user_type === 'free' ? `<span class="access-count">${user.free_access_count}/3</span>` : ''}
            `;
        });

        // Update premium access indicators
        const premiumButtons = document.querySelectorAll('.premium-feature');
        premiumButtons.forEach(btn => {
            if (user.user_type === 'paid' || user.user_type === 'admin') {
                btn.classList.remove('locked');
                btn.removeAttribute('disabled');
            } else {
                btn.classList.add('locked');
                if (user.free_access_count >= 3) {
                    btn.setAttribute('disabled', 'true');
                }
            }
        });

    } else {
        // User is not logged in
        loginBtns.forEach(btn => btn.style.display = 'inline-block');
        registerBtns.forEach(btn => btn.style.display = 'inline-block');
        logoutBtns.forEach(btn => btn.style.display = 'none');
        userInfo.forEach(info => info.style.display = 'none');
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // Add to page
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    container.appendChild(notification);

    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);

    return notification;
}

// Logout function
function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('freeAccessCount');
    updateAuthUI();
    window.location.href = 'index.html';
}

function showPredictionSuccess(prediction) {
    const message = `
        ✅ 예측이 성공적으로 저장되었습니다!
        
        📊 ${prediction.stockName}
        💰 현재가: $${prediction.currentPrice}
        🎯 예측가: $${prediction.predictedPrice}
        📈 변화율: ${prediction.changePercent > 0 ? '+' : ''}${prediction.changePercent}%
        📅 목표일: ${prediction.targetDate}
        
        ${prediction.sharePublicly ? '🌐 공개 예측으로 저장되었습니다.' : '🔒 비공개 예측으로 저장되었습니다.'}
    `;

    alert(message);
}

function clearPredictionForm() {
    document.getElementById('stockSelect').value = '';
    document.getElementById('currentPrice').value = '';
    document.getElementById('predictedPrice').value = '';
    document.getElementById('targetDate').value = '';
    document.getElementById('duration').value = '1week';
    const sharePublicly = document.getElementById('isPublic');
    if (sharePublicly) sharePublicly.checked = true;
}

// Start prediction function (for the main CTA button)
function startPrediction() {
    console.log('Start prediction clicked');
    scrollToSection('prediction');
}

// Show login modal function (referenced in HTML)
function showLoginModal() {
    alert('로그인 기능은 곧 구현될 예정입니다!');
}

// Load and display saved predictions
function loadMyPredictions() {
    const predictions = JSON.parse(localStorage.getItem('stockPredictions') || '[]');

    // Update statistics
    updatePredictionStats(predictions);

    // Display predictions list
    displayPredictionsList(predictions);
}

function updatePredictionStats(predictions) {
    const totalElement = document.getElementById('totalPredictions');
    const publicElement = document.getElementById('publicPredictions');
    const avgReturnElement = document.getElementById('avgReturn');

    if (!totalElement || !publicElement || !avgReturnElement) return;

    const total = predictions.length;
    const publicCount = predictions.filter(p => p.sharePublicly).length;

    // Calculate average expected return
    let avgReturn = 0;
    if (total > 0) {
        const totalReturn = predictions.reduce((sum, p) => {
            const currentPrice = parseFloat(p.currentPrice);
            const predictedPrice = parseFloat(p.predictedPrice);
            const returnPercent = ((predictedPrice - currentPrice) / currentPrice) * 100;
            return sum + returnPercent;
        }, 0);
        avgReturn = totalReturn / total;
    }

    totalElement.textContent = total;
    publicElement.textContent = publicCount;
    avgReturnElement.textContent = avgReturn.toFixed(1) + '%';
}

function displayPredictionsList(predictions) {
    const listElement = document.getElementById('predictionsList');
    const noDataElement = document.getElementById('noPredictions');

    if (!listElement || !noDataElement) return;

    if (predictions.length === 0) {
        listElement.style.display = 'none';
        noDataElement.style.display = 'block';
        return;
    }

    listElement.style.display = 'block';
    noDataElement.style.display = 'none';

    // Sort predictions by date (newest first)
    const sortedPredictions = [...predictions].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    listElement.innerHTML = sortedPredictions.map(prediction => {
        const currentPrice = parseFloat(prediction.currentPrice);
        const predictedPrice = parseFloat(prediction.predictedPrice);
        const changePercent = ((predictedPrice - currentPrice) / currentPrice) * 100;
        const changeClass = changePercent >= 0 ? 'positive' : 'negative';
        const changeSymbol = changePercent >= 0 ? '+' : '';

        const createdDate = new Date(prediction.timestamp).toLocaleDateString('ko-KR');
        const targetDate = new Date(prediction.targetDate).toLocaleDateString('ko-KR');

        return `
            <div class="prediction-card">
                <div class="prediction-header">
                    <div class="prediction-stock">${prediction.stockName}</div>
                    <div class="prediction-date">${createdDate}</div>
                </div>
                
                <div class="prediction-details">
                    <div class="prediction-detail">
                        <div class="prediction-detail-label">현재 가격</div>
                        <div class="prediction-detail-value">$${currentPrice.toFixed(2)}</div>
                    </div>
                    <div class="prediction-detail">
                        <div class="prediction-detail-label">예측 가격</div>
                        <div class="prediction-detail-value">$${predictedPrice.toFixed(2)}</div>
                    </div>
                    <div class="prediction-detail">
                        <div class="prediction-detail-label">목표 날짜</div>
                        <div class="prediction-detail-value">${targetDate}</div>
                    </div>
                    <div class="prediction-detail">
                        <div class="prediction-detail-label">예상 수익률</div>
                        <div class="prediction-detail-value prediction-change ${changeClass}">
                            ${changeSymbol}${changePercent.toFixed(2)}%
                        </div>
                    </div>
                </div>
                
                <div class="prediction-status">
                    <span class="status-badge ${prediction.sharePublicly ? 'public' : 'private'}">
                        ${prediction.sharePublicly ? '🌐 공개' : '🔒 비공개'}
                    </span>
                    <span class="prediction-detail-label">예측 기간: ${prediction.duration}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Initialize predictions display when page loads
function initMyPredictions() {
    // Load predictions when the page loads
    if (document.getElementById('predictionsList')) {
        loadMyPredictions();
    }
}

// Update the existing submitPrediction function to refresh the predictions display
function refreshPredictionsDisplay() {
    // Refresh the predictions display if we're on that section
    if (document.getElementById('predictionsList')) {
        loadMyPredictions();
    }
}

// Enhance mini-charts with dual-line functionality for my-predictions page
function enhanceMiniCharts() {
    const miniCharts = document.querySelectorAll('.prediction-chart-mini canvas');

    miniCharts.forEach((canvas, index) => {
        if (canvas.width > 0 && canvas.height > 0) {
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;

            // Clear canvas
            ctx.clearRect(0, 0, width, height);

            // Generate sample data for dual lines
            const actualData = generateMiniChartData(width);
            const predictionData = generateMiniChartData(width, true);

            // Draw actual data line (blue)
            drawMiniChartLine(ctx, actualData, '#2962FF', width, height, false);

            // Draw prediction data line (orange, dashed)
            drawMiniChartLine(ctx, predictionData, '#ff6b35', width, height, true);

            // Add mini legend
            drawMiniChartLegend(ctx, width, height);
        }
    });
}

// Generate data points for mini charts
function generateMiniChartData(width, isPrediction = false) {
    const points = Math.floor(width / 4); // One point every 4 pixels
    const data = [];
    let value = 100 + (Math.random() - 0.5) * 20; // Start around 100

    for (let i = 0; i < points; i++) {
        // Add some randomness but keep it realistic
        const change = (Math.random() - 0.5) * (isPrediction ? 8 : 5); // Predictions more volatile
        value += change;
        value = Math.max(80, Math.min(120, value)); // Keep within reasonable bounds

        data.push({
            x: (i / (points - 1)) * width,
            y: value
        });
    }

    return data;
}

// Draw a line on mini chart canvas
function drawMiniChartLine(ctx, data, color, width, height, isDashed = false) {
    if (data.length < 2) return;

    // Normalize Y values to canvas height with padding
    const padding = 10;
    const minY = Math.min(...data.map(d => d.y));
    const maxY = Math.max(...data.map(d => d.y));
    const range = maxY - minY || 1;

    ctx.strokeStyle = color;
    ctx.lineWidth = isDashed ? 2 : 2;

    if (isDashed) {
        ctx.setLineDash([3, 3]);
    } else {
        ctx.setLineDash([]);
    }

    ctx.beginPath();

    data.forEach((point, index) => {
        const x = point.x;
        const y = padding + ((maxY - point.y) / range) * (height - 2 * padding);

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });

    ctx.stroke();
}

// Draw mini chart legend
function drawMiniChartLegend(ctx, width, height) {
    const legendY = height - 15;
    const legendStartX = 5;

    ctx.font = '8px Arial';
    ctx.textAlign = 'left';

    // Actual data legend
    ctx.strokeStyle = '#2962FF';
    ctx.lineWidth = 1;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(legendStartX, legendY);
    ctx.lineTo(legendStartX + 10, legendY);
    ctx.stroke();

    ctx.fillStyle = '#333';
    ctx.fillText('실제', legendStartX + 12, legendY + 2);

    // Prediction data legend
    const predictionX = legendStartX + 35;
    ctx.strokeStyle = '#ff6b35';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 2]);
    ctx.beginPath();
    ctx.moveTo(predictionX, legendY);
    ctx.lineTo(predictionX + 10, legendY);
    ctx.stroke();

    ctx.fillStyle = '#333';
    ctx.fillText('예측', predictionX + 12, legendY + 2);
}

// Initialize dynamic mini charts for chart cards
function initializeDynamicMiniChart(canvas, symbol, currentPrice, predictedPrice) {
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Generate realistic data based on current and predicted prices
    const actualData = generateRealisticMiniData(width, currentPrice);
    const predictionData = generateRealisticMiniData(width, currentPrice, predictedPrice);

    // Draw actual data line (blue area)
    drawMiniChartArea(ctx, actualData, '#2962FF', width, height, 0.2);

    // Draw prediction data line (orange line, dashed)
    drawMiniChartLine(ctx, predictionData, '#ff6b35', width, height, true);

    // Add symbol label
    ctx.font = 'bold 12px Arial';
    ctx.fillStyle = '#333';
    ctx.textAlign = 'left';
    ctx.fillText(symbol, 10, 20);

    // Add mini indicators
    const changePercent = ((predictedPrice - currentPrice) / currentPrice * 100);
    const changeText = `${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(1)}%`;
    ctx.font = '10px Arial';
    ctx.fillStyle = changePercent >= 0 ? '#26a69a' : '#ef5350';
    ctx.textAlign = 'right';
    ctx.fillText(changeText, width - 10, 20);
}

// Generate realistic mini chart data based on prices
function generateRealisticMiniData(width, basePrice, targetPrice = null) {
    const points = Math.floor(width / 8); // One point every 8 pixels
    const data = [];

    // If targetPrice is provided, create a trend towards it
    const trend = targetPrice ? (targetPrice - basePrice) / points : 0;
    let value = basePrice;

    for (let i = 0; i < points; i++) {
        // Add trend plus some random variation
        const trendAdjustment = trend * i;
        const randomVariation = (Math.random() - 0.5) * (basePrice * 0.02); // ±2% variation

        value = basePrice + trendAdjustment + randomVariation;

        data.push({
            x: (i / (points - 1)) * width,
            y: value
        });
    }

    return data;
}

// Draw area chart for mini charts
function drawMiniChartArea(ctx, data, color, width, height, opacity = 0.3) {
    if (data.length < 2) return;

    // Normalize Y values to canvas height with padding
    const padding = 20;
    const minY = Math.min(...data.map(d => d.y));
    const maxY = Math.max(...data.map(d => d.y));
    const range = maxY - minY || 1;

    // Create gradient
    const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
    const baseColor = color;
    gradient.addColorStop(0, baseColor + Math.floor(opacity * 255).toString(16).padStart(2, '0'));
    gradient.addColorStop(1, baseColor + '00');

    ctx.fillStyle = gradient;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;

    // Draw area
    ctx.beginPath();

    data.forEach((point, index) => {
        const x = point.x;
        const y = padding + ((maxY - point.y) / range) * (height - 2 * padding);

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });

    // Close the area to bottom
    ctx.lineTo(data[data.length - 1].x, height - padding);
    ctx.lineTo(data[0].x, height - padding);
    ctx.closePath();
    ctx.fill();

    // Draw the line on top
    ctx.beginPath();
    data.forEach((point, index) => {
        const x = point.x;
        const y = padding + ((maxY - point.y) / range) * (height - 2 * padding);

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
}
