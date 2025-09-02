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
