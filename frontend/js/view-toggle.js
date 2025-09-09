// Chart view toggle functionality
// This script handles the toggle between grid and list views in the charts page

document.addEventListener('DOMContentLoaded', function () {
    console.log('View toggle functionality initialized');

    // Find the view toggle buttons
    const viewButtons = document.querySelectorAll('.view-btn');
    const chartsGrid = document.getElementById('chartsGrid');

    if (viewButtons.length && chartsGrid) {
        console.log('Found view buttons and charts grid');

        // Initialize view from localStorage if available
        const savedView = localStorage.getItem('chartView') || 'grid';
        setActiveView(savedView, viewButtons, chartsGrid);

        // Add click event listeners to view toggle buttons
        viewButtons.forEach(button => {
            button.addEventListener('click', function () {
                const view = this.getAttribute('data-view');
                console.log('Switching to view:', view);

                // Update active button
                viewButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                // Update grid view
                setActiveView(view, viewButtons, chartsGrid);

                // Save preference to localStorage
                localStorage.setItem('chartView', view);
            });
        });
    } else {
        console.warn('View buttons or charts grid not found');
    }
});

/**
 * Sets the active view (grid or list)
 * @param {string} view - The view type ('grid' or 'list')
 * @param {NodeList} buttons - The view toggle buttons
 * @param {HTMLElement} chartsGrid - The charts grid container
 */
function setActiveView(view, buttons, chartsGrid) {
    // Update buttons
    buttons.forEach(btn => {
        if (btn.getAttribute('data-view') === view) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update grid container class
    chartsGrid.classList.remove('grid-view', 'list-view');
    chartsGrid.classList.add(`${view}-view`);

    // Update chart cards for appropriate layout
    const chartCards = chartsGrid.querySelectorAll('.chart-card');
    if (view === 'list') {
        chartCards.forEach(card => {
            card.classList.add('list-layout');
        });
    } else {
        chartCards.forEach(card => {
            card.classList.remove('list-layout');
        });
    }
}
