// TradingView-inspired Theme & Chart Enhancements
document.addEventListener('DOMContentLoaded', function () {
    // Theme toggle functionality
    initThemeToggle();

    // Initialize TradingView-styled charts
    enhanceCharts();

    // Make the page elements fade in
    animatePageElements();
});

// Initialize theme toggle
function initThemeToggle() {
    // Create theme toggle button
    const themeToggle = document.createElement('button');
    themeToggle.classList.add('theme-toggle');
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.setAttribute('aria-label', 'Toggle dark/light mode');
    document.body.appendChild(themeToggle);

    // Check for saved theme preference or respect OS preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'light' || (!savedTheme && !prefersDarkScheme)) {
        document.body.classList.add('light-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }

    // Toggle theme on button click
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');

        if (document.body.classList.contains('light-theme')) {
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }

        // Refresh charts to apply theme
        enhanceCharts();

        // Add transition effect
        document.body.classList.add('dark-mode-transition');
        setTimeout(() => {
            document.body.classList.remove('dark-mode-transition');
        }, 300);
    });
}

// Enhance charts with TradingView styling
function enhanceCharts() {
    // Check if hero chart exists and is a proper chart instance
    if (window.heroChart && typeof window.heroChart.applyOptions === 'function') {
        applyTradingViewChartStyle(window.heroChart);
    }

    // Check if prediction chart exists and is a proper chart instance
    if (window.predictionChart && typeof window.predictionChart.applyOptions === 'function') {
        applyTradingViewChartStyle(window.predictionChart);
    }

    // Apply style to all chart instances
    if (window.chartInstances && Array.isArray(window.chartInstances)) {
        window.chartInstances.forEach(chart => {
            if (chart && typeof chart.applyOptions === 'function') {
                applyTradingViewChartStyle(chart);
            }
        });
    }

    // Create featured chart (large main chart after hero section)
    createFeaturedChart();
}

// Apply TradingView styling to charts
function applyTradingViewChartStyle(chart) {
    if (!chart) return;

    // Check if the chart has the applyOptions method
    if (typeof chart.applyOptions !== 'function') {
        console.warn('Chart object does not have applyOptions method:', chart);
        return;
    }

    const isDarkTheme = !document.body.classList.contains('light-theme');

    try {
        // TradingView-inspired chart options
        chart.applyOptions({
            layout: {
                background: {
                    type: 'solid',
                    color: isDarkTheme ? '#131722' : '#ffffff'
                },
                textColor: isDarkTheme ? '#d1d4dc' : '#131722',
                fontSize: 12,
                fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            },
            grid: {
                vertLines: {
                    color: isDarkTheme ? '#2a2e39' : '#f0f3fa',
                },
                horzLines: {
                    color: isDarkTheme ? '#2a2e39' : '#f0f3fa',
                },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
                vertLine: {
                    width: 1,
                    color: isDarkTheme ? '#758696' : '#9db2bd',
                    style: LightweightCharts.LineStyle.Dashed,
                },
                horzLine: {
                    width: 1,
                    color: isDarkTheme ? '#758696' : '#9db2bd',
                    style: LightweightCharts.LineStyle.Dashed,
                },
            },
            timeScale: {
                borderColor: isDarkTheme ? '#2a2e39' : '#e0e3eb',
                timeVisible: true,
                secondsVisible: false,
            },
            rightPriceScale: {
                borderColor: isDarkTheme ? '#2a2e39' : '#e0e3eb',
            },
        });

        // Update series colors if they exist
        const series = chart.series ? chart.series : chart.getSeries ? chart.getSeries() : null;
        if (series && Array.isArray(series)) {
            series.forEach(s => updateSeriesStyle(s, isDarkTheme));
        } else if (series) {
            updateSeriesStyle(series, isDarkTheme);
        }
    } catch (error) {
        console.error('Error applying chart options:', error);
    }
}

// Update individual series styling
function updateSeriesStyle(series, isDarkTheme) {
    if (!series) return;

    if (series.applyOptions) {
        // Check the series type and apply appropriate styling
        if (series.seriesType === 'candlestick' || series.options?.type === 'candlestick') {
            series.applyOptions({
                upColor: '#26a69a',
                downColor: '#ef5350',
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
                borderVisible: false,
            });
        } else if (series.seriesType === 'line' || series.options?.type === 'line') {
            series.applyOptions({
                color: '#2962ff',
                lineWidth: 2,
                crosshairMarkerVisible: true,
                crosshairMarkerRadius: 4,
            });
        } else if (series.seriesType === 'area' || series.options?.type === 'area') {
            series.applyOptions({
                topColor: isDarkTheme ? 'rgba(41, 98, 255, 0.28)' : 'rgba(41, 98, 255, 0.2)',
                bottomColor: isDarkTheme ? 'rgba(41, 98, 255, 0.05)' : 'rgba(41, 98, 255, 0.04)',
                lineColor: '#2962ff',
                lineWidth: 2,
            });
        } else if (series.seriesType === 'bar' || series.options?.type === 'bar') {
            series.applyOptions({
                upColor: '#26a69a',
                downColor: '#ef5350',
                thinBars: false,
            });
        } else if (series.seriesType === 'histogram' || series.options?.type === 'histogram') {
            series.applyOptions({
                color: '#26a69a',
                base: 0,
            });
        }
    }
}

// Animate page elements on load
function animatePageElements() {
    const elements = document.querySelectorAll('.hero-content > *, .feature-card, .market-card, .section-header, .chart-container, .featured-chart-container, .chart-controls, .event-card, .plan-card');

    let delay = 0;
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.animation = `fadeIn 0.5s ease-out ${delay}s forwards`;
        delay += 0.1;
    });
}

// Create animated price tickers
function createMarketTickers() {
    // This would be populated with real market data from your API
    const marketData = [
        { symbol: 'BTC', name: 'Bitcoin', price: 112380, change: 2.5, color: '#f7931a' },
        { symbol: 'ETH', name: 'Ethereum', price: 4320, change: -1.2, color: '#627eea' },
        { symbol: 'AAPL', name: 'Apple Inc', price: 207.50, change: 0.8, color: '#666666' },
        { symbol: 'MSFT', name: 'Microsoft', price: 415.75, change: 1.5, color: '#00a4ef' },
        { symbol: '005930', name: '삼성전자', price: 72000, change: 2.1, color: '#1428a0' }
    ];

    const tickerContainer = document.createElement('div');
    tickerContainer.className = 'market-ticker';

    const tickerTrack = document.createElement('div');
    tickerTrack.className = 'ticker-track';

    marketData.forEach(item => {
        const tickerItem = document.createElement('div');
        tickerItem.className = 'ticker-item';

        const symbolEl = document.createElement('span');
        symbolEl.className = 'ticker-symbol';
        symbolEl.style.color = item.color;
        symbolEl.textContent = item.symbol;

        const priceEl = document.createElement('span');
        priceEl.className = 'ticker-price';
        priceEl.textContent = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: item.symbol === '005930' ? 'KRW' : 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: item.price < 100 ? 2 : 0
        }).format(item.price);

        const changeEl = document.createElement('span');
        changeEl.className = `ticker-change ${item.change >= 0 ? 'positive' : 'negative'}`;
        changeEl.textContent = `${item.change >= 0 ? '+' : ''}${item.change}%`;

        tickerItem.appendChild(symbolEl);
        tickerItem.appendChild(priceEl);
        tickerItem.appendChild(changeEl);
        tickerTrack.appendChild(tickerItem);
    });

    tickerContainer.appendChild(tickerTrack);

    // Add to the page just below the navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.parentNode.insertBefore(tickerContainer, navbar.nextSibling);
    }
}

// Create a hero chart if it doesn't exist
function createHeroChartIfNeeded() {
    if (!window.heroChart && document.getElementById('heroChart')) {
        initializeHeroChart();
    }
}

// Initialize the hero chart with a more professional design
function initializeHeroChart() {
    const chartElement = document.getElementById('heroChart');
    if (!chartElement) return;

    const isDarkTheme = !document.body.classList.contains('light-theme');

    // Create chart with TradingView styling
    const chart = LightweightCharts.createChart(chartElement, {
        width: chartElement.clientWidth,
        height: chartElement.clientHeight,
        layout: {
            background: {
                type: 'solid',
                color: isDarkTheme ? '#131722' : '#ffffff'
            },
            textColor: isDarkTheme ? '#d1d4dc' : '#131722',
            fontSize: 12,
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        },
        grid: {
            vertLines: {
                color: isDarkTheme ? '#2a2e39' : '#f0f3fa',
            },
            horzLines: {
                color: isDarkTheme ? '#2a2e39' : '#f0f3fa',
            },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                width: 1,
                color: isDarkTheme ? '#758696' : '#9db2bd',
                style: LightweightCharts.LineStyle.Dashed,
            },
            horzLine: {
                width: 1,
                color: isDarkTheme ? '#758696' : '#9db2bd',
                style: LightweightCharts.LineStyle.Dashed,
            },
        },
        timeScale: {
            borderColor: isDarkTheme ? '#2a2e39' : '#e0e3eb',
            timeVisible: true,
            secondsVisible: false,
        },
        rightPriceScale: {
            borderColor: isDarkTheme ? '#2a2e39' : '#e0e3eb',
        },
    });

    // Sample data for an attractive chart
    // This would normally come from your API
    const sampleData = generateSampleChartData();

    // Create area series
    const areaSeries = chart.addAreaSeries({
        topColor: isDarkTheme ? 'rgba(41, 98, 255, 0.28)' : 'rgba(41, 98, 255, 0.2)',
        bottomColor: isDarkTheme ? 'rgba(41, 98, 255, 0.05)' : 'rgba(41, 98, 255, 0.04)',
        lineColor: '#2962ff',
        lineWidth: 2,
    });

    areaSeries.setData(sampleData);

    // Make chart responsive
    window.addEventListener('resize', () => {
        chart.applyOptions({
            width: chartElement.clientWidth,
            height: chartElement.clientHeight,
        });
    });

    // Store chart reference
    window.heroChart = chart;
    chart.series = areaSeries;
}

// Generate sample chart data
function generateSampleChartData() {
    const data = [];
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 3);

    let price = 100;
    const trend = [
        { direction: 1, days: 15 },
        { direction: -1, days: 10 },
        { direction: 1, days: 25 },
        { direction: -1, days: 5 },
        { direction: 1, days: 45 }
    ];

    let currentTrendIndex = 0;
    let daysInCurrentTrend = 0;

    for (let i = 0; i < 90; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);

        // Check if we need to switch trend
        if (daysInCurrentTrend >= trend[currentTrendIndex].days) {
            currentTrendIndex = (currentTrendIndex + 1) % trend.length;
            daysInCurrentTrend = 0;
        }

        // Apply the trend with some randomness
        const trendDirection = trend[currentTrendIndex].direction;
        const changePercent = (Math.random() * 2 - 0.5 + (trendDirection * 0.5)) / 100;
        price = price * (1 + changePercent);

        data.push({
            time: Math.floor(currentDate.getTime() / 1000),
            value: price
        });

        daysInCurrentTrend++;
    }

    return data;
}

// Create the featured large chart with sample data
function createFeaturedChart() {
    const chartElement = document.getElementById('featuredChart');
    if (!chartElement) return;

    // Clear any existing chart
    chartElement.innerHTML = '';

    const isDarkTheme = !document.body.classList.contains('light-theme');

    // Create chart with TradingView styling
    const chart = LightweightCharts.createChart(chartElement, {
        layout: {
            background: { color: isDarkTheme ? '#131722' : '#ffffff' },
            textColor: isDarkTheme ? '#d1d4dc' : '#131722',
        },
        grid: {
            vertLines: { color: isDarkTheme ? '#2a2e39' : '#f0f3fa' },
            horzLines: { color: isDarkTheme ? '#2a2e39' : '#f0f3fa' },
        },
        width: chartElement.clientWidth,
        height: chartElement.clientHeight,
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: isDarkTheme ? '#2a2e39' : '#f0f3fa',
        },
        rightPriceScale: {
            borderColor: isDarkTheme ? '#2a2e39' : '#f0f3fa',
            scaleMargins: {
                top: 0.1,
                bottom: 0.1,
            },
        },
        crosshair: {
            horzLine: {
                color: isDarkTheme ? '#758696' : '#9598a1',
                labelBackgroundColor: isDarkTheme ? '#758696' : '#9598a1',
            },
            vertLine: {
                color: isDarkTheme ? '#758696' : '#9598a1',
                labelBackgroundColor: isDarkTheme ? '#758696' : '#9598a1',
            },
        },
    });

    // Sample data based on the screenshot (a sample stock price data)
    const data = [
        { time: '2022-01-01', value: 155.00 },
        { time: '2022-01-02', value: 154.20 },
        { time: '2022-01-03', value: 156.80 },
        { time: '2022-01-04', value: 158.90 },
        { time: '2022-01-05', value: 157.50 },
        { time: '2022-01-06', value: 159.80 },
        { time: '2022-01-07', value: 161.20 },
        { time: '2022-01-08', value: 162.70 },
        { time: '2022-01-09', value: 162.10 },
        { time: '2022-01-10', value: 160.80 },
        { time: '2022-01-11', value: 159.30 },
        { time: '2022-01-12', value: 161.50 },
        { time: '2022-01-13', value: 164.20 },
        { time: '2022-01-14', value: 166.80 },
        { time: '2022-01-15', value: 165.30 },
        { time: '2022-01-16', value: 167.20 },
        { time: '2022-01-17', value: 165.80 },
        { time: '2022-01-18', value: 163.40 },
        { time: '2022-01-19', value: 161.70 },
        { time: '2022-01-20', value: 159.60 },
        { time: '2022-01-21', value: 157.50 },
        { time: '2022-01-22', value: 158.90 },
        { time: '2022-01-23', value: 160.30 },
        { time: '2022-01-24', value: 162.10 },
        { time: '2022-01-25', value: 164.70 },
        { time: '2022-01-26', value: 163.20 },
        { time: '2022-01-27', value: 161.80 },
        { time: '2022-01-28', value: 162.90 },
        { time: '2022-01-29', value: 164.50 },
        { time: '2022-01-30', value: 165.97 }
    ];

    // Create the line series with TradingView yellow styling from screenshot
    const lineSeries = chart.addLineSeries({
        color: '#f7cb4d',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 5,
        priceLineVisible: true,
        priceLineWidth: 1,
        priceLineColor: '#f7cb4d',
        priceLineStyle: 1,
        lastValueVisible: true,
        priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
        },
    });

    // Set the data
    lineSeries.setData(data);

    // Add price line label at current price
    const lastValue = data[data.length - 1].value;
    lineSeries.createPriceLine({
        price: lastValue,
        color: '#f7cb4d',
        lineWidth: 1,
        lineStyle: 1,
        axisLabelVisible: true,
        title: lastValue.toFixed(2),
    });

    // Store chart instance for theme switching
    window.featuredChart = chart;

    // Make chart responsive
    const resizeObserver = new ResizeObserver(entries => {
        if (entries.length === 0 || entries[0].target !== chartElement) {
            return;
        }

        const newRect = entries[0].contentRect;
        chart.applyOptions({ width: newRect.width, height: newRect.height });
    });

    resizeObserver.observe(chartElement);

    // Set up timeframe buttons
    const timeframeButtons = document.querySelectorAll('.btn-timeframe');
    if (timeframeButtons.length > 0) {
        timeframeButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons
                timeframeButtons.forEach(btn => btn.classList.remove('active'));

                // Add active class to clicked button
                button.classList.add('active');

                // In a real app, you would fetch data for the selected timeframe
                // For now, we'll just simulate a chart update
                chart.timeScale().fitContent();
            });
        });
    }

    return chart;
}

// Update all TradingView-styled elements when page loads
window.addEventListener('load', function () {
    createMarketTickers();
    createHeroChartIfNeeded();
});
