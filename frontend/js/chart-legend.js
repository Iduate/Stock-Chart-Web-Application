// Function to add a professional chart legend
function addChartLegend(symbol, dataSource) {
    const heroChartElement = document.getElementById('heroChart');
    if (!heroChartElement) return;

    // Check if legend already exists and remove it
    const existingLegend = heroChartElement.querySelector('.chart-legend');
    if (existingLegend) {
        existingLegend.remove();
    }

    // Create new legend
    const legend = document.createElement('div');
    legend.className = 'chart-legend';

    // Add symbol info
    const symbolItem = document.createElement('div');
    symbolItem.className = 'legend-item';
    symbolItem.innerHTML = `
        <div class="legend-color" style="background-color: #2962FF;"></div>
        <div class="legend-label">심볼:</div>
        <div class="legend-value">${symbol}</div>
    `;

    // Add source info
    const sourceItem = document.createElement('div');
    sourceItem.className = 'legend-item';
    sourceItem.innerHTML = `
        <i class="fas fa-database" style="margin-right: 6px; color: var(--tv-pro-trust-indicator);"></i>
        <div class="legend-label">데이터:</div>
        <div class="legend-value">${dataSource || 'Yahoo Finance'}</div>
        <div class="verified-badge" style="margin-left: 4px; font-size: 0.7rem;">
            <i class="fas fa-check"></i>
        </div>
    `;

    // Add last update time
    const timeItem = document.createElement('div');
    timeItem.className = 'legend-item';

    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');

    timeItem.innerHTML = `
        <i class="fas fa-clock" style="margin-right: 6px; color: var(--tv-pro-ui-text-secondary);"></i>
        <div class="legend-label">업데이트:</div>
        <div class="legend-value">${hours}:${minutes}:${seconds}</div>
    `;

    // Add items to legend
    legend.appendChild(symbolItem);
    legend.appendChild(sourceItem);
    legend.appendChild(timeItem);

    // Add legend to chart container
    heroChartElement.appendChild(legend);
}
