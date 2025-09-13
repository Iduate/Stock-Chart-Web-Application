// Fluorescent Dynamic Charts - Boss Requirements Implementation
// Features: Fluorescent colors, 2-second dynamic updates, mobile-optimized

console.log('🌈 Fluorescent Charts Module Loaded');

// Fluorescent color palette - BOSS UPDATE: MAXIMUM CONTRAST colors with wider spacing
const FLUORESCENT_COLORS = {
    // BOSS APPROVED: High contrast primary colors - much more different from each other
    neonGreen: '#00FF00',        // Pure bright green (primary line)
    electricBlue: '#0033FF',     // Deep electric blue (very different from green)  
    hotPink: '#FF0066',          // Hot magenta pink (completely different)
    brightYellow: '#FFFF00',     // Pure bright yellow (maximum contrast)
    neonOrange: '#FF3300',       // Bright red-orange (distinct)
    electricPurple: '#6600FF',   // Electric purple (very different)
    neonCyan: '#00FFCC',         // Electric cyan (unique tone)
    laserRed: '#FF0033',         // Laser red (sharp contrast)

    // BOSS SPECIAL: Extra contrasting colors for multiple lines with WIDE gaps
    electricLime: '#CCFF00',     // Electric lime - very different from pure green
    deepMagenta: '#CC0099',      // Deep magenta - far from hot pink
    royalBlue: '#0066CC',        // Royal blue - distinct from electric blue
    goldYellow: '#FFD700',       // Gold yellow - warmer than bright yellow

    // Enhanced gradients with MAXIMUM contrast - BOSS APPROVED
    primaryGradient: 'linear-gradient(45deg, #00FF00, #00FF66)',      // Green series
    secondaryGradient: 'linear-gradient(45deg, #0033FF, #0066FF)',    // Blue series  
    tertiaryGradient: 'linear-gradient(45deg, #FF0066, #FF3399)',     // Pink series

    // BOSS REQUESTED: Strong glow effects for clear separation between lines
    strongGreenGlow: 'rgba(0, 255, 0, 0.6)',        // Much stronger green glow
    strongBlueGlow: 'rgba(0, 51, 255, 0.6)',        // Much stronger blue glow  
    strongPinkGlow: 'rgba(255, 0, 102, 0.6)',       // Much stronger pink glow
};

// Dynamic chart configuration for 2-second updates
const DYNAMIC_CONFIG = {
    updateInterval: 2000, // 2 seconds as requested
    animationDuration: 1500,
    glowIntensity: 0.8,
    enablePulse: true,
    enableGlow: true,
    mobileOptimized: true
};

// Chart instances storage
let fluorescentCharts = new Map();
let updateIntervals = new Map();

/**
 * Initialize fluorescent charts with dynamic updates
 */
function initializeFluorescentCharts() {
    console.log('🚀 Initializing Fluorescent Dynamic Charts...');

    // Find all chart containers
    const chartContainers = document.querySelectorAll('#heroChart, #featuredChart, #chart-1, #chart-2, #chart-3, .chart-placeholder');

    chartContainers.forEach((container, index) => {
        if (container && !fluorescentCharts.has(container.id || `chart-${index}`)) {
            createFluorescentChart(container, index);
        }
    });

    // Add mobile-specific enhancements
    if (isMobileDevice()) {
        addMobileEnhancements();
    }
}

/**
 * Create a single fluorescent chart with dynamic updates
 */
function createFluorescentChart(container, index) {
    const chartId = container.id || `fluorescent-chart-${index}`;
    console.log(`📊 Creating fluorescent chart: ${chartId}`);

    // Clear any existing content
    container.innerHTML = '';

    // Set up container styles for MAXIMUM CONTRAST fluorescent effect
    container.style.position = 'relative';
    container.style.background = 'radial-gradient(circle at center, rgba(0, 255, 0, 0.08) 0%, transparent 70%)';
    container.style.borderRadius = '12px';
    container.style.overflow = 'hidden';

    // Add BOSS APPROVED glow wrapper with HIGH CONTRAST colors
    const glowWrapper = document.createElement('div');
    glowWrapper.className = 'fluorescent-glow-wrapper';
    glowWrapper.style.cssText = `
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        background: linear-gradient(45deg, ${FLUORESCENT_COLORS.neonGreen}, ${FLUORESCENT_COLORS.electricBlue});
        border-radius: 15px;
        opacity: 0.15;
        animation: fluorescentPulse 2s ease-in-out infinite;
        z-index: -1;
    `;
    container.appendChild(glowWrapper);

    // Create chart with fluorescent theme
    const chartOptions = getFluorescentChartOptions();
    const chart = LightweightCharts.createChart(container, chartOptions);

    // BOSS REQUIREMENT: PRIMARY line with bright green - very visible
    const areaSeries = chart.addAreaSeries({
        topColor: FLUORESCENT_COLORS.strongGreenGlow,
        bottomColor: 'rgba(0, 255, 0, 0.05)',
        lineColor: FLUORESCENT_COLORS.neonGreen,
        lineWidth: 5,  // BOSS UPDATE: Much thicker line for better visibility
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 10,  // BOSS UPDATE: Larger marker
        crosshairMarkerBorderColor: FLUORESCENT_COLORS.neonGreen,
        crosshairMarkerBackgroundColor: FLUORESCENT_COLORS.neonGreen,
        lastValueVisible: true,
        priceLineVisible: true,
        priceLineWidth: 4,  // BOSS UPDATE: Much thicker price line
        priceLineColor: FLUORESCENT_COLORS.neonGreen,
        priceLineStyle: LightweightCharts.LineStyle.Solid,
    });

    // BOSS REQUIREMENT: SECONDARY line with MAXIMUM CONTRAST - electric blue (very different from green)
    const comparisonSeries = chart.addLineSeries({
        color: FLUORESCENT_COLORS.electricBlue,  // BOSS APPROVED: Very different from green
        lineWidth: 5,  // BOSS UPDATE: Much thicker for better visibility
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 8,
        crosshairMarkerBorderColor: FLUORESCENT_COLORS.electricBlue,
        crosshairMarkerBackgroundColor: FLUORESCENT_COLORS.electricBlue,
        lastValueVisible: true,
        priceLineVisible: false,
    });

    // Store chart instance
    fluorescentCharts.set(chartId, {
        chart: chart,
        areaSeries: areaSeries,
        comparisonSeries: comparisonSeries,
        container: container
    });

    // Generate initial data and start dynamic updates
    generateInitialData(chartId);
    startDynamicUpdates(chartId);

    // Add chart info overlay with fluorescent styling
    addFluorescentOverlay(container, chartId);
}

/**
 * Get chart options with fluorescent theme
 */
function getFluorescentChartOptions() {
    return {
        width: 0, // Will be set by container
        height: 0, // Will be set by container
        layout: {
            background: { color: 'transparent' },
            textColor: FLUORESCENT_COLORS.neonGreen,
            fontSize: 13,  // Slightly larger for better readability
            fontFamily: 'Inter, sans-serif',
        },
        grid: {
            vertLines: {
                color: 'rgba(0, 255, 0, 0.15)',  // More visible grid
                style: LightweightCharts.LineStyle.Dotted,
            },
            horzLines: {
                color: 'rgba(0, 255, 0, 0.15)',  // More visible grid
                style: LightweightCharts.LineStyle.Dotted,
            },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                width: 3,  // Thicker crosshair
                color: FLUORESCENT_COLORS.neonGreen,
                style: LightweightCharts.LineStyle.Solid,
            },
            horzLine: {
                width: 3,  // Thicker crosshair
                color: FLUORESCENT_COLORS.neonGreen,
                style: LightweightCharts.LineStyle.Solid,
            }
        },
        timeScale: {
            borderColor: FLUORESCENT_COLORS.neonGreen,
            timeVisible: true,
            secondsVisible: false,
            tickMarkFormatter: (time) => {
                const date = new Date(time * 1000);
                return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
            }
        },
        rightPriceScale: {
            borderColor: FLUORESCENT_COLORS.neonGreen,
            textColor: FLUORESCENT_COLORS.neonGreen,
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
}

/**
 * Generate initial chart data with WIDE SPACING between lines - BOSS REQUIREMENT
 */
function generateInitialData(chartId) {
    const chartData = fluorescentCharts.get(chartId);
    if (!chartData) return;

    const now = Math.floor(Date.now() / 1000);
    const data = [];
    const comparisonData = [];

    // BOSS UPDATE: Create much wider gap between the two lines
    let basePrice = 100 + Math.random() * 200;
    // BOSS REQUIREMENT: Make comparison line MUCH more separated (30-50% difference instead of 10-20%)
    let comparisonPrice = basePrice * (0.6 + Math.random() * 0.4); // Much wider range: 60% to 100% of base

    for (let i = 99; i >= 0; i--) {
        const time = now - (i * 60); // 1 minute intervals

        // BOSS UPDATE: Different movement patterns to keep lines separated
        const change = (Math.random() - 0.5) * 8; // Slightly larger movements
        basePrice = Math.max(10, basePrice + change);

        // BOSS REQUIREMENT: Comparison line moves differently to maintain gap
        const comparisonChange = (Math.random() - 0.5) * 6; // Different scale
        comparisonPrice = Math.max(10, comparisonPrice + comparisonChange);

        // BOSS SAFETY: Ensure lines don't get too close (minimum 15% gap)
        if (Math.abs(basePrice - comparisonPrice) / basePrice < 0.15) {
            if (basePrice > comparisonPrice) {
                comparisonPrice = basePrice * 0.75; // Force 25% gap below
            } else {
                comparisonPrice = basePrice * 1.3; // Force 30% gap above
            }
        }

        data.push({
            time: time,
            value: parseFloat(basePrice.toFixed(2))
        });

        comparisonData.push({
            time: time,
            value: parseFloat(comparisonPrice.toFixed(2))
        });
    }

    chartData.areaSeries.setData(data);
    chartData.comparisonSeries.setData(comparisonData);

    // Store last values for continuous updates
    chartData.lastPrice = basePrice;
    chartData.lastComparisonPrice = comparisonPrice;
    chartData.lastTime = now;
}

/**
 * Start dynamic updates every 2 seconds as requested
 */
function startDynamicUpdates(chartId) {
    // Clear any existing interval
    if (updateIntervals.has(chartId)) {
        clearInterval(updateIntervals.get(chartId));
    }

    const interval = setInterval(() => {
        updateChartData(chartId);
    }, DYNAMIC_CONFIG.updateInterval);

    updateIntervals.set(chartId, interval);
    console.log(`⚡ Started dynamic updates for ${chartId} (${DYNAMIC_CONFIG.updateInterval}ms interval)`);
}

/**
 * Update chart data with new fluorescent data point - BOSS SPACING REQUIREMENTS
 */
function updateChartData(chartId) {
    const chartData = fluorescentCharts.get(chartId);
    if (!chartData) return;

    // BOSS UPDATE: Generate new data points with maintained spacing
    const now = Math.floor(Date.now() / 1000);
    const priceChange = (Math.random() - 0.5) * 10;  // Larger movements for more drama
    const comparisonChange = (Math.random() - 0.5) * 8;  // Different scale

    chartData.lastPrice = Math.max(10, chartData.lastPrice + priceChange);
    chartData.lastComparisonPrice = Math.max(10, chartData.lastComparisonPrice + comparisonChange);

    // BOSS REQUIREMENT: Maintain minimum spacing between lines (15% gap minimum)
    if (Math.abs(chartData.lastPrice - chartData.lastComparisonPrice) / chartData.lastPrice < 0.15) {
        if (chartData.lastPrice > chartData.lastComparisonPrice) {
            chartData.lastComparisonPrice = chartData.lastPrice * 0.75; // Force 25% gap below
        } else {
            chartData.lastComparisonPrice = chartData.lastPrice * 1.3; // Force 30% gap above
        }
    }

    chartData.lastTime = now;

    // Update series with new data
    chartData.areaSeries.update({
        time: now,
        value: parseFloat(chartData.lastPrice.toFixed(2))
    });

    chartData.comparisonSeries.update({
        time: now,
        value: parseFloat(chartData.lastComparisonPrice.toFixed(2))
    });

    // Update overlay info
    updateFluorescentOverlay(chartId, chartData.lastPrice, priceChange);

    // Add glow pulse effect on update
    triggerGlowPulse(chartData.container);
}

/**
 * Add fluorescent overlay with real-time info
 */
function addFluorescentOverlay(container, chartId) {
    const overlay = document.createElement('div');
    overlay.className = 'fluorescent-overlay';
    overlay.id = `overlay-${chartId}`;
    overlay.style.cssText = `
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid ${FLUORESCENT_COLORS.neonGreen};
        border-radius: 10px;
        padding: 12px;
        color: ${FLUORESCENT_COLORS.neonGreen};
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 0 20px ${FLUORESCENT_COLORS.neonGreenGlow};
        z-index: 10;
        backdrop-filter: blur(10px);
    `;

    overlay.innerHTML = `
        <div class="price-display">$0.00</div>
        <div class="change-display">+0.00 (0.00%)</div>
        <div class="status-display">🔴 LIVE</div>
    `;

    container.appendChild(overlay);
}

/**
 * Update fluorescent overlay with new price data
 */
function updateFluorescentOverlay(chartId, price, change) {
    const overlay = document.getElementById(`overlay-${chartId}`);
    if (!overlay) return;

    const isPositive = change >= 0;
    const changePercent = ((change / price) * 100).toFixed(2);

    // Update colors based on change
    const color = isPositive ? FLUORESCENT_COLORS.neonGreen : FLUORESCENT_COLORS.neonRed;
    const glowColor = isPositive ? FLUORESCENT_COLORS.neonGreenGlow : 'rgba(255, 30, 30, 0.3)';

    overlay.style.borderColor = color;
    overlay.style.boxShadow = `0 0 20px ${glowColor}`;
    overlay.style.color = color;

    // Update content
    overlay.querySelector('.price-display').textContent = `$${price.toFixed(2)}`;
    overlay.querySelector('.change-display').textContent =
        `${isPositive ? '+' : ''}${change.toFixed(2)} (${isPositive ? '+' : ''}${changePercent}%)`;
    overlay.querySelector('.status-display').innerHTML = '🟢 LIVE';
}

/**
 * Trigger glow pulse effect on chart update
 */
function triggerGlowPulse(container) {
    const glowWrapper = container.querySelector('.fluorescent-glow-wrapper');
    if (glowWrapper) {
        glowWrapper.style.animation = 'none';
        setTimeout(() => {
            glowWrapper.style.animation = 'fluorescentPulse 2s ease-in-out infinite';
        }, 10);
    }
}

/**
 * Check if device is mobile for mobile-specific optimizations
 */
function isMobileDevice() {
    return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Add mobile-specific enhancements
 */
function addMobileEnhancements() {
    console.log('📱 Adding mobile optimizations for fluorescent charts');

    // Add mobile-specific CSS
    const mobileStyles = document.createElement('style');
    mobileStyles.textContent = `
        @media (max-width: 768px) {
            .fluorescent-overlay {
                font-size: 12px !important;
                padding: 8px !important;
                top: 10px !important;
                right: 10px !important;
            }
            
            .chart-placeholder {
                min-height: 200px !important;
            }
            
            .fluorescent-glow-wrapper {
                opacity: 0.05 !important;
            }
        }
    `;
    document.head.appendChild(mobileStyles);
}

/**
 * Add CSS animations for fluorescent effects
 */
function addFluorescentStyles() {
    if (document.getElementById('fluorescent-styles')) return;

    const style = document.createElement('style');
    style.id = 'fluorescent-styles';
    style.textContent = `
        @keyframes fluorescentPulse {
            0%, 100% { 
                opacity: 0.1; 
                transform: scale(1);
            }
            50% { 
                opacity: 0.3; 
                transform: scale(1.02);
            }
        }
        
        @keyframes fluorescentGlow {
            0%, 100% { 
                box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
            }
            50% { 
                box-shadow: 0 0 40px rgba(0, 255, 65, 0.6);
            }
        }
        
        .fluorescent-overlay {
            animation: fluorescentGlow 3s ease-in-out infinite;
        }
        
        .chart-placeholder {
            position: relative;
            overflow: hidden;
        }
        
        .chart-placeholder::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.1), transparent);
            animation: fluorescentSweep 4s ease-in-out infinite;
            z-index: 1;
            pointer-events: none;
        }
        
        @keyframes fluorescentSweep {
            0% { left: -100%; }
            50% { left: 100%; }
            100% { left: 100%; }
        }
    `;
    document.head.appendChild(style);
}

/**
 * Cleanup function to stop all dynamic updates
 */
function stopAllDynamicUpdates() {
    console.log('🛑 Stopping all dynamic updates');
    updateIntervals.forEach((interval, chartId) => {
        clearInterval(interval);
        console.log(`Stopped updates for ${chartId}`);
    });
    updateIntervals.clear();
}

/**
 * Restart all dynamic updates
 */
function restartAllDynamicUpdates() {
    console.log('🔄 Restarting all dynamic updates');
    fluorescentCharts.forEach((chartData, chartId) => {
        startDynamicUpdates(chartId);
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    addFluorescentStyles();

    // Wait for LightweightCharts to be ready
    if (typeof LightweightCharts !== 'undefined') {
        setTimeout(initializeFluorescentCharts, 1000);
    } else {
        window.addEventListener('lightweightChartsReady', function () {
            setTimeout(initializeFluorescentCharts, 1000);
        });
    }
});

// Handle page visibility changes to pause/resume updates
document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
        stopAllDynamicUpdates();
    } else {
        restartAllDynamicUpdates();
    }
});

// Export functions for global access
window.fluorescentCharts = {
    initialize: initializeFluorescentCharts,
    stop: stopAllDynamicUpdates,
    restart: restartAllDynamicUpdates,
    charts: fluorescentCharts,
    colors: FLUORESCENT_COLORS
};

console.log('✨ Fluorescent Charts Module Ready - Boss Requirements Implemented');
