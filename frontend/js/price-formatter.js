/**
 * Price Formatter Utility
 * Provides consistent price and percentage formatting across the application
 */

class PriceFormatter {
    // Market-specific precision settings
    static MARKET_PRECISION = {
        'crypto': 8,        // Cryptocurrency: up to 8 decimal places
        'us_stock': 2,      // US Stocks: 2 decimal places (cents)
        'kr_stock': 0,      // Korean Stocks: integer (won)
        'jp_stock': 0,      // Japanese Stocks: integer (yen)
        'uk_stock': 2,      // UK Stocks: 2 decimal places (pence)
        'ca_stock': 2,      // Canadian Stocks: 2 decimal places
        'fr_stock': 2,      // French Stocks: 2 decimal places
        'de_stock': 2,      // German Stocks: 2 decimal places
        'index': 2,         // Market indices: 2 decimal places
        'default': 2        // Default: 2 decimal places
    };

    // Symbol-specific precision overrides
    static SYMBOL_PRECISION = {
        'BTC': 2,    // Bitcoin: 2 decimal places for display
        'ETH': 2,    // Ethereum: 2 decimal places for display
        'ADA': 4,    // Cardano: 4 decimal places
        'DOGE': 6,   // Dogecoin: 6 decimal places
        'SHIB': 8    // Shiba Inu: 8 decimal places
    };

    /**
     * Format price based on symbol and market type
     * @param {number} price - The price to format
     * @param {string} symbol - The asset symbol
     * @param {string} market - The market type
     * @returns {string} Formatted price with currency symbol
     */
    static formatPrice(price, symbol = '', market = 'us_stock') {
        if (typeof price !== 'number' || isNaN(price)) {
            return '$0.00';
        }

        const precision = this.getPrecision(symbol, market);
        const formattedPrice = price.toFixed(precision);

        // Add appropriate currency symbol
        const currencySymbol = this.getCurrencySymbol(market);

        return `${currencySymbol}${formattedPrice}`;
    }

    /**
     * Format price without currency symbol
     * @param {number} price - The price to format
     * @param {string} symbol - The asset symbol
     * @param {string} market - The market type
     * @returns {string} Formatted price without currency symbol
     */
    static formatPriceOnly(price, symbol = '', market = 'us_stock') {
        if (typeof price !== 'number' || isNaN(price)) {
            return '0.00';
        }

        const precision = this.getPrecision(symbol, market);
        return price.toFixed(precision);
    }

    /**
     * Format percentage with consistent precision
     * @param {number} percentage - The percentage to format
     * @param {number} precision - Number of decimal places (default: 2)
     * @returns {string} Formatted percentage
     */
    static formatPercentage(percentage, precision = 2) {
        if (typeof percentage !== 'number' || isNaN(percentage)) {
            return '0.00%';
        }

        const sign = percentage >= 0 ? '+' : '';
        return `${sign}${percentage.toFixed(precision)}%`;
    }

    /**
     * Format change in price and percentage
     * @param {number} priceChange - The price change amount
     * @param {number} percentChange - The percentage change
     * @param {string} symbol - The asset symbol
     * @param {string} market - The market type
     * @returns {object} Object with formatted price and percentage changes
     */
    static formatChange(priceChange, percentChange, symbol = '', market = 'us_stock') {
        const formattedPrice = this.formatPriceOnly(Math.abs(priceChange), symbol, market);
        const formattedPercent = this.formatPercentage(percentChange);

        const sign = priceChange >= 0 ? '+' : '-';
        const currencySymbol = this.getCurrencySymbol(market);

        return {
            price: `${sign}${currencySymbol}${formattedPrice}`,
            percentage: formattedPercent,
            isPositive: priceChange >= 0
        };
    }

    /**
     * Get precision for a specific symbol and market
     * @param {string} symbol - The asset symbol
     * @param {string} market - The market type
     * @returns {number} Number of decimal places
     */
    static getPrecision(symbol, market) {
        // Check symbol-specific precision first
        if (this.SYMBOL_PRECISION[symbol.toUpperCase()]) {
            return this.SYMBOL_PRECISION[symbol.toUpperCase()];
        }

        // Fall back to market precision
        return this.MARKET_PRECISION[market] || this.MARKET_PRECISION.default;
    }

    /**
     * Get currency symbol for a market
     * @param {string} market - The market type
     * @returns {string} Currency symbol
     */
    static getCurrencySymbol(market) {
        const symbols = {
            'us_stock': '$',
            'crypto': '$',
            'kr_stock': '₩',
            'jp_stock': '¥',
            'uk_stock': '£',
            'ca_stock': 'C$',
            'fr_stock': '€',
            'de_stock': '€',
            'index': '',
            'default': '$'
        };

        return symbols[market] || symbols.default;
    }

    /**
     * Detect market type from symbol
     * @param {string} symbol - The asset symbol
     * @returns {string} Detected market type
     */
    static detectMarket(symbol) {
        const cryptoSymbols = ['BTC', 'ETH', 'ADA', 'BNB', 'DOT', 'MATIC', 'SOL', 'LTC', 'XRP', 'DOGE', 'SHIB'];
        const indexSymbols = ['^GSPC', '^DJI', '^IXIC', '^RUT'];

        if (cryptoSymbols.includes(symbol.toUpperCase())) {
            return 'crypto';
        }

        if (indexSymbols.includes(symbol.toUpperCase())) {
            return 'index';
        }

        // Default to US stock
        return 'us_stock';
    }

    /**
     * Format volume with appropriate suffixes (K, M, B)
     * @param {number} volume - The volume to format
     * @returns {string} Formatted volume
     */
    static formatVolume(volume) {
        if (typeof volume !== 'number' || isNaN(volume)) {
            return '0';
        }

        if (volume >= 1000000000) {
            return (volume / 1000000000).toFixed(1) + 'B';
        } else if (volume >= 1000000) {
            return (volume / 1000000).toFixed(1) + 'M';
        } else if (volume >= 1000) {
            return (volume / 1000).toFixed(1) + 'K';
        } else {
            return volume.toString();
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PriceFormatter;
}

// Make available globally for browser usage
if (typeof window !== 'undefined') {
    window.PriceFormatter = PriceFormatter;
}
