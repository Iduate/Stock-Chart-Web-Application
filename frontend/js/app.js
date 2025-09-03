// Stock Chart Web Application - Main JavaScript File
// API Base URL Configuration - Auto-detect environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://127.0.0.1:8000/api' 
    : '/api';  // Use relative path for production
console.log('App.js loaded - Production API fix version 1.4 - ' + new Date().getTime());
console.log('API Base URL:', API_BASE_URL);

// Test function to manually call crypto
window.testCrypto = function() {
    console.log('Manual crypto test called');
    loadCryptoData();
};

// Global variables for chart instances
let heroChart = null;
let predictionChart = null;
let currentSeries = null;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking LightweightCharts...');
    
    // Check if LightweightCharts is available
    if (typeof LightweightCharts === 'undefined') {
        console.error('LightweightCharts library not loaded! Please check if the script is included.');
        // Try to load it dynamically
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js';
        script.onload = function() {
            console.log('LightweightCharts loaded dynamically');
            initializeApp();
            initializeCharts();
            loadMarketData();
            startRealTimeUpdates();
        };
        document.head.appendChild(script);
        return;
    }
    
    initializeApp();
    initializeCharts();
    loadMarketData();
    startRealTimeUpdates();
});

// Initialize main application features
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
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Setup navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
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

// Initialize charts
function initializeCharts() {
    console.log('Initializing charts...');
    
    // Initialize hero chart
    const heroChartElement = document.getElementById('heroChart');
    console.log('Hero chart element:', heroChartElement);
    
    if (heroChartElement && typeof LightweightCharts !== 'undefined') {
        console.log('Creating hero chart...');
        console.log('LightweightCharts available:', typeof LightweightCharts);
        console.log('LightweightCharts object:', LightweightCharts);
        
        try {
            // Ensure the element has proper dimensions
            if (heroChartElement.clientWidth === 0) {
                heroChartElement.style.width = '100%';
                heroChartElement.style.height = window.innerWidth <= 480 ? '200px' : (window.innerWidth <= 768 ? '250px' : '400px');
            }
            
            const chartWidth = heroChartElement.clientWidth || (window.innerWidth <= 768 ? window.innerWidth - 40 : 800);
            const chartHeight = window.innerWidth <= 480 ? 200 : (window.innerWidth <= 768 ? 250 : 400);
            
            window.heroChart = LightweightCharts.createChart(heroChartElement, getMobileChartConfig(chartWidth, chartHeight));
            
            console.log('Hero chart created:', window.heroChart);
            
            // Verify the chart object has the required methods
            if (typeof window.heroChart.addLineSeries === 'function') {
                loadStockChart('AAPL');
            } else {
                console.error('Chart created but addLineSeries method is missing');
                // Try alternative approach
                setTimeout(() => {
                    loadStockChart('AAPL');
                }, 100);
            }
        } catch (error) {
            console.error('Failed to create hero chart:', error);
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

// Load stock chart with multiple API fallback
async function loadStockChart(symbol) {
    console.log(`Loading stock chart for ${symbol}...`);
    
    // Verify chart object exists and has required methods
    if (!window.heroChart) {
        console.error('Hero chart not initialized');
        return;
    }
    
    const apiSources = [
        { name: 'Primary Historical', endpoint: `historical/${symbol}/` },
        { name: 'Tiingo', endpoint: `tiingo/${symbol}/` },
        { name: 'Marketstack', endpoint: `marketstack/${symbol}/` },
        { name: 'Enhanced', endpoint: `enhanced/${symbol}/` }
    ];
    
    let data = null;
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
                const heroChartElement = document.getElementById('heroChart');
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
            
            const lineSeries = window.heroChart.addLineSeries({
                color: '#ffd700',
                lineWidth: 3,
                priceFormat: {
                    type: 'price',
                    precision: 2,
                    minMove: 0.01,
                },
            });
            
            window.currentSeries = lineSeries;
            
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
            
            lineSeries.setData(formattedData);
            console.log('Chart data set successfully');
            
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
    stockSelect.addEventListener('change', async function() {
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
        { name: 'Alpha Vantage', endpoint: 'quote' },
        { name: 'Tiingo', endpoint: 'tiingo' },
        { name: 'Marketstack', endpoint: 'marketstack' }
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
window.addEventListener('load', function() {
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
    modal.addEventListener('click', function(e) {
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
    
    modal.addEventListener('click', function(e) {
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
    // TODO: Implement Google OAuth
    alert('Google 로그인 기능은 현재 개발 중입니다.');
}

function loginWithApple() {
    // TODO: Implement Apple OAuth  
    alert('Apple 로그인 기능은 현재 개발 중입니다.');
}

function registerWithGoogle() {
    // TODO: Implement Google OAuth for registration
    alert('Google 회원가입 기능은 현재 개발 중입니다.');
}

function registerWithApple() {
    // TODO: Implement Apple OAuth for registration
    alert('Apple 회원가입 기능은 현재 개발 중입니다.');
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
        // Resize hero chart
        const heroChartElement = document.getElementById('heroChart');
        if (heroChartElement && window.heroChart) {
            const newWidth = heroChartElement.clientWidth || (window.innerWidth <= 768 ? window.innerWidth - 40 : 800);
            const newHeight = window.innerWidth <= 480 ? 200 : (window.innerWidth <= 768 ? 250 : 400);
            
            try {
                window.heroChart.applyOptions({
                    width: newWidth,
                    height: newHeight
                });
                
                // Update chart element height
                heroChartElement.style.height = newHeight + 'px';
            } catch (error) {
                console.error('Error resizing hero chart:', error);
            }
        }
        
        // Resize prediction chart
        const predictionChartElement = document.getElementById('predictionChart');
        if (predictionChartElement && window.predictionChart) {
            const newWidth = predictionChartElement.clientWidth || (window.innerWidth <= 768 ? window.innerWidth - 40 : 600);
            const newHeight = window.innerWidth <= 480 ? 200 : (window.innerWidth <= 768 ? 250 : 300);
            
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
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(resizeCharts, 250);
    });
    
    // Add orientation change event listener for mobile devices
    window.addEventListener('orientationchange', function() {
        setTimeout(resizeCharts, 500); // Delay to allow orientation change to complete
    });
}

// Initialize mobile-optimized chart configuration
function getMobileChartConfig(width, height) {
    const isMobile = window.innerWidth <= 768;
    
    return {
        width: width,
        height: height,
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#333',
            fontSize: isMobile ? 10 : 12,
        },
        grid: {
            vertLines: {
                color: 'rgba(197, 203, 206, 0.5)',
                visible: !isMobile || window.innerWidth > 480, // Hide grid on very small screens
            },
            horzLines: {
                color: 'rgba(197, 203, 206, 0.5)',
                visible: !isMobile || window.innerWidth > 480,
            },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
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
function submitPrediction() {
    console.log('Submit prediction clicked');
    
    // Get form values
    const stockSelect = document.getElementById('stockSelect');
    const currentPrice = document.getElementById('currentPrice');
    const predictedPrice = document.getElementById('predictedPrice');
    const targetDate = document.getElementById('targetDate');
    const duration = document.getElementById('duration');
    const sharePublicly = document.getElementById('isPublic');
    
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
    
    // Create prediction object
    const prediction = {
        symbol: stockSelect.value,
        stockName: stockSelect.options[stockSelect.selectedIndex].text,
        currentPrice: parseFloat(currentPrice.value),
        predictedPrice: parseFloat(predictedPrice.value),
        targetDate: targetDate.value,
        forecastPeriod: duration.value,
        sharePublicly: sharePublicly ? sharePublicly.checked : false,
        createdAt: new Date().toISOString(),
        userId: 'anonymous', // For now, since we don't have user auth
        accuracy: null, // Will be calculated later
        status: 'pending'
    };
    
    // Calculate prediction change percentage
    const changePercent = ((prediction.predictedPrice - prediction.currentPrice) / prediction.currentPrice * 100).toFixed(2);
    prediction.changePercent = parseFloat(changePercent);
    
    console.log('Prediction data:', prediction);
    
    // Save to localStorage (since we don't have backend integration yet)
    let predictions = JSON.parse(localStorage.getItem('stockPredictions') || '[]');
    prediction.id = Date.now(); // Simple ID generation
    predictions.push(prediction);
    localStorage.setItem('stockPredictions', JSON.stringify(predictions));
    
    // Show success message
    showPredictionSuccess(prediction);
    
    // Clear form
    clearPredictionForm();
    
    // Refresh predictions display
    refreshPredictionsDisplay();
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
