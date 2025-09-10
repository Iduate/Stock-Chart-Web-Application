// This script adds a chart reload button to help when charts don't appear
document.addEventListener('DOMContentLoaded', function () {
    // Wait for app.js to initialize
    setTimeout(() => {
        // Only add if a chart element exists
        const chartElement = document.getElementById('heroChart') || document.getElementById('featuredChart');
        if (!chartElement) return;

        // Create a reload button
        const reloadButton = document.createElement('button');
        reloadButton.className = 'chart-reload-button';
        reloadButton.innerHTML = '<i class="fas fa-sync-alt"></i> Reload Chart';
        reloadButton.style.cssText = `
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1001;
            display: flex;
            align-items: center;
            gap: 6px;
        `;

        // Add click handler
        reloadButton.addEventListener('click', function () {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Reloading...';

            // Call the global force recreate function
            if (typeof window.forceRecreateChart === 'function') {
                window.forceRecreateChart();

                // Re-enable after a delay
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-sync-alt"></i> Reload Chart';
                }, 2000);
            } else {
                console.error('forceRecreateChart function not found');
                this.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
            }
        });

        // Add to chart container
        chartElement.appendChild(reloadButton);
    }, 1000);
});
