// ê¸€ë¡œë²Œ ë³€ìˆ˜
let currentUser = null;
let currentPage = 1;
let totalPages = 1;
let charts = [];
let selectedStock = null;
let realTimeData = {};
let marketDataCache = {};

// API ê¸°ë³¸ URL - í˜„ìž¬ í˜¸ìŠ¤íŠ¸ì™€ ì¼ì¹˜í•˜ë„ë¡ ì„¤ì •
const API_BASE_URL = window.location.origin + '/api';

// ì¸ê¸° ì£¼ì‹ ì‹¬ë³¼ë“¤
const POPULAR_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'];
const POPULAR_CRYPTOS = ['BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOT', 'MATIC'];

// íŽ˜ì´ì§€ ë¡œë“œì‹œ ì´ˆê¸°í™”
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeCharts();
    loadCharts();
    loadRanking('accuracy');
    loadEvents();
    setupEventListeners();
    loadMarketData(); // ì‹¤ì‹œê°„ ì‹œìž¥ ë°ì´í„° ë¡œë“œ
    startRealTimeUpdates(); // ì‹¤ì‹œê°„ ì—…ë°ì´íŠ¸ ì‹œìž‘
});

// ì‹¤ì‹œê°„ ì‹œìž¥ ë°ì´í„° ë¡œë“œ
async function loadMarketData() {
    try {
        // ì¸ê¸° ì£¼ì‹ ë°ì´í„° ë¡œë“œ
        await loadPopularStocks();
        // ì•”í˜¸í™”í ë°ì´í„° ë¡œë“œ
        await loadPopularCryptos();
        // ì‹œìž¥ ì§€ìˆ˜ ë°ì´í„° ë¡œë“œ
        await loadMarketIndices();
        // ë©”ì¸ ì°¨íŠ¸ì— AAPL ë°ì´í„° ë¡œë“œ
        await loadStockChart('AAPL');
    } catch (error) {
        console.error('ì‹œìž¥ ë°ì´í„° ë¡œë“œ ì˜¤ë¥˜:', error);
    }
}

// ì¸ê¸° ì£¼ì‹ ë°ì´í„° ë¡œë“œ
async function loadPopularStocks() {
    try {
        console.log('Loading popular stocks...');
        const promises = POPULAR_STOCKS.slice(0, 4).map(symbol => 
            fetchStockQuote(symbol)
        );
        const stockData = await Promise.all(promises);
        
        console.log('Stock data loaded:', stockData);
        displayPopularStocks(stockData);
    } catch (error) {
        console.error('ì¸ê¸° ì£¼ì‹ ë°ì´í„° ë¡œë“œ ì˜¤ë¥˜:', error);
    }
}

// ì•”í˜¸í™”í ë°ì´í„° ë¡œë“œ
async function loadPopularCryptos() {
    try {
        console.log('Loading popular cryptos...');
        const promises = POPULAR_CRYPTOS.slice(0, 4).map(symbol => 
            fetchCryptoData(symbol)
        );
        const cryptoData = await Promise.all(promises);
        
        console.log('Crypto data loaded:', cryptoData);
        displayPopularCryptos(cryptoData);
    } catch (error) {
        console.error('ì•”í˜¸í™”í ë°ì´í„° ë¡œë“œ ì˜¤ë¥˜:', error);
    }
}

// ì£¼ì‹ ì‹œì„¸ ê°€ì ¸ì˜¤ê¸°
async function fetchStockQuote(symbol) {
    try {
        const response = await fetch(`${API_BASE_URL}/market-data/quote/${symbol}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return { symbol, ...data };
    } catch (error) {
        console.error(`${symbol} ì£¼ì‹ ë°ì´í„° ì˜¤ë¥˜:`, error);
        return { symbol, error: true };
    }
}

// ì•”í˜¸í™”í ë°ì´í„° ê°€ì ¸ì˜¤ê¸°
async function fetchCryptoData(symbol) {
    try {
        const response = await fetch(`${API_BASE_URL}/market-data/crypto/${symbol}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return { symbol, ...data };
    } catch (error) {
        console.error(`${symbol} ì•”í˜¸í™”í ë°ì´í„° ì˜¤ë¥˜:`, error);
        return { symbol, error: true };
    }
}

// ì£¼ì‹ ížˆìŠ¤í† ë¦¬ì»¬ ë°ì´í„° ê°€ì ¸ì˜¤ê¸°
async function fetchHistoricalData(symbol) {
    try {
        const response = await fetch(`${API_BASE_URL}/market-data/historical/${symbol}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`${symbol} ížˆìŠ¤í† ë¦¬ì»¬ ë°ì´í„° ì˜¤ë¥˜:`, error);
        return null;
    }
}

// ì‹¤ì‹œê°„ ì—…ë°ì´íŠ¸ ì‹œìž‘
function startRealTimeUpdates() {
    // 30ì´ˆë§ˆë‹¤ ë°ì´í„° ì—…ë°ì´íŠ¸
    setInterval(() => {
        loadMarketData();
    }, 30000);
}

// ì•± ì´ˆê¸°í™”
function initializeApp() {
    // ë¡œê·¸ì¸ ìƒíƒœ í™•ì¸
    const token = localStorage.getItem('accessToken');
    if (token) {
        validateToken(token);
    }
    
    // ëª¨ë°”ì¼ ë„¤ë¹„ê²Œì´ì…˜ ì„¤ì •
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });
    
    // ë„¤ë¹„ê²Œì´ì…˜ ë§í¬ í´ë¦­ì‹œ ë©”ë‰´ ë‹«ê¸° ë° ì„¹ì…˜ ì´ë™
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            navMenu.classList.remove('active');
            
            // hrefê°€ #ìœ¼ë¡œ ì‹œìž‘í•˜ëŠ” ê²½ìš° ì„¹ì…˜ ì´ë™
            const href = this.getAttribute('href');
            if (href && href.startsWith('#') && href !== '#') {
                e.preventDefault();
                const sectionId = href.substring(1);
                scrollToSection(sectionId);
            }
        });
    });
    
    // ë„¤ë¹„ê²Œì´ì…˜ í™œì„±í™” ìƒíƒœ ì—…ë°ì´íŠ¸
    updateActiveNavigation();
    
    // ìŠ¤í¬ë¡¤ ì´ë²¤íŠ¸ë¡œ ë„¤ë¹„ê²Œì´ì…˜ ìƒíƒœ ì—…ë°ì´íŠ¸
    window.addEventListener('scroll', debounce(updateActiveNavigation, 100));
    
    // API í…ŒìŠ¤íŒ… UI ì¶”ê°€
    addAPITestingUI();
}

// ì°¨íŠ¸ ì´ˆê¸°í™”
function initializeCharts() {
    console.log('Initializing charts...');
    
    // ížˆì–´ë¡œ ì„¹ì…˜ ì°¨íŠ¸
    const heroChartElement = document.getElementById('heroChart');
    console.log('Hero chart element:', heroChartElement);
    
    if (heroChartElement) {
        console.log('Creating hero chart...');
        console.log('LightweightCharts available:', typeof LightweightCharts);
        
        try {
            window.heroChart = LightweightCharts.createChart(heroChartElement, {
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
            
            console.log('Hero chart created:', window.heroChart);
            
            // ì‹¤ì œ ì£¼ì‹ ë°ì´í„°ë¡œ ì°¨íŠ¸ ì—…ë°ì´íŠ¸ (AAPL ê¸°ë³¸)
            loadStockChart('AAPL');
        } catch (error) {
            console.error('Error creating hero chart:', error);
            // ì˜¤ë¥˜ ì‹œ ì°¨íŠ¸ ì»¨í…Œì´ë„ˆì— ë©”ì‹œì§€ í‘œì‹œ
            heroChartElement.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 400px; color: white; font-size: 18px;">ì°¨íŠ¸ ë¡œë”© ì¤‘...</div>';
        }
    } else {
        console.error('Hero chart element not found!');
    }
    
    // ì˜ˆì¸¡ ì°¨íŠ¸
    const predictionChartElement = document.getElementById('predictionChart');
    if (predictionChartElement) {
        console.log('Creating prediction chart...');
        window.predictionChart = LightweightCharts.createChart(predictionChartElement, {
            width: predictionChartElement.clientWidth,
            height: 400,
        });
        console.log('Prediction chart created:', window.predictionChart);
    }
}

// ì‹¤ì œ ì£¼ì‹ ì°¨íŠ¸ ë¡œë“œ (ë‹¤ì¤‘ API ì†ŒìŠ¤ ì§€ì›)
async function loadStockChart(symbol) {
    console.log(`Loading stock chart for ${symbol}...`);
    
    // ë‹¤ì¤‘ API ì†ŒìŠ¤ ì‹œë„
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
            
            // ê¸°ì¡´ ì‹œë¦¬ì¦ˆ ì œê±° (ìžˆë‹¤ë©´)
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
            
            // ë°ì´í„° í¬ë§· ë³€í™˜
            console.log('Raw data before formatting:', data);
            console.log('Data length:', data.length);
            console.log('First data item:', data[0]);
            
            const formattedData = data.map((item, index) => {
                const time = item.date || item.time || item.datetime;
                const value = parseFloat(item.close || item.price || item.value || item.c);
                
                if (index < 3) {
                    console.log(`Item ${index}:`, { original: item, time, value });
                }
                
                return { time, value };
            }).filter(item => item.time && !isNaN(item.value));
            
            console.log('Formatted data for chart:', formattedData.slice(0, 5)); // ì²˜ìŒ 5ê°œ ë°ì´í„°ë§Œ ë¡œê·¸
            console.log('Total formatted data points:', formattedData.length);
            
            lineSeries.setData(formattedData);
            console.log('Chart data set successfully');
            
            // ì°¨íŠ¸ê°€ ì—¬ì „ížˆ ë¹„ì–´ìžˆë‹¤ë©´ ì°¨íŠ¸ ì˜ì—­ í¬ê¸° ì¡°ì •
            if (formattedData.length > 0) {
                window.heroChart.timeScale().fitContent();
                console.log('Chart time scale fitted');
            }
            
            // ì°¨íŠ¸ ì œëª© ì—…ë°ì´íŠ¸
            updateChartTitle(symbol, data[data.length - 1]);
        } else {
            console.error('No data or chart not available');
            if (!data) console.error('Data is null/undefined');
            if (!window.heroChart) console.error('heroChart is not available');
            
            // ë°ì´í„°ê°€ ì—†ì„ ë•Œ ìƒ˜í”Œ ë°ì´í„°ë¡œ í´ë°±
            console.log('Using sample data as no valid data received...');
            if (window.heroChart) {
                const sampleData = generateSampleData();
                const lineSeries = window.heroChart.addLineSeries({
                    color: '#ffd700',
                    lineWidth: 2,
                });
                lineSeries.setData(sampleData);
                console.log('Sample data loaded as fallback for no data');
            }
        }
    } catch (error) {
        console.error('ì£¼ì‹ ì°¨íŠ¸ ë¡œë“œ ì˜¤ë¥˜:', error);
        // ì˜¤ë¥˜ ì‹œ ìƒ˜í”Œ ë°ì´í„° ì‚¬ìš©
        console.log('Using sample data as fallback...');
        if (window.heroChart) {
            const sampleData = generateSampleData();
            const lineSeries = window.heroChart.addLineSeries({
                color: '#ffd700',
                lineWidth: 2,
            });
            lineSeries.setData(sampleData);
            console.log('Sample data loaded as fallback');
        }
    }
}

// ìƒ˜í”Œ ë°ì´í„° ìƒì„±
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

// ì‹œìž¥ ì§€ìˆ˜ ë°ì´í„° ë¡œë“œ
async function loadMarketIndices() {
    try {
        const response = await fetch(`${API_BASE_URL}/market-data/indices/`);
        if (response.ok) {
            const data = await response.json();
            displayMarketIndices(data);
        }
    } catch (error) {
        console.error('ì‹œìž¥ ì§€ìˆ˜ ë¡œë“œ ì˜¤ë¥˜:', error);
    }
}

// ì¸ê¸° ì£¼ì‹ í‘œì‹œ
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
        
        // Try different possible field names from API response
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
    container.innerHTML = html;
    
    // í´ë¦­ ì´ë²¤íŠ¸ ì¶”ê°€
    container.querySelectorAll('.stock-item').forEach(item => {
        item.addEventListener('click', () => {
            const symbol = item.dataset.symbol;
            loadStockChart(symbol);
        });
    });
}

// ì¸ê¸° ì•”í˜¸í™”í í‘œì‹œ
function displayPopularCryptos(cryptoData) {
    const container = document.querySelector('.popular-cryptos');
    if (!container) {
        console.error('Popular cryptos container not found');
        return;
    }
    
    console.log('Crypto data received:', cryptoData);
    
    const html = cryptoData.map(crypto => {
        if (crypto.error) {
            console.error('Crypto error:', crypto.symbol, crypto.error);
            return '';
        }
        
        console.log('Processing crypto:', crypto);
        
        // Try different possible field names from API response
        const price = crypto.price || crypto.current_price || crypto.close || crypto.value || 0;
        const change = crypto.change || crypto.change_percent || crypto.percent_change || 0;
        const isPositive = change >= 0;
        
        return `
            <div class="crypto-item" data-symbol="${crypto.symbol}">
                <div class="crypto-info">
                    <h4>${crypto.symbol}</h4>
                    <p class="crypto-price">$${price.toFixed(2)}</p>
                </div>
                <div class="crypto-change ${isPositive ? 'positive' : 'negative'}">
                    ${isPositive ? '+' : ''}${change.toFixed(2)}%
                </div>
            </div>
        `;
    }).join('');
    
    console.log('Generated crypto HTML:', html);
    container.innerHTML = html;
}

// ì‹œìž¥ ì§€ìˆ˜ í‘œì‹œ
function displayMarketIndices(indicesData) {
    const container = document.querySelector('.market-indices');
    if (!container) {
        console.error('Market indices container not found');
        return;
    }
    
    console.log('Market indices data received:', indicesData);
    
    if (!indicesData) {
        console.error('No indices data provided');
        return;
    }
    
    // Handle if indicesData is wrapped in an object
    const dataArray = indicesData.indices || indicesData;
    
    if (!Array.isArray(dataArray)) {
        console.error('Indices data is not an array:', dataArray);
        return;
    }
    
    const html = dataArray.map(index => {
        console.log('Processing index:', index);
        const isPositive = (index.change || 0) >= 0;
        return `
            <div class="index-item">
                <div class="index-info">
                    <h4>${index.name || index.symbol || 'Unknown'}</h4>
                    <p class="index-value">${(index.value || index.price || 0).toFixed(2)}</p>
                </div>
                <div class="index-change ${isPositive ? 'positive' : 'negative'}">
                    ${isPositive ? '+' : ''}${(index.change || 0).toFixed(2)}%
                </div>
            </div>
        `;
    }).join('');
    
    console.log('Generated indices HTML:', html);
    container.innerHTML = html;
}

// ì°¨íŠ¸ ì œëª© ì—…ë°ì´íŠ¸
function updateChartTitle(symbol, latestData) {
    const titleElement = document.querySelector('.chart-title');
    if (titleElement && latestData) {
        const price = latestData.close || latestData.price || latestData.value;
        titleElement.innerHTML = `
            <h3>${symbol}</h3>
            <p class="current-price">$${price.toFixed(2)}</p>
        `;
    }
}

// ì´ë²¤íŠ¸ ë¦¬ìŠ¤ë„ˆ ì„¤ì •
function setupEventListeners() {
    // ë¡œê·¸ì¸ í¼
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // íšŒì›ê°€ìž… í¼
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // ì˜ˆì¸¡ ê´€ë ¨
    const stockSelect = document.getElementById('stockSelect');
    if (stockSelect) {
        loadStocks();
        stockSelect.addEventListener('change', handleStockChange);
    }
    
    // í•„í„° ë° ê²€ìƒ‰
    const marketFilter = document.getElementById('marketFilter');
    const statusFilter = document.getElementById('statusFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (marketFilter) marketFilter.addEventListener('change', filterCharts);
    if (statusFilter) statusFilter.addEventListener('change', filterCharts);
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterCharts, 300));
    }
    
    // íŽ˜ì´ì§€ë„¤ì´ì…˜
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    
    if (prevPage) prevPage.addEventListener('click', () => changePage(currentPage - 1));
    if (nextPage) nextPage.addEventListener('click', () => changePage(currentPage + 1));
}

// í† í° ê²€ì¦
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
            currentUser = userData.user;
            updateUIForLoggedInUser();
        } else {
            localStorage.removeItem('accessToken');
        }
    } catch (error) {
        console.error('í† í° ê²€ì¦ ì‹¤íŒ¨:', error);
        localStorage.removeItem('accessToken');
    }
}

// ë¡œê·¸ì¸ ì²˜ë¦¬
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
            showNotification('ë¡œê·¸ì¸ì— ì„±ê³µí–ˆìŠµë‹ˆë‹¤!', 'success');
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || 'ë¡œê·¸ì¸ì— ì‹¤íŒ¨í–ˆìŠµë‹ˆë‹¤.', 'error');
        }
    } catch (error) {
        console.error('ë¡œê·¸ì¸ ì˜¤ë¥˜:', error);
        showNotification('ë¡œê·¸ì¸ ì¤‘ ì˜¤ë¥˜ê°€ ë°œìƒí–ˆìŠµë‹ˆë‹¤.', 'error');
    }
}

// íšŒì›ê°€ìž… ì²˜ë¦¬
async function handleSignup(event) {
    event.preventDefault();
    
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const passwordConfirm = document.getElementById('signupPasswordConfirm').value;
    const referralCode = document.getElementById('referralCode').value;
    
    if (password !== passwordConfirm) {
        showNotification('ë¹„ë°€ë²ˆí˜¸ê°€ ì¼ì¹˜í•˜ì§€ ì•ŠìŠµë‹ˆë‹¤.', 'error');
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
            showNotification('íšŒì›ê°€ìž…ì´ ì™„ë£Œë˜ì—ˆìŠµë‹ˆë‹¤! ë¡œê·¸ì¸í•´ì£¼ì„¸ìš”.', 'success');
            showLoginModal();
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || 'íšŒì›ê°€ìž…ì— ì‹¤íŒ¨í–ˆìŠµë‹ˆë‹¤.', 'error');
        }
    } catch (error) {
        console.error('íšŒì›ê°€ìž… ì˜¤ë¥˜:', error);
        showNotification('íšŒì›ê°€ìž… ì¤‘ ì˜¤ë¥˜ê°€ ë°œìƒí–ˆìŠµë‹ˆë‹¤.', 'error');
    }
}

// Google ë¡œê·¸ì¸
function loginWithGoogle() {
    // Google OAuth êµ¬í˜„
    showNotification('Google ë¡œê·¸ì¸ ê¸°ëŠ¥ì„ ì¤€ë¹„ì¤‘ìž…ë‹ˆë‹¤.', 'info');
}

// Apple ë¡œê·¸ì¸
function loginWithApple() {
    // Apple OAuth êµ¬í˜„
    showNotification('Apple ë¡œê·¸ì¸ ê¸°ëŠ¥ì„ ì¤€ë¹„ì¤‘ìž…ë‹ˆë‹¤.', 'info');
}

// ë¡œê·¸ì¸ëœ ì‚¬ìš©ìž UI ì—…ë°ì´íŠ¸
function updateUIForLoggedInUser() {
    const loginBtn = document.querySelector('.login-btn');
    if (loginBtn && currentUser) {
        loginBtn.textContent = `${currentUser.username}ë‹˜`;
        loginBtn.onclick = showUserMenu;
        loginBtn.style.cursor = 'pointer';
    }
}

// ì‚¬ìš©ìž ë©”ë‰´ í‘œì‹œ
function showUserMenu() {
    // ê¸°ì¡´ ë©”ë‰´ê°€ ìžˆìœ¼ë©´ ì œê±°
    const existingMenu = document.querySelector('.user-menu');
    if (existingMenu) {
        existingMenu.remove();
        return;
    }
    
    // ì‚¬ìš©ìž ë©”ë‰´ ìƒì„±
    const userMenu = document.createElement('div');
    userMenu.className = 'user-menu';
    userMenu.innerHTML = `
        <div class="user-menu-header">
            <div class="user-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="user-info">
                <div class="user-name">${currentUser.username}</div>
                <div class="user-email">${currentUser.email}</div>
            </div>
        </div>
        <div class="user-menu-items">
            <a href="#" onclick="goToMyProfile()" class="menu-item">
                <i class="fas fa-user-circle"></i> ë‚´ í”„ë¡œí•„
            </a>
            <a href="#" onclick="goToMyPredictions()" class="menu-item">
                <i class="fas fa-chart-line"></i> ë‚´ ì˜ˆì¸¡
            </a>
            <a href="#" onclick="goToMyRanking()" class="menu-item">
                <i class="fas fa-trophy"></i> ë‚´ ëž­í‚¹
            </a>
            <a href="#" onclick="goToSubscription()" class="menu-item">
                <i class="fas fa-crown"></i> êµ¬ë… ê´€ë¦¬
            </a>
            <a href="#" onclick="goToSettings()" class="menu-item">
                <i class="fas fa-cog"></i> ì„¤ì •
            </a>
            <hr class="menu-divider">
            <a href="#" onclick="logout()" class="menu-item logout">
                <i class="fas fa-sign-out-alt"></i> ë¡œê·¸ì•„ì›ƒ
            </a>
        </div>
    `;
    
    // ë©”ë‰´ ìŠ¤íƒ€ì¼ ì„¤ì •
    userMenu.style.cssText = `
        position: absolute;
        top: 100%;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        width: 280px;
        z-index: 1000;
        overflow: hidden;
    `;
    
    // ë¡œê·¸ì¸ ë²„íŠ¼ ë¶€ëª¨ì— ìƒëŒ€ ìœ„ì¹˜ ì„¤ì •
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.parentElement.style.position = 'relative';
    loginBtn.parentElement.appendChild(userMenu);
    
    // ì™¸ë¶€ í´ë¦­ì‹œ ë©”ë‰´ ë‹«ê¸°
    setTimeout(() => {
        document.addEventListener('click', closeUserMenuOnOutsideClick);
    }, 100);
}

// ì™¸ë¶€ í´ë¦­ì‹œ ì‚¬ìš©ìž ë©”ë‰´ ë‹«ê¸°
function closeUserMenuOnOutsideClick(event) {
    const userMenu = document.querySelector('.user-menu');
    const loginBtn = document.querySelector('.login-btn');
    
    if (userMenu && !userMenu.contains(event.target) && !loginBtn.contains(event.target)) {
        userMenu.remove();
        document.removeEventListener('click', closeUserMenuOnOutsideClick);
    }
}

// ì¢…ëª© ëª©ë¡ ë¡œë“œ
async function loadStocks() {
    try {
        const response = await fetch(`${API_BASE_URL}/market/stocks/`);
        if (response.ok) {
            const stocks = await response.json();
            const stockSelect = document.getElementById('stockSelect');
            
            stockSelect.innerHTML = '<option value="">ì¢…ëª©ì„ ì„ íƒí•˜ì„¸ìš”</option>';
            
            // ìž„ì‹œ ë°ì´í„° (ì‹¤ì œ APIê°€ ì—†ëŠ” ê²½ìš°)
            const sampleStocks = [
                { id: 1, name: 'ì‚¼ì„±ì „ìž', symbol: '005930', current_price: 73500 },
                { id: 2, name: 'SKí•˜ì´ë‹‰ìŠ¤', symbol: '000660', current_price: 142000 },
                { id: 3, name: 'LGì—ë„ˆì§€ì†”ë£¨ì…˜', symbol: '373220', current_price: 415000 },
                { id: 4, name: 'NAVER', symbol: '035420', current_price: 195000 },
                { id: 5, name: 'ì¹´ì¹´ì˜¤', symbol: '035720', current_price: 58000 },
                { id: 6, name: 'Apple Inc.', symbol: 'AAPL', current_price: 175.25 },
                { id: 7, name: 'Microsoft Corp.', symbol: 'MSFT', current_price: 338.12 },
                { id: 8, name: 'Tesla Inc.', symbol: 'TSLA', current_price: 248.50 },
                { id: 9, name: 'Bitcoin', symbol: 'BTC-USD', current_price: 43250.75 },
                { id: 10, name: 'Ethereum', symbol: 'ETH-USD', current_price: 2563.40 }
            ];
            
            const stocksToUse = stocks.length > 0 ? stocks : sampleStocks;
            
            stocksToUse.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.id;
                option.textContent = `${stock.name} (${stock.symbol})`;
                option.dataset.currentPrice = stock.current_price || 0;
                stockSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('ì¢…ëª© ë¡œë“œ ì˜¤ë¥˜:', error);
        // ì—ëŸ¬ ë°œìƒì‹œ ìƒ˜í”Œ ë°ì´í„° ì‚¬ìš©
        const stockSelect = document.getElementById('stockSelect');
        const sampleStocks = [
            { id: 1, name: 'ì‚¼ì„±ì „ìž', symbol: '005930', current_price: 73500 },
            { id: 2, name: 'SKí•˜ì´ë‹‰ìŠ¤', symbol: '000660', current_price: 142000 },
            { id: 3, name: 'Apple Inc.', symbol: 'AAPL', current_price: 175.25 },
            { id: 4, name: 'Bitcoin', symbol: 'BTC-USD', current_price: 43250.75 }
        ];
        
        stockSelect.innerHTML = '<option value="">ì¢…ëª©ì„ ì„ íƒí•˜ì„¸ìš”</option>';
        sampleStocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.id;
            option.textContent = `${stock.name} (${stock.symbol})`;
            option.dataset.currentPrice = stock.current_price;
            stockSelect.appendChild(option);
        });
    }
}

// ì¢…ëª© ë³€ê²½ ì²˜ë¦¬
function handleStockChange(event) {
    const selectedOption = event.target.selectedOptions[0];
    if (selectedOption && selectedOption.value) {
        selectedStock = {
            id: selectedOption.value,
            name: selectedOption.textContent,
            currentPrice: parseFloat(selectedOption.dataset.currentPrice) || 0
        };
        
        // í˜„ìž¬ ê°€ê²© ìž…ë ¥ í•„ë“œ ì—…ë°ì´íŠ¸
        const currentPriceInput = document.getElementById('currentPrice');
        if (currentPriceInput) {
            currentPriceInput.value = selectedStock.currentPrice.toLocaleString();
        }
        
        // ì˜ˆì¸¡ ì°¨íŠ¸ ì—…ë°ì´íŠ¸
        updatePredictionChart();
    } else {
        selectedStock = null;
        const currentPriceInput = document.getElementById('currentPrice');
        if (currentPriceInput) {
            currentPriceInput.value = '';
        }
    }
}

// ì˜ˆì¸¡ ì°¨íŠ¸ ì—…ë°ì´íŠ¸
function updatePredictionChart() {
    const predictionChartElement = document.getElementById('predictionChart');
    if (!predictionChartElement || !selectedStock) return;
    
    // ê¸°ì¡´ ì°¨íŠ¸ ì œê±°
    predictionChartElement.innerHTML = '';
    
    const chart = LightweightCharts.createChart(predictionChartElement, {
        width: predictionChartElement.clientWidth,
        height: 400,
        layout: {
            background: { color: '#ffffff' },
            textColor: '#333',
        },
        grid: {
            vertLines: { color: '#f0f0f0' },
            horzLines: { color: '#f0f0f0' },
        },
        rightPriceScale: {
            borderColor: '#ccc',
        },
        timeScale: {
            borderColor: '#ccc',
        },
    });
    
    // í˜„ìž¬ ê°€ê²©ì„ ê¸°ì¤€ìœ¼ë¡œ ìƒ˜í”Œ ë°ì´í„° ìƒì„±
    const historicalData = generateHistoricalData(selectedStock.currentPrice);
    const lineSeries = chart.addLineSeries({
        color: '#007bff',
        lineWidth: 2,
    });
    lineSeries.setData(historicalData);
    
    // ì°¨íŠ¸ ë°˜ì‘í˜• ì²˜ë¦¬
    window.addEventListener('resize', () => {
        chart.applyOptions({ width: predictionChartElement.clientWidth });
    });
}

// ê³¼ê±° ë°ì´í„° ìƒì„±
function generateHistoricalData(currentPrice) {
    const data = [];
    const days = 30;
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    let price = currentPrice * 0.9; // 30ì¼ ì „ ê°€ê²©ì„ í˜„ìž¬ê°€ì˜ 90%ë¡œ ì„¤ì •
    
    for (let i = 0; i < days; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        
        // ê°€ê²© ë³€ë™ (ëžœë¤)
        price += (Math.random() - 0.5) * (currentPrice * 0.05);
        price = Math.max(price, currentPrice * 0.5); // ìµœì†Œê°’ ì œí•œ
        
        data.push({
            time: date.toISOString().split('T')[0],
            value: Math.round(price * 100) / 100
        });
    }
    
    // ë§ˆì§€ë§‰ ë°ì´í„°ë¥¼ í˜„ìž¬ ê°€ê²©ìœ¼ë¡œ ì„¤ì •
    if (data.length > 0) {
        data[data.length - 1].value = currentPrice;
    }
    
    return data;
}

// ì˜ˆì¸¡ ì œì¶œ
async function submitPrediction() {
    if (!currentUser) {
        showNotification('ë¡œê·¸ì¸ì´ í•„ìš”í•©ë‹ˆë‹¤.', 'warning');
        showLoginModal();
        return;
    }
    
    if (!selectedStock) {
        showNotification('ì¢…ëª©ì„ ì„ íƒí•´ì£¼ì„¸ìš”.', 'warning');
        return;
    }
    
    const predictedPrice = document.getElementById('predictedPrice').value;
    const targetDate = document.getElementById('targetDate').value;
    const duration = document.getElementById('duration').value;
    const isPublic = document.getElementById('isPublic').checked;
    
    if (!predictedPrice || !targetDate) {
        showNotification('ì˜ˆì¸¡ ê°€ê²©ê³¼ ëª©í‘œ ë‚ ì§œë¥¼ ìž…ë ¥í•´ì£¼ì„¸ìš”.', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/charts/predictions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
            body: JSON.stringify({
                stock_id: selectedStock.id,
                predicted_price: parseFloat(predictedPrice),
                target_date: targetDate,
                duration: parseInt(duration),
                is_public: isPublic
            })
        });
        
        if (response.ok) {
            showNotification('ì˜ˆì¸¡ì´ ì„±ê³µì ìœ¼ë¡œ ì €ìž¥ë˜ì—ˆìŠµë‹ˆë‹¤!', 'success');
            // í¼ ì´ˆê¸°í™”
            document.getElementById('predictedPrice').value = '';
            document.getElementById('targetDate').value = '';
            document.getElementById('duration').value = '7';
            // ì°¨íŠ¸ ë³´ë“œë¡œ ì´ë™
            scrollToSection('charts');
            loadCharts();
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || 'ì˜ˆì¸¡ ì €ìž¥ì— ì‹¤íŒ¨í–ˆìŠµë‹ˆë‹¤.', 'error');
        }
    } catch (error) {
        console.error('ì˜ˆì¸¡ ì œì¶œ ì˜¤ë¥˜:', error);
        showNotification('ì˜ˆì¸¡ ì œì¶œ ì¤‘ ì˜¤ë¥˜ê°€ ë°œìƒí–ˆìŠµë‹ˆë‹¤.', 'error');
    }
}

// ì°¨íŠ¸ ëª©ë¡ ë¡œë“œ
async function loadCharts() {
    try {
        const response = await fetch(`${API_BASE_URL}/charts/`);
        if (response.ok) {
            const charts = await response.json();
            displayCharts(charts);
        } else {
            // ìƒ˜í”Œ ë°ì´í„° í‘œì‹œ
            displaySampleCharts();
        }
    } catch (error) {
        console.error('ì°¨íŠ¸ ë¡œë“œ ì˜¤ë¥˜:', error);
        displaySampleCharts();
    }
}

// ìƒ˜í”Œ ì°¨íŠ¸ ë°ì´í„° í‘œì‹œ
function displaySampleCharts() {
    const sampleCharts = [
        {
            id: 1,
            user: { username: 'íˆ¬ìžì™•' },
            stock_name: 'ì‚¼ì„±ì „ìž',
            stock_symbol: '005930',
            predicted_price: 75000,
            current_price: 73500,
            target_date: '2025-09-10',
            created_at: '2025-09-01',
            status: 'pending'
        },
        {
            id: 2,
            user: { username: 'ì°¨íŠ¸ë§ˆìŠ¤í„°' },
            stock_name: 'Apple Inc.',
            stock_symbol: 'AAPL',
            predicted_price: 180.00,
            current_price: 175.25,
            target_date: '2025-09-15',
            created_at: '2025-09-01',
            status: 'pending'
        }
    ];
    
    displayCharts(sampleCharts);
}

// ì°¨íŠ¸ í‘œì‹œ
function displayCharts(charts) {
    const chartsGrid = document.getElementById('chartsGrid');
    if (!chartsGrid) return;
    
    console.log('Charts data received:', charts);
    
    // chartsê°€ ë°°ì—´ì¸ì§€ í™•ì¸
    if (!Array.isArray(charts)) {
        console.error('Charts data is not an array:', charts);
        chartsGrid.innerHTML = '<div class="no-results">ì°¨íŠ¸ ë°ì´í„° í˜•ì‹ ì˜¤ë¥˜</div>';
        return;
    }
    
    if (charts.length === 0) {
        chartsGrid.innerHTML = '<div class="no-results">í‘œì‹œí•  ì°¨íŠ¸ê°€ ì—†ìŠµë‹ˆë‹¤.</div>';
        return;
    }
    
    const chartsHTML = charts.map(chart => `
        <div class="chart-card">
            <div class="chart-header">
                <h3>${chart.stock_name} (${chart.stock_symbol})</h3>
                <span class="chart-status ${chart.status}">${getStatusText(chart.status)}</span>
            </div>
            <div class="chart-info">
                <div class="price-info">
                    <div class="price-item">
                        <span class="label">í˜„ìž¬ê°€:</span>
                        <span class="value">${formatPrice(chart.current_price)}</span>
                    </div>
                    <div class="price-item">
                        <span class="label">ì˜ˆì¸¡ê°€:</span>
                        <span class="value predicted">${formatPrice(chart.predicted_price)}</span>
                    </div>
                </div>
                <div class="chart-meta">
                    <p class="user">ì˜ˆì¸¡ìž: ${chart.user.username}</p>
                    <p class="date">ëª©í‘œì¼: ${formatDate(chart.target_date)}</p>
                    <p class="created">ìƒì„±ì¼: ${formatDate(chart.created_at)}</p>
                </div>
            </div>
            <div class="chart-actions">
                <button class="btn btn-sm btn-outline" onclick="viewChart(${chart.id})">
                    ìƒì„¸ë³´ê¸°
                </button>
            </div>
        </div>
    `).join('');
    
    chartsGrid.innerHTML = chartsHTML;
}

// ìƒíƒœ í…ìŠ¤íŠ¸ ë³€í™˜
function getStatusText(status) {
    const statusMap = {
        'pending': 'ì˜ˆì¸¡ ì¤‘',
        'completed': 'ì™„ë£Œë¨',
        'expired': 'ë§Œë£Œë¨'
    };
    return statusMap[status] || status;
}

// ê°€ê²© í¬ë§·
function formatPrice(price) {
    return new Intl.NumberFormat('ko-KR').format(price);
}

// ë‚ ì§œ í¬ë§·
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
}

// ì°¨íŠ¸ í•„í„°ë§
function filterCharts() {
    const marketFilter = document.getElementById('marketFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const searchInput = document.getElementById('searchInput').value;
    
    // í•„í„°ë§ëœ ì°¨íŠ¸ ë¡œë“œ
    loadCharts(1); // ì²« íŽ˜ì´ì§€ë¶€í„° ë‹¤ì‹œ ë¡œë“œ
}

// íŽ˜ì´ì§€ ë³€ê²½
function changePage(page) {
    if (page >= 1 && page <= totalPages) {
        loadCharts(page);
    }
}

// íŽ˜ì´ì§€ë„¤ì´ì…˜ ì—…ë°ì´íŠ¸
function updatePagination() {
    const pageInfo = document.getElementById('pageInfo');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    if (pageInfo) {
        pageInfo.textContent = `${currentPage} / ${totalPages}`;
    }
    
    if (prevBtn) {
        prevBtn.disabled = currentPage <= 1;
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentPage >= totalPages;
    }
}

// ì°¨íŠ¸ ë Œë”ë§
function renderCharts() {
    const chartsGrid = document.getElementById('chartsGrid');
    if (!chartsGrid) return;
    
    chartsGrid.innerHTML = '';
    
    if (charts.length === 0) {
        chartsGrid.innerHTML = '<p class="no-results">ê²€ìƒ‰ ê²°ê³¼ê°€ ì—†ìŠµë‹ˆë‹¤.</p>';
        return;
    }
    
    charts.forEach(chart => {
        const chartCard = createChartCard(chart);
        chartsGrid.appendChild(chartCard);
    });
}

// ì°¨íŠ¸ ì¹´ë“œ ìƒì„±
function createChartCard(chart) {
    const card = document.createElement('div');
    card.className = 'chart-card';
    
    const statusClass = chart.status === 'completed' ? 'status-completed' : 'status-pending';
    const statusText = chart.status === 'completed' ? 'ì™„ë£Œë¨' : 'ì˜ˆì¸¡ ì¤‘';
    
    const profitRate = chart.profit_rate ? `${chart.profit_rate}%` : '-';
    const accuracy = chart.accuracy_percentage ? `${chart.accuracy_percentage}%` : '-';
    
    card.innerHTML = `
        <div class="chart-header">
            <div class="chart-title">${chart.stock.name} (${chart.stock.symbol})</div>
            <span class="chart-status ${statusClass}">${statusText}</span>
        </div>
        <div class="chart-info">
            <div><span>ì˜ˆì¸¡ìž:</span> <span>${chart.user.username}</span></div>
            <div><span>í˜„ìž¬ ê°€ê²©:</span> <span>â‚©${chart.current_price.toLocaleString()}</span></div>
            <div><span>ì˜ˆì¸¡ ê°€ê²©:</span> <span>â‚©${chart.predicted_price.toLocaleString()}</span></div>
            <div><span>ëª©í‘œì¼:</span> <span>${new Date(chart.target_date).toLocaleDateString()}</span></div>
            <div><span>ìˆ˜ìµë¥ :</span> <span>${profitRate}</span></div>
            <div><span>ì •í™•ë„:</span> <span>${accuracy}</span></div>
        </div>
        <div class="chart-actions">
            <span><i class="fas fa-eye"></i> ${chart.views_count}</span>
            <span><i class="fas fa-heart"></i> ${chart.likes_count}</span>
            <span><i class="fas fa-comment"></i> ${chart.comments_count}</span>
            <button class="btn btn-outline btn-sm" onclick="viewChart(${chart.id})">ìƒì„¸ë³´ê¸°</button>
        </div>
    `;
    
    return card;
}

// ëž­í‚¹ ë°ì´í„° ë¡œë“œ
async function loadRanking(type) {
    try {
        const response = await fetch(`${API_BASE_URL}/rankings/${type}/`);
        if (response.ok) {
            const rankings = await response.json();
            displayRanking(rankings);
        } else {
            displaySampleRanking(type);
        }
    } catch (error) {
        console.error('ëž­í‚¹ ë¡œë“œ ì˜¤ë¥˜:', error);
        displaySampleRanking(type);
    }
}

// ìƒ˜í”Œ ëž­í‚¹ ë°ì´í„° í‘œì‹œ
function displaySampleRanking(type) {
    const sampleData = {
        accuracy: [
            { username: 'ì˜ˆì¸¡ì™•', accuracy: 95.2, predictions_count: 142 },
            { username: 'ì°¨íŠ¸ë§ˆìŠ¤í„°', accuracy: 89.7, predictions_count: 89 },
            { username: 'íˆ¬ìžê³ ìˆ˜', accuracy: 87.3, predictions_count: 156 }
        ],
        profit: [
            { username: 'ìˆ˜ìµì™•', profit_rate: 45.8, total_profit: 892000 },
            { username: 'ëˆë²Œì´', profit_rate: 38.2, total_profit: 645000 },
            { username: 'íˆ¬ìžì‹ ', profit_rate: 34.7, total_profit: 723000 }
        ],
        predictions: [
            { username: 'ì˜ˆì¸¡ëŸ‰ì‚°', predictions_count: 245, accuracy: 72.5 },
            { username: 'ì°¨íŠ¸ë¶„ì„', predictions_count: 198, accuracy: 68.9 },
            { username: 'ì‹œìž¥í†µì°°', predictions_count: 167, accuracy: 75.2 }
        ]
    };
    
    displayRanking(sampleData[type] || []);
}

// ëž­í‚¹ í‘œì‹œ
function displayRanking(rankings) {
    const rankingTable = document.getElementById('rankingTable');
    if (!rankingTable) return;
    
    if (rankings.length === 0) {
        rankingTable.innerHTML = '<div class="no-results">ëž­í‚¹ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.</div>';
        return;
    }
    
    const tableHTML = `
        <table class="ranking-table">
            <thead>
                <tr>
                    <th>ìˆœìœ„</th>
                    <th>ì‚¬ìš©ìž</th>
                    <th>ì§€í‘œ</th>
                    <th>ì„¸ë¶€ì‚¬í•­</th>
                </tr>
            </thead>
            <tbody>
                ${rankings.map((user, index) => `
                    <tr>
                        <td class="rank">${index + 1}</td>
                        <td class="username">${user.username}</td>
                        <td class="metric">
                            ${user.accuracy ? `${user.accuracy}%` : ''}
                            ${user.profit_rate ? `${user.profit_rate}%` : ''}
                            ${user.predictions_count && !user.accuracy && !user.profit_rate ? user.predictions_count : ''}
                        </td>
                        <td class="details">
                            ${user.predictions_count ? `ì˜ˆì¸¡ ìˆ˜: ${user.predictions_count}` : ''}
                            ${user.total_profit ? `ì´ ìˆ˜ìµ: â‚©${user.total_profit.toLocaleString()}` : ''}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    rankingTable.innerHTML = tableHTML;
}

// ì´ë²¤íŠ¸ ë¡œë“œ
async function loadEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/events/`);
        if (response.ok) {
            const events = await response.json();
            displayEvents(events);
        } else {
            displaySampleEvents();
        }
    } catch (error) {
        console.error('ì´ë²¤íŠ¸ ë¡œë“œ ì˜¤ë¥˜:', error);
        displaySampleEvents();
    }
}

// ìƒ˜í”Œ ì´ë²¤íŠ¸ ë°ì´í„° í‘œì‹œ
function displaySampleEvents() {
    const sampleEvents = [
        {
            id: 1,
            title: 'ì›”ê°„ ì˜ˆì¸¡ ëŒ€íšŒ',
            description: 'ì´ë²ˆ ë‹¬ ê°€ìž¥ ì •í™•í•œ ì˜ˆì¸¡ì„ í•œ ì‚¬ìš©ìžì—ê²Œ 100ë§Œì› ìƒê¸ˆ',
            start_date: '2025-09-01',
            end_date: '2025-09-30',
            prize: '1,000,000ì›',
            participants_count: 245
        }
    ];
    
    displayEvents(sampleEvents);
}

// ì´ë²¤íŠ¸ í‘œì‹œ
function displayEvents(events) {
    const eventsGrid = document.getElementById('eventsGrid');
    if (!eventsGrid) return;
    
    if (events.length === 0) {
        eventsGrid.innerHTML = '<div class="no-results">ì§„í–‰ì¤‘ì¸ ì´ë²¤íŠ¸ê°€ ì—†ìŠµë‹ˆë‹¤.</div>';
        return;
    }
    
    eventsGrid.innerHTML = events.map(event => `
        <div class="event-card">
            <div class="event-header">
                <h3>${event.title}</h3>
                <span class="event-prize">${event.prize}</span>
            </div>
            <div class="event-content">
                <p>${event.description}</p>
                <div class="event-meta">
                    <span>ê¸°ê°„: ${formatDate(event.start_date)} ~ ${formatDate(event.end_date)}</span>
                    <span>ì°¸ê°€ìž: ${event.participants_count}ëª…</span>
                </div>
            </div>
            <div class="event-actions">
                <button class="btn btn-primary btn-sm" onclick="joinEvent(${event.id})">
                    ì°¸ê°€í•˜ê¸°
                </button>
            </div>
        </div>
    `).join('');
}

// ì´ë²¤íŠ¸ ì°¸ê°€
function joinEvent(eventId) {
    if (!currentUser) {
        showNotification('ì´ë²¤íŠ¸ ì°¸ê°€í•˜ë ¤ë©´ ë¡œê·¸ì¸ì´ í•„ìš”í•©ë‹ˆë‹¤.', 'warning');
        showLoginModal();
        return;
    }
    
    showNotification('ì´ë²¤íŠ¸ ì°¸ê°€ ê¸°ëŠ¥ì„ ì¤€ë¹„ì¤‘ìž…ë‹ˆë‹¤.', 'info');
}

// ëª¨ë‹¬ í‘œì‹œ/ìˆ¨ê¹€ í•¨ìˆ˜ë“¤
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

function hideLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function showSignupModal() {
    document.getElementById('signupModal').style.display = 'block';
}

function hideSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth'
        });
        
        // ë„¤ë¹„ê²Œì´ì…˜ í™œì„±í™” ìƒíƒœ ì—…ë°ì´íŠ¸
        updateActiveNavigation(sectionId);
    }
}

// ë„¤ë¹„ê²Œì´ì…˜ í™œì„±í™” ìƒíƒœ ì—…ë°ì´íŠ¸
function updateActiveNavigation(currentSection = null) {
    const navLinks = document.querySelectorAll('.nav-link');
    
    // í˜„ìž¬ ì„¹ì…˜ì´ ì§€ì •ë˜ì§€ ì•Šì€ ê²½ìš° ìŠ¤í¬ë¡¤ ìœ„ì¹˜ë¡œ íŒë‹¨
    if (!currentSection) {
        const sections = ['home', 'charts', 'prediction', 'ranking', 'events', 'subscription'];
        const scrollPosition = window.scrollY + 100;
        
        for (const sectionId of sections) {
            const section = document.getElementById(sectionId);
            if (section) {
                const sectionTop = section.offsetTop;
                const sectionBottom = sectionTop + section.offsetHeight;
                
                if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                    currentSection = sectionId;
                    break;
                }
            }
        }
    }
    
    // ëª¨ë“  ë§í¬ì—ì„œ active í´ëž˜ìŠ¤ ì œê±°
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === ('#' + currentSection)) {
            link.classList.add('active');
        }
    });
}

function viewChart(chartId) {
    // ì°¨íŠ¸ ìƒì„¸ íŽ˜ì´ì§€ë¡œ ì´ë™ ë˜ëŠ” ëª¨ë‹¬ í‘œì‹œ
    showNotification('ì°¨íŠ¸ ìƒì„¸ ë³´ê¸° ê¸°ëŠ¥ì„ ì¤€ë¹„ì¤‘ìž…ë‹ˆë‹¤.', 'info');
}

function showNotification(message, type = 'info') {
    // ì•Œë¦¼ í‘œì‹œ (í† ìŠ¤íŠ¸ ë©”ì‹œì§€)
    const notification = document.createElement('div');
    notification.className = 'notification notification-' + type;
    notification.textContent = message;
    
    // ìŠ¤íƒ€ì¼ ì ìš©
    notification.style.cssText = 
        'position: fixed;' +
        'top: 20px;' +
        'right: 20px;' +
        'padding: 1rem 1.5rem;' +
        'border-radius: 5px;' +
        'color: white;' +
        'font-weight: 500;' +
        'z-index: 3000;' +
        'animation: slideIn 0.3s ease;';
    
    // íƒ€ìž…ë³„ ë°°ê²½ìƒ‰
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196F3'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // 3ì´ˆ í›„ ì œê±°
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
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

// CSS ì• ë‹ˆë©”ì´ì…˜ ë° ìŠ¤íƒ€ì¼ ì¶”ê°€

function showSignupModal() {
    hideLoginModal();
    document.getElementById('signupModal').style.display = 'block';
}

function hideSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth'
        });
        
        // ë„¤ë¹„ê²Œì´ì…˜ í™œì„±í™” ìƒíƒœ ì—…ë°ì´íŠ¸
        updateActiveNavigation(sectionId);
    }
}

// ë„¤ë¹„ê²Œì´ì…˜ í™œì„±í™” ìƒíƒœ ì—…ë°ì´íŠ¸
function updateActiveNavigation(currentSection = null) {
    const navLinks = document.querySelectorAll('.nav-link');
    
    // í˜„ìž¬ ì„¹ì…˜ì´ ì§€ì •ë˜ì§€ ì•Šì€ ê²½ìš° ìŠ¤í¬ë¡¤ ìœ„ì¹˜ë¡œ íŒë‹¨
    if (!currentSection) {
        const sections = ['home', 'charts', 'prediction', 'ranking', 'events', 'subscription'];
        const scrollPosition = window.scrollY + 100;
        
        for (const sectionId of sections) {
            const section = document.getElementById(sectionId);
            if (section) {
                const sectionTop = section.offsetTop;
                const sectionBottom = sectionTop + section.offsetHeight;
                
                if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                    currentSection = sectionId;
                    break;
                }
            }
        }
    }
    
    // ëª¨ë“  ë§í¬ì—ì„œ active í´ëž˜ìŠ¤ ì œê±°
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

// ì‚¬ìš©ìž ë©”ë‰´ ë„¤ë¹„ê²Œì´ì…˜ í•¨ìˆ˜ë“¤
function goToMyProfile() {
    closeUserMenu();
    showNotification('í”„ë¡œí•„ íŽ˜ì´ì§€ë¡œ ì´ë™í•©ë‹ˆë‹¤.', 'info');
    // TODO: í”„ë¡œí•„ íŽ˜ì´ì§€ êµ¬í˜„
}

function goToMyPredictions() {
    closeUserMenu();
    scrollToSection('charts');
    // ë‚´ ì˜ˆì¸¡ë§Œ í•„í„°ë§
    filterMyPredictions();
}

function goToMyRanking() {
    closeUserMenu();
    scrollToSection('ranking');
    showNotification('ë‚´ ëž­í‚¹ ì •ë³´ë¥¼ í‘œì‹œí•©ë‹ˆë‹¤.', 'info');
}

function goToSubscription() {
    closeUserMenu();
    scrollToSection('subscription');
}

function goToSettings() {
    closeUserMenu();
    showNotification('ì„¤ì • íŽ˜ì´ì§€ë¥¼ ì¤€ë¹„ì¤‘ìž…ë‹ˆë‹¤.', 'info');
    // TODO: ì„¤ì • íŽ˜ì´ì§€ êµ¬í˜„
}

function logout() {
    closeUserMenu();
    
    // ë¡œì»¬ ìŠ¤í† ë¦¬ì§€ì—ì„œ í† í° ì œê±°
    localStorage.removeItem('accessToken');
    currentUser = null;
    
    // UI ì—…ë°ì´íŠ¸
    const loginBtn = document.querySelector('.login-btn');
    if (loginBtn) {
        loginBtn.textContent = 'ë¡œê·¸ì¸';
        loginBtn.onclick = showLoginModal;
        loginBtn.style.cursor = 'pointer';
    }
    
    showNotification('ë¡œê·¸ì•„ì›ƒë˜ì—ˆìŠµë‹ˆë‹¤.', 'success');
    
    // í™ˆ ì„¹ì…˜ìœ¼ë¡œ ì´ë™
    scrollToSection('home');
}

function closeUserMenu() {
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        userMenu.remove();
        document.removeEventListener('click', closeUserMenuOnOutsideClick);
    }
}

// ë‚´ ì˜ˆì¸¡ í•„í„°ë§
function filterMyPredictions() {
    if (!currentUser) {
        showNotification('ë¡œê·¸ì¸ì´ í•„ìš”í•©ë‹ˆë‹¤.', 'warning');
        return;
    }
    
    // ì°¨íŠ¸ í•„í„°ë§ ë¡œì§ êµ¬í˜„
    showNotification('ë‚´ ì˜ˆì¸¡ì„ í‘œì‹œí•©ë‹ˆë‹¤.', 'info');
    // TODO: ì‹¤ì œ í•„í„°ë§ êµ¬í˜„
}

// ì˜ˆì¸¡ ì‹œìž‘í•˜ê¸°
function startPrediction() {
    if (!currentUser) {
        showSignupModal();
        return;
    }
    
    scrollToSection('prediction');
    showNotification('ì˜ˆì¸¡ì„ ì‹œìž‘í•´ë³´ì„¸ìš”!', 'success');
}

// êµ¬ë… ê³„íš ì„ íƒ
function subscribePlan(planType) {
    if (!currentUser) {
        showNotification('êµ¬ë…í•˜ë ¤ë©´ ë¡œê·¸ì¸ì´ í•„ìš”í•©ë‹ˆë‹¤.', 'warning');
        showLoginModal();
        return;
    }
    
    showNotification(`${planType} í”Œëžœ êµ¬ë… ê¸°ëŠ¥ì„ ì¤€ë¹„ì¤‘ìž…ë‹ˆë‹¤.`, 'info');
    // TODO: ì‹¤ì œ êµ¬ë… ì²˜ë¦¬ êµ¬í˜„
}

// íƒ­ ì „í™˜ (ëž­í‚¹ ì„¹ì…˜)
function showRanking(type) {
    // ëª¨ë“  íƒ­ ë²„íŠ¼ì—ì„œ active í´ëž˜ìŠ¤ ì œê±°
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // í´ë¦­ëœ íƒ­ì— active í´ëž˜ìŠ¤ ì¶”ê°€
    event.target.classList.add('active');
    
    // í•´ë‹¹ ëž­í‚¹ ë°ì´í„° ë¡œë“œ
    loadRanking(type);
}

function viewChart(chartId) {
    // ì°¨íŠ¸ ìƒì„¸ íŽ˜ì´ì§€ë¡œ ì´ë™ ë˜ëŠ” ëª¨ë‹¬ í‘œì‹œ
    showNotification('ì°¨íŠ¸ ìƒì„¸ ë³´ê¸° ê¸°ëŠ¥ì„ ì¤€ë¹„ì¤‘ìž…ë‹ˆë‹¤.', 'info');
}

function showNotification(message, type = 'info') {
    // ì•Œë¦¼ í‘œì‹œ (í† ìŠ¤íŠ¸ ë©”ì‹œì§€)
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // ìŠ¤íƒ€ì¼ ì ìš©
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
    
    // íƒ€ìž…ë³„ ë°°ê²½ìƒ‰
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196F3'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // 3ì´ˆ í›„ ì œê±°
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

// Copy the valid JavaScript content and add new API functions
// This will be used to replace the corrupted app.js file

// Tiingo API integration functions
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

// Marketstack API integration functions
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

// Enhanced market data loading with multiple API sources
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

// Test all API sources for a specific symbol
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
    
    // Display results in the API comparison section
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

// Add API testing to the market data section
function addAPITestingUI() {
    const marketSection = document.querySelector('#market');
    if (!marketSection) return;
    
    // Add API comparison container if it doesn't exist
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
        
        // Insert after market data display
        const marketData = document.querySelector('.market-data');
        if (marketData) {
            marketData.parentNode.insertBefore(apiContainer, marketData.nextSibling);
        }
    }
}
