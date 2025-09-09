// Stock Symbol Component
document.addEventListener('DOMContentLoaded', function () {
    // Find all stock symbols and improve their display
    initializeStockSymbols();

    // Find all time displays and improve them
    initializeTimeDisplays();
});

/**
 * Initialize all stock symbol displays with proper icons
 */
function initializeStockSymbols() {
    // Find all insight-symbol elements
    const stockSymbols = document.querySelectorAll('.insight-symbol');

    stockSymbols.forEach(symbol => {
        const text = symbol.textContent.trim();

        // Create new container with icon
        const container = document.createElement('div');
        container.className = 'stock-symbol-container';

        // Create icon
        const icon = document.createElement('div');
        icon.className = 'stock-symbol-icon';

        // Determine what type of symbol it is
        let iconClass = 'fas fa-chart-line';
        if (text.startsWith('KRX:')) {
            iconClass = 'fas fa-won-sign';
        } else if (text.startsWith('NASDAQ:') || text.startsWith('NYSE:')) {
            iconClass = 'fas fa-dollar-sign';
        } else if (text.startsWith('BTC') || text.startsWith('ETH')) {
            iconClass = 'fab fa-bitcoin';
        }

        // Add icon
        const iconElement = document.createElement('i');
        iconElement.className = iconClass;
        icon.appendChild(iconElement);

        // Add text
        const textElement = document.createElement('span');
        textElement.className = 'stock-symbol-text';
        textElement.textContent = text;

        // Assemble container
        container.appendChild(icon);
        container.appendChild(textElement);

        // Replace original element content
        symbol.innerHTML = '';
        symbol.appendChild(container);
    });
}

/**
 * Initialize all time displays with proper icons
 */
function initializeTimeDisplays() {
    // Find all post-time elements
    const timeDisplays = document.querySelectorAll('.post-time');

    timeDisplays.forEach(timeDisplay => {
        const text = timeDisplay.textContent.trim();

        // Create new container
        const container = document.createElement('div');
        container.className = 'time-ago';

        // Create icon
        const icon = document.createElement('i');
        icon.className = 'fas fa-clock';

        // Create text element
        const textElement = document.createElement('span');
        textElement.textContent = text;

        // Assemble container
        container.appendChild(icon);
        container.appendChild(textElement);

        // Replace original element content
        timeDisplay.innerHTML = '';
        timeDisplay.appendChild(container);
    });
}
