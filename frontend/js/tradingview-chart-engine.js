/**
 * TradingView-Style Lightweight Chart Engine
 * Direct canvas implementation for instant mouse response
 */

class TradingViewChart {
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.data = [];
        this.predictions = [];
        
        // Chart state
        this.viewport = {
            startIndex: 0,
            endIndex: 0,
            minPrice: 0,
            maxPrice: 0,
            padding: { top: 20, right: 80, bottom: 40, left: 40 }
        };
        
        // Mouse state
        this.mouse = {
            x: 0, y: 0,
            isDown: false,
            lastX: 0, lastY: 0,
            crosshair: true
        };
        
        // Chart options
        this.options = {
            candleWidth: 8,
            candleSpacing: 12,
            gridColor: '#2a2e39',
            textColor: '#d1d4dc',
            backgroundColor: '#1e222d',
            upColor: '#26a69a',
            downColor: '#ef5350',
            predictionColor: '#ff6b35',
            ...options
        };
        
        this.setupCanvas();
        this.setupEvents();
    }
    
    setupCanvas() {
        const rect = this.canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        
        this.ctx.scale(dpr, dpr);
        this.width = rect.width;
        this.height = rect.height;
    }
    
    setupEvents() {
        // Mouse events for smooth interaction
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('mouseout', this.onMouseOut.bind(this));
        this.canvas.addEventListener('wheel', this.onWheel.bind(this));
        this.canvas.addEventListener('click', this.onClick.bind(this));
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', this.onTouchStart.bind(this));
        this.canvas.addEventListener('touchmove', this.onTouchMove.bind(this));
        this.canvas.addEventListener('touchend', this.onTouchEnd.bind(this));
        
        // Prevent context menu
        this.canvas.addEventListener('contextmenu', e => e.preventDefault());
    }
    
    onMouseDown(e) {
        this.mouse.isDown = true;
        this.mouse.lastX = e.offsetX;
        this.mouse.lastY = e.offsetY;
        this.canvas.style.cursor = 'grabbing';
    }
    
    onMouseMove(e) {
        this.mouse.x = e.offsetX;
        this.mouse.y = e.offsetY;
        
        if (this.mouse.isDown) {
            // Pan chart
            const deltaX = e.offsetX - this.mouse.lastX;
            this.pan(deltaX);
            this.mouse.lastX = e.offsetX;
        }
        
        this.draw();
    }
    
    onMouseUp(e) {
        this.mouse.isDown = false;
        this.canvas.style.cursor = 'crosshair';
    }
    
    onMouseOut(e) {
        this.mouse.crosshair = false;
        this.draw();
    }
    
    onWheel(e) {
        e.preventDefault();
        const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9;
        this.zoom(zoomFactor, e.offsetX);
    }
    
    onClick(e) {
        // Create prediction on click
        const { date, price } = this.screenToData(e.offsetX, e.offsetY);
        if (date && price) {
            this.addPrediction(date, price);
            this.draw();
            
            // Emit prediction event
            this.canvas.dispatchEvent(new CustomEvent('prediction', {
                detail: { date, price }
            }));
        }
    }
    
    onTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        this.onMouseDown({
            offsetX: touch.clientX - rect.left,
            offsetY: touch.clientY - rect.top
        });
    }
    
    onTouchMove(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        this.onMouseMove({
            offsetX: touch.clientX - rect.left,
            offsetY: touch.clientY - rect.top
        });
    }
    
    onTouchEnd(e) {
        e.preventDefault();
        if (e.touches.length === 0) {
            this.onMouseUp({});
            
            // Handle tap for prediction
            if (e.changedTouches.length > 0) {
                const touch = e.changedTouches[0];
                const rect = this.canvas.getBoundingClientRect();
                this.onClick({
                    offsetX: touch.clientX - rect.left,
                    offsetY: touch.clientY - rect.top
                });
            }
        }
    }
    
    setData(data) {
        this.data = data;
        this.calculateViewport();
        this.draw();
    }
    
    calculateViewport() {
        if (this.data.length === 0) return;
        
        // Show last 50 candles by default
        const visibleCandles = Math.min(50, this.data.length);
        this.viewport.endIndex = this.data.length - 1;
        this.viewport.startIndex = Math.max(0, this.viewport.endIndex - visibleCandles + 1);
        
        // Calculate price range
        const visibleData = this.data.slice(this.viewport.startIndex, this.viewport.endIndex + 1);
        const prices = visibleData.flatMap(d => [d.high, d.low]);
        this.viewport.minPrice = Math.min(...prices);
        this.viewport.maxPrice = Math.max(...prices);
        
        // Add padding
        const range = this.viewport.maxPrice - this.viewport.minPrice;
        const padding = range * 0.1;
        this.viewport.minPrice -= padding;
        this.viewport.maxPrice += padding;
    }
    
    pan(deltaX) {
        const candlesPerPixel = (this.viewport.endIndex - this.viewport.startIndex) / this.getChartWidth();
        const candleDelta = -deltaX * candlesPerPixel;
        
        const newStart = this.viewport.startIndex + candleDelta;
        const newEnd = this.viewport.endIndex + candleDelta;
        
        // Constrain to data bounds
        if (newStart >= 0 && newEnd < this.data.length) {
            this.viewport.startIndex = newStart;
            this.viewport.endIndex = newEnd;
        }
    }
    
    zoom(factor, centerX) {
        const candleCount = this.viewport.endIndex - this.viewport.startIndex;
        const newCandleCount = Math.max(10, Math.min(this.data.length, candleCount * factor));
        
        const chartWidth = this.getChartWidth();
        const centerRatio = centerX / chartWidth;
        
        const centerCandle = this.viewport.startIndex + (candleCount * centerRatio);
        const newStart = centerCandle - (newCandleCount * centerRatio);
        const newEnd = newStart + newCandleCount;
        
        // Constrain to data bounds
        this.viewport.startIndex = Math.max(0, newStart);
        this.viewport.endIndex = Math.min(this.data.length - 1, newEnd);
        
        this.calculatePriceRange();
    }
    
    calculatePriceRange() {
        const visibleData = this.data.slice(this.viewport.startIndex, this.viewport.endIndex + 1);
        const prices = visibleData.flatMap(d => [d.high, d.low]);
        this.viewport.minPrice = Math.min(...prices);
        this.viewport.maxPrice = Math.max(...prices);
        
        const range = this.viewport.maxPrice - this.viewport.minPrice;
        const padding = range * 0.1;
        this.viewport.minPrice -= padding;
        this.viewport.maxPrice += padding;
    }
    
    getChartWidth() {
        return this.width - this.viewport.padding.left - this.viewport.padding.right;
    }
    
    getChartHeight() {
        return this.height - this.viewport.padding.top - this.viewport.padding.bottom;
    }
    
    priceToY(price) {
        const chartHeight = this.getChartHeight();
        const priceRange = this.viewport.maxPrice - this.viewport.minPrice;
        return this.viewport.padding.top + ((this.viewport.maxPrice - price) / priceRange) * chartHeight;
    }
    
    indexToX(index) {
        const chartWidth = this.getChartWidth();
        const visibleCandles = this.viewport.endIndex - this.viewport.startIndex;
        const x = ((index - this.viewport.startIndex) / visibleCandles) * chartWidth;
        return this.viewport.padding.left + x;
    }
    
    screenToData(screenX, screenY) {
        // Convert screen coordinates to data
        const chartWidth = this.getChartWidth();
        const chartHeight = this.getChartHeight();
        
        if (screenX < this.viewport.padding.left || screenX > this.width - this.viewport.padding.right ||
            screenY < this.viewport.padding.top || screenY > this.height - this.viewport.padding.bottom) {
            return { date: null, price: null };
        }
        
        // Calculate candle index
        const relativeX = screenX - this.viewport.padding.left;
        const visibleCandles = this.viewport.endIndex - this.viewport.startIndex;
        const candleIndex = Math.floor(this.viewport.startIndex + (relativeX / chartWidth) * visibleCandles);
        
        // Calculate price
        const relativeY = screenY - this.viewport.padding.top;
        const priceRange = this.viewport.maxPrice - this.viewport.minPrice;
        const price = this.viewport.maxPrice - (relativeY / chartHeight) * priceRange;
        
        // Get date from data or extrapolate
        let date;
        if (candleIndex < this.data.length && candleIndex >= 0) {
            date = new Date(this.data[candleIndex].timestamp);
        } else if (candleIndex >= this.data.length && this.data.length > 0) {
            // Future date extrapolation
            const lastDate = new Date(this.data[this.data.length - 1].timestamp);
            const daysAhead = candleIndex - this.data.length + 1;
            date = new Date(lastDate.getTime() + daysAhead * 24 * 60 * 60 * 1000);
        }
        
        return { date, price };
    }
    
    addPrediction(date, price) {
        // Remove existing prediction for the same date
        this.predictions = this.predictions.filter(p => {
            const diffDays = Math.abs(new Date(p.date) - date) / (1000 * 60 * 60 * 24);
            return diffDays >= 1;
        });
        
        this.predictions.push({
            id: Date.now(),
            date: date,
            price: price
        });
    }
    
    removePrediction(id) {
        this.predictions = this.predictions.filter(p => p.id !== id);
        this.draw();
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Draw background
        this.ctx.fillStyle = this.options.backgroundColor;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        if (this.data.length === 0) return;
        
        this.drawGrid();
        this.drawCandles();
        this.drawPredictions();
        this.drawPriceScale();
        this.drawTimeScale();
        
        if (this.mouse.crosshair) {
            this.drawCrosshair();
        }
    }
    
    drawGrid() {
        this.ctx.strokeStyle = this.options.gridColor;
        this.ctx.lineWidth = 1;
        
        const chartWidth = this.getChartWidth();
        const chartHeight = this.getChartHeight();
        
        // Horizontal grid lines
        for (let i = 0; i <= 10; i++) {
            const y = this.viewport.padding.top + (i / 10) * chartHeight;
            this.ctx.beginPath();
            this.ctx.moveTo(this.viewport.padding.left, y);
            this.ctx.lineTo(this.viewport.padding.left + chartWidth, y);
            this.ctx.stroke();
        }
        
        // Vertical grid lines
        for (let i = 0; i <= 10; i++) {
            const x = this.viewport.padding.left + (i / 10) * chartWidth;
            this.ctx.beginPath();
            this.ctx.moveTo(x, this.viewport.padding.top);
            this.ctx.lineTo(x, this.viewport.padding.top + chartHeight);
            this.ctx.stroke();
        }
    }
    
    drawCandles() {
        const visibleData = this.data.slice(this.viewport.startIndex, this.viewport.endIndex + 1);
        const candleWidth = Math.max(2, this.getChartWidth() / visibleData.length * 0.8);
        
        visibleData.forEach((candle, i) => {
            const index = this.viewport.startIndex + i;
            const x = this.indexToX(index);
            
            const openY = this.priceToY(candle.open);
            const closeY = this.priceToY(candle.close);
            const highY = this.priceToY(candle.high);
            const lowY = this.priceToY(candle.low);
            
            const isUp = candle.close >= candle.open;
            const color = isUp ? this.options.upColor : this.options.downColor;
            
            // Draw wick
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 1;
            this.ctx.beginPath();
            this.ctx.moveTo(x, highY);
            this.ctx.lineTo(x, lowY);
            this.ctx.stroke();
            
            // Draw body
            this.ctx.fillStyle = color;
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 1;
            
            const bodyTop = Math.min(openY, closeY);
            const bodyHeight = Math.max(Math.abs(closeY - openY), 1);
            
            this.ctx.fillRect(x - candleWidth/2, bodyTop, candleWidth, bodyHeight);
            this.ctx.strokeRect(x - candleWidth/2, bodyTop, candleWidth, bodyHeight);
        });
    }
    
    drawPredictions() {
        this.predictions.forEach(prediction => {
            const date = new Date(prediction.date);
            const price = prediction.price;
            
            // Find approximate x position
            let x;
            if (this.data.length > 0) {
                const lastDate = new Date(this.data[this.data.length - 1].timestamp);
                const firstDate = new Date(this.data[0].timestamp);
                const totalTime = lastDate.getTime() - firstDate.getTime();
                const predictionTime = date.getTime() - firstDate.getTime();
                const timeRatio = predictionTime / totalTime;
                
                x = this.viewport.padding.left + timeRatio * this.getChartWidth();
            }
            
            const y = this.priceToY(price);
            
            // Skip if outside visible area
            if (x < this.viewport.padding.left || x > this.width - this.viewport.padding.right ||
                y < this.viewport.padding.top || y > this.height - this.viewport.padding.bottom) {
                return;
            }
            
            // Draw prediction point
            this.ctx.fillStyle = this.options.predictionColor;
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 8, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.stroke();
            
            // Draw inner dot
            this.ctx.fillStyle = '#ffffff';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 3, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    drawPriceScale() {
        this.ctx.fillStyle = this.options.textColor;
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'left';
        
        const steps = 10;
        const priceRange = this.viewport.maxPrice - this.viewport.minPrice;
        
        for (let i = 0; i <= steps; i++) {
            const price = this.viewport.maxPrice - (i / steps) * priceRange;
            const y = this.viewport.padding.top + (i / steps) * this.getChartHeight();
            
            const priceText = price.toFixed(2);
            this.ctx.fillText(priceText, this.width - this.viewport.padding.right + 5, y + 4);
        }
    }
    
    drawTimeScale() {
        this.ctx.fillStyle = this.options.textColor;
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        
        const visibleData = this.data.slice(this.viewport.startIndex, this.viewport.endIndex + 1);
        const labelStep = Math.max(1, Math.floor(visibleData.length / 6));
        
        for (let i = 0; i < visibleData.length; i += labelStep) {
            const candle = visibleData[i];
            const index = this.viewport.startIndex + i;
            const x = this.indexToX(index);
            
            const date = new Date(candle.timestamp);
            const dateText = `${date.getMonth() + 1}/${date.getDate()}`;
            
            this.ctx.fillText(dateText, x, this.height - this.viewport.padding.bottom + 20);
        }
    }
    
    drawCrosshair() {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        
        // Vertical line
        this.ctx.beginPath();
        this.ctx.moveTo(this.mouse.x, this.viewport.padding.top);
        this.ctx.lineTo(this.mouse.x, this.height - this.viewport.padding.bottom);
        this.ctx.stroke();
        
        // Horizontal line
        this.ctx.beginPath();
        this.ctx.moveTo(this.viewport.padding.left, this.mouse.y);
        this.ctx.lineTo(this.width - this.viewport.padding.right, this.mouse.y);
        this.ctx.stroke();
        
        this.ctx.setLineDash([]);
    }
}

// Export for use
window.TradingViewChart = TradingViewChart;