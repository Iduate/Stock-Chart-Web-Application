// TradingView-Style Mouse Wheel Chart Controller
class TradingViewWheelController {
    constructor(chartContainer, chartInstance) {
        this.chartContainer = chartContainer;
        this.chartInstance = chartInstance;
        this.isEnabled = true;
        this.zoomSensitivity = 0.1;
        this.scrollSensitivity = 30;
        this.minZoom = 0.1;
        this.maxZoom = 10;
        this.currentZoom = 1;
        this.scrollPosition = 0;
        this.maxScrollPosition = 0;
        
        // Animation properties
        this.isAnimating = false;
        this.animationDuration = 200;
        
        this.init();
    }
    
    init() {
        console.log('🔄 Initializing TradingView-style mouse wheel controller...');
        this.bindEvents();
        this.setupChartLimits();
    }
    
    bindEvents() {
        // Primary wheel event handler
        this.chartContainer.addEventListener('wheel', (e) => {
            if (!this.isEnabled) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            const isCtrlPressed = e.ctrlKey || e.metaKey;
            const delta = e.deltaY;
            
            if (isCtrlPressed) {
                // CTRL + Wheel = Zoom (like TradingView)
                this.handleZoom(delta, e.clientX, e.clientY);
            } else {
                // Plain wheel = Horizontal scroll (like TradingView)
                this.handleScroll(delta);
            }
        }, { passive: false });
        
        // Handle keyboard shortcuts like TradingView
        document.addEventListener('keydown', (e) => {
            if (!this.chartContainer.matches(':hover')) return;
            
            switch(e.code) {
                case 'Equal':
                case 'NumpadAdd':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.zoomIn();
                    }
                    break;
                case 'Minus':
                case 'NumpadSubtract':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.zoomOut();
                    }
                    break;
                case 'Digit0':
                case 'Numpad0':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.resetZoom();
                    }
                    break;
            }
        });
        
        // Mouse position tracking for zoom focus
        this.chartContainer.addEventListener('mousemove', (e) => {
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
        });
    }
    
    // TradingView-style zoom functionality
    handleZoom(delta, mouseX, mouseY) {
        const zoomFactor = delta > 0 ? (1 - this.zoomSensitivity) : (1 + this.zoomSensitivity);
        const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.currentZoom * zoomFactor));
        
        if (newZoom === this.currentZoom) return;
        
        console.log(`🔍 TradingView Zoom: ${this.currentZoom.toFixed(2)} → ${newZoom.toFixed(2)}`);
        
        // Calculate zoom focus point (like TradingView)
        const rect = this.chartContainer.getBoundingClientRect();
        const focusX = (mouseX - rect.left) / rect.width;
        const focusY = (mouseY - rect.top) / rect.height;
        
        this.currentZoom = newZoom;
        this.applyZoom(focusX, focusY);
        
        // Show zoom indicator (like TradingView)
        this.showZoomIndicator(newZoom);
    }
    
    // TradingView-style horizontal scrolling
    handleScroll(delta) {
        const scrollAmount = (delta > 0 ? this.scrollSensitivity : -this.scrollSensitivity);
        const newScrollPosition = Math.max(0, Math.min(this.maxScrollPosition, this.scrollPosition + scrollAmount));
        
        if (newScrollPosition === this.scrollPosition) return;
        
        console.log(`📜 TradingView Scroll: ${this.scrollPosition} → ${newScrollPosition}`);
        
        this.scrollPosition = newScrollPosition;
        this.applyScroll();
        
        // Load more data if needed (like TradingView)
        this.checkDataLoading();
    }
    
    applyZoom(focusX = 0.5, focusY = 0.5) {
        if (!this.chartInstance) return;
        
        // Apply zoom to Korean chart
        if (window.koreanCanvasChart) {
            this.applyKoreanChartZoom(focusX, focusY);
        }
        
        // Apply zoom to Chart.js if exists
        if (this.chartInstance.scales) {
            this.applyChartJsZoom(focusX, focusY);
        }
        
        this.triggerChartUpdate();
    }
    
    applyKoreanChartZoom(focusX, focusY) {
        const chart = window.koreanCanvasChart;
        if (!chart) return;
        
        // Calculate visible data range based on zoom
        const totalDataPoints = chart.data ? chart.data.length : 50;
        const visiblePoints = Math.floor(totalDataPoints / this.currentZoom);
        
        // Adjust start position based on focus point
        const currentStart = chart.startIndex || 0;
        const focusOffset = Math.floor(visiblePoints * focusX);
        const newStart = Math.max(0, Math.min(totalDataPoints - visiblePoints, currentStart - focusOffset));
        
        // Update chart properties
        chart.startIndex = newStart;
        chart.endIndex = newStart + visiblePoints;
        chart.zoomLevel = this.currentZoom;
        
        // Force redraw
        chart.draw();
        
        console.log(`🏛️ Korean Chart Zoom Applied: ${visiblePoints} visible points, start: ${newStart}`);
    }
    
    applyChartJsZoom(focusX, focusY) {
        const chart = this.chartInstance;
        if (!chart.scales || !chart.scales.x) return;
        
        // Get current x-axis range
        const xScale = chart.scales.x;
        const currentMin = xScale.min;
        const currentMax = xScale.max;
        const currentRange = currentMax - currentMin;
        
        // Calculate new range based on zoom
        const newRange = currentRange / this.currentZoom;
        const focusPoint = currentMin + (currentRange * focusX);
        
        // Calculate new min/max
        const newMin = focusPoint - (newRange * focusX);
        const newMax = focusPoint + (newRange * (1 - focusX));
        
        // Apply new range
        chart.options.scales.x.min = newMin;
        chart.options.scales.x.max = newMax;
        
        console.log(`📊 Chart.js Zoom Applied: Range ${currentRange.toFixed(0)} → ${newRange.toFixed(0)}`);
    }
    
    applyScroll() {
        // Apply horizontal scroll to Korean chart
        if (window.koreanCanvasChart) {
            this.applyKoreanChartScroll();
        }
        
        // Apply scroll to Chart.js if exists
        if (this.chartInstance && this.chartInstance.scales) {
            this.applyChartJsScroll();
        }
        
        this.triggerChartUpdate();
    }
    
    applyKoreanChartScroll() {
        const chart = window.koreanCanvasChart;
        if (!chart) return;
        
        const totalDataPoints = chart.data ? chart.data.length : 50;
        const visiblePoints = chart.endIndex - chart.startIndex;
        
        // Calculate scroll as percentage
        const scrollPercent = this.scrollPosition / this.maxScrollPosition;
        const maxStart = Math.max(0, totalDataPoints - visiblePoints);
        const newStart = Math.floor(maxStart * scrollPercent);
        
        chart.startIndex = newStart;
        chart.endIndex = newStart + visiblePoints;
        chart.draw();
        
        console.log(`🏛️ Korean Chart Scroll: Position ${this.scrollPosition}, Start Index: ${newStart}`);
    }
    
    applyChartJsScroll() {
        const chart = this.chartInstance;
        if (!chart.scales || !chart.scales.x) return;
        
        const xScale = chart.scales.x;
        const dataLength = chart.data.datasets[0]?.data?.length || 0;
        if (dataLength === 0) return;
        
        // Calculate scroll offset
        const scrollPercent = this.scrollPosition / this.maxScrollPosition;
        const visibleRange = (xScale.max - xScale.min);
        const totalRange = dataLength;
        const maxOffset = Math.max(0, totalRange - visibleRange);
        const offset = maxOffset * scrollPercent;
        
        // Apply scroll offset
        chart.options.scales.x.min = offset;
        chart.options.scales.x.max = offset + visibleRange;
        
        console.log(`📊 Chart.js Scroll: Offset ${offset.toFixed(0)}, Range: ${visibleRange.toFixed(0)}`);
    }
    
    setupChartLimits() {
        // Set maximum scroll position based on data length
        if (window.koreanCanvasChart && window.koreanCanvasChart.data) {
            const dataLength = window.koreanCanvasChart.data.length;
            this.maxScrollPosition = Math.max(0, dataLength * 10); // 10px per data point
        } else {
            this.maxScrollPosition = 1000; // Default
        }
        
        console.log(`📏 Chart limits set: Max scroll ${this.maxScrollPosition}`);
    }
    
    // Quick zoom functions (like TradingView shortcuts)
    zoomIn() {
        this.handleZoom(-100, this.lastMouseX || 0, this.lastMouseY || 0);
    }
    
    zoomOut() {
        this.handleZoom(100, this.lastMouseX || 0, this.lastMouseY || 0);
    }
    
    resetZoom() {
        console.log('🔄 Resetting zoom to default (like TradingView Ctrl+0)');
        this.currentZoom = 1;
        this.scrollPosition = this.maxScrollPosition * 0.8; // Show recent data
        this.applyZoom(0.5, 0.5);
        this.applyScroll();
        this.showZoomIndicator(1, 'Reset');
    }
    
    // Visual feedback like TradingView
    showZoomIndicator(zoomLevel, action = 'Zoom') {
        // Remove existing indicator
        const existingIndicator = document.querySelector('.tv-zoom-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        // Create zoom indicator
        const indicator = document.createElement('div');
        indicator.className = 'tv-zoom-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            z-index: 10000;
            pointer-events: none;
            transition: opacity 0.3s ease;
        `;
        indicator.textContent = `${action}: ${(zoomLevel * 100).toFixed(0)}%`;
        
        document.body.appendChild(indicator);
        
        // Auto-remove after 2 seconds
        setTimeout(() => {
            if (indicator.parentElement) {
                indicator.style.opacity = '0';
                setTimeout(() => {
                    if (indicator.parentElement) {
                        indicator.parentElement.removeChild(indicator);
                    }
                }, 300);
            }
        }, 2000);
    }
    
    checkDataLoading() {
        // Check if we need to load more historical data (like TradingView)
        const scrollPercent = this.scrollPosition / this.maxScrollPosition;
        
        if (scrollPercent < 0.1) {
            // Near the beginning - load more historical data
            this.loadMoreHistoricalData();
        } else if (scrollPercent > 0.9) {
            // Near the end - load more recent data
            this.loadMoreRecentData();
        }
    }
    
    async loadMoreHistoricalData() {
        console.log('📡 Loading more historical data (like TradingView)...');
        
        if (window.loadStockData && currentStockSymbol) {
            try {
                // Load more days of historical data
                const currentDays = parseInt(chartTimeRange?.value || '90');
                const moreDays = Math.min(currentDays * 2, 365);
                
                await window.loadStockData(currentStockSymbol, moreDays, currentInterval);
                this.setupChartLimits(); // Update limits with new data
                
                console.log('✅ Historical data loaded successfully');
            } catch (error) {
                console.error('❌ Failed to load historical data:', error);
            }
        }
    }
    
    async loadMoreRecentData() {
        console.log('📡 Loading more recent data (like TradingView)...');
        
        // In a real application, this would fetch the latest data
        // For now, we'll just update the chart limits
        this.setupChartLimits();
    }
    
    triggerChartUpdate() {
        // Trigger update event for external listeners
        const event = new CustomEvent('tradingViewChartUpdate', {
            detail: {
                zoom: this.currentZoom,
                scroll: this.scrollPosition,
                timestamp: Date.now()
            }
        });
        
        this.chartContainer.dispatchEvent(event);
    }
    
    // Enable/disable functionality
    enable() {
        this.isEnabled = true;
        console.log('✅ TradingView mouse wheel enabled');
    }
    
    disable() {
        this.isEnabled = false;
        console.log('❌ TradingView mouse wheel disabled');
    }
    
    // Get current state (for debugging)
    getState() {
        return {
            zoom: this.currentZoom,
            scroll: this.scrollPosition,
            maxScroll: this.maxScrollPosition,
            enabled: this.isEnabled
        };
    }
}

// Enhanced Chart Manager integration
if (window.ChartManager) {
    // Extend the existing ChartManager with TradingView wheel functionality
    const originalInit = window.ChartManager.prototype.init;
    
    window.ChartManager.prototype.init = function() {
        // Call original init
        originalInit.call(this);
        
        // Add TradingView wheel controller
        this.setupTradingViewWheel();
    };
    
    window.ChartManager.prototype.setupTradingViewWheel = function() {
        const chartContainer = this.getChartContainer();
        if (!chartContainer) {
            console.warn('⚠️ Chart container not found for TradingView wheel setup');
            return;
        }
        
        // Initialize TradingView wheel controller
        this.wheelController = new TradingViewWheelController(chartContainer.parentElement, this.currentChart);
        
        console.log('✅ TradingView-style mouse wheel functionality activated');
        
        // Add control buttons
        this.addWheelControlButtons();
    };
    
    window.ChartManager.prototype.addWheelControlButtons = function() {
        const controlsContainer = document.querySelector('.chart-controls, .prediction-controls');
        if (!controlsContainer) return;
        
        const wheelControls = document.createElement('div');
        wheelControls.className = 'wheel-controls';
        wheelControls.style.cssText = 'margin: 10px 0; display: flex; gap: 5px; flex-wrap: wrap;';
        
        // Zoom In Button
        const zoomInBtn = document.createElement('button');
        zoomInBtn.textContent = '🔍+';
        zoomInBtn.className = 'btn btn-sm';
        zoomInBtn.title = 'Zoom In (Ctrl++)';
        zoomInBtn.onclick = () => this.wheelController?.zoomIn();
        
        // Zoom Out Button
        const zoomOutBtn = document.createElement('button');
        zoomOutBtn.textContent = '🔍-';
        zoomOutBtn.className = 'btn btn-sm';
        zoomOutBtn.title = 'Zoom Out (Ctrl+-)';
        zoomOutBtn.onclick = () => this.wheelController?.zoomOut();
        
        // Reset Zoom Button
        const resetBtn = document.createElement('button');
        resetBtn.textContent = '🔄';
        resetBtn.className = 'btn btn-sm';
        resetBtn.title = 'Reset Zoom (Ctrl+0)';
        resetBtn.onclick = () => this.wheelController?.resetZoom();
        
        // Toggle Wheel Button
        const toggleBtn = document.createElement('button');
        toggleBtn.textContent = '🖱️';
        toggleBtn.className = 'btn btn-sm';
        toggleBtn.title = 'Toggle Mouse Wheel';
        toggleBtn.onclick = () => {
            if (this.wheelController?.isEnabled) {
                this.wheelController.disable();
                toggleBtn.style.opacity = '0.5';
            } else {
                this.wheelController?.enable();
                toggleBtn.style.opacity = '1';
            }
        };
        
        wheelControls.appendChild(zoomInBtn);
        wheelControls.appendChild(zoomOutBtn);
        wheelControls.appendChild(resetBtn);
        wheelControls.appendChild(toggleBtn);
        
        controlsContainer.appendChild(wheelControls);
        
        console.log('✅ TradingView wheel control buttons added');
    };
}

// Initialize for standalone use
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize if no ChartManager exists
    if (!window.chartManager) {
        const chartContainers = document.querySelectorAll('#priceChart, .chart-container, canvas');
        chartContainers.forEach(container => {
            if (container) {
                const wheelController = new TradingViewWheelController(container.parentElement, null);
                console.log('✅ Standalone TradingView wheel controller initialized');
                
                // Store for global access
                window.tradingViewWheelController = wheelController;
            }
        });
    }
});

// Export for global access
window.TradingViewWheelController = TradingViewWheelController;

console.log('🚀 TradingView-style mouse wheel functionality loaded successfully');