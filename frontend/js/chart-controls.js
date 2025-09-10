// Chart Controls JavaScript
// Handles all chart control elements like timeframes and feature buttons

// Prevent multiple initialization
if (typeof window.chartControlsInitialized !== 'undefined') {
    console.log('Chart controls already initialized, skipping...');
} else {
    window.chartControlsInitialized = true;

    // Translation dictionary for multilingual support
    let translations = {};
    if (typeof window.chartControlTranslations === 'undefined') {
        window.chartControlTranslations = {
            'en': {
                'characteristic': 'characteristic',
                'equipment': 'equipment'
            },
            'ko': {
                'characteristic': '특성',
                'equipment': '장비'
            }
        };
    }
    translations = window.chartControlTranslations;

    // Get current language (default to Korean)
    if (typeof window.chartCurrentLanguage === 'undefined') {
        window.chartCurrentLanguage = 'ko';
    }
    let currentLanguage = window.chartCurrentLanguage;

    document.addEventListener('DOMContentLoaded', function () {
        console.log('Chart controls initialized');

        // Detect language from HTML lang attribute or localStorage
        const htmlLang = document.documentElement.lang;
        if (htmlLang) {
            currentLanguage = htmlLang.substring(0, 2); // Extract language code
        }
        console.log('Using language:', currentLanguage);

        // Initialize timeframe buttons
        initTimeframeButtons();

        // Initialize feature buttons and translate labels
        initFeatureButtons();

        // Apply translations to existing buttons
        translateButtons();
    });

    /**
     * Initialize the timeframe buttons (1D, 1W, 1M, 3M, 1Y, ALL)
     */
    function initTimeframeButtons() {
        const timeframeButtons = document.querySelectorAll('.btn-timeframe, [class*="1D"], [class*="1W"], [class*="1M"], [class*="3M"], [class*="1Y"], [class*="ALL"]');

        if (timeframeButtons.length > 0) {
            console.log('Found timeframe buttons:', timeframeButtons.length);

            timeframeButtons.forEach(button => {
                button.addEventListener('click', function () {
                    // Remove active class from all buttons
                    timeframeButtons.forEach(btn => btn.classList.remove('active'));

                    // Add active class to clicked button
                    this.classList.add('active');

                    // Get the timeframe value from button text or data attribute
                    const timeframe = this.dataset.timeframe || this.textContent.trim();
                    console.log('Selected timeframe:', timeframe);

                    // Update chart with selected timeframe
                    updateChartTimeframe(timeframe);
                });
            });
        } else {
            console.warn('No timeframe buttons found');
        }
    }

    /**
     * Initialize feature buttons (characteristic, equipment, etc.)
     */
    function initFeatureButtons() {
        const featureButtons = document.querySelectorAll('[class*="characteristic"], [class*="equipment"]');

        if (featureButtons.length > 0) {
            console.log('Found feature buttons:', featureButtons.length);

            featureButtons.forEach(button => {
                button.addEventListener('click', function () {
                    // Toggle active state for feature buttons
                    this.classList.toggle('active');

                    // Get the feature name from button data or content
                    const feature = this.dataset.feature || this.textContent.trim();
                    console.log('Toggled feature:', feature);

                    // Update chart with selected feature
                    toggleChartFeature(feature);
                });
            });
        } else {
            console.warn('No feature buttons found');
        }
    }

    /**
     * Update chart based on selected timeframe
     * @param {string} timeframe - The selected timeframe (1D, 1W, etc.)
     */
    function updateChartTimeframe(timeframe) {
        // Find active chart instance
        const chart = window.activeChart || window.heroChart || window.tradingViewChart;

        if (!chart) {
            console.warn('No active chart found');
            return;
        }

        // Set timeframe ranges based on selection
        let range = {};
        const now = new Date();

        switch (timeframe) {
            case '1D':
                range = { from: new Date(now.setHours(0, 0, 0, 0)).getTime() / 1000, to: now.getTime() / 1000 };
                break;
            case '1W':
                range = { from: new Date(now.setDate(now.getDate() - 7)).getTime() / 1000, to: new Date().getTime() / 1000 };
                break;
            case '1M':
                range = { from: new Date(now.setMonth(now.getMonth() - 1)).getTime() / 1000, to: new Date().getTime() / 1000 };
                break;
            case '3M':
                range = { from: new Date(now.setMonth(now.getMonth() - 3)).getTime() / 1000, to: new Date().getTime() / 1000 };
                break;
            case '1Y':
                range = { from: new Date(now.setFullYear(now.getFullYear() - 1)).getTime() / 1000, to: new Date().getTime() / 1000 };
                break;
            case 'ALL':
                // Let the chart show all available data
                chart.timeScale().fitContent();
                return;
        }

        // Apply the range to the chart
        chart.timeScale().setVisibleRange(range);
    }

    /**
     * Toggle chart feature visualization
     * @param {string} feature - The feature name (characteristic, equipment, etc.)
     */
    function toggleChartFeature(feature) {
        // Find active chart instance
        const chart = window.activeChart || window.heroChart || window.tradingViewChart;

        if (!chart) {
            console.warn('No active chart found');
            return;
        }

        // Handle different features
        switch (feature.toLowerCase()) {
            case 'characteristic':
                toggleCharacteristicIndicators(chart);
                break;
            case 'equipment':
                toggleEquipmentIndicators(chart);
                break;
            default:
                console.warn('Unknown feature:', feature);
        }
    }

    /**
     * Toggle characteristic indicators on the chart
     * @param {object} chart - The chart instance
     */
    function toggleCharacteristicIndicators(chart) {
        // Implementation for characteristic indicators
        console.log('Toggling characteristic indicators');

        // Example: Toggle visibility of a specific series or indicator
        if (window.characteristicSeries) {
            const isVisible = window.characteristicSeries.options().visible;
            window.characteristicSeries.applyOptions({ visible: !isVisible });
        } else {
            // Create characteristic indicators if they don't exist
            createCharacteristicIndicators(chart);
        }
    }

    /**
     * Toggle equipment indicators on the chart
     * @param {object} chart - The chart instance
     */
    function toggleEquipmentIndicators(chart) {
        // Implementation for equipment indicators
        console.log('Toggling equipment indicators');

        // Example: Toggle visibility of a specific series or indicator
        if (window.equipmentSeries) {
            const isVisible = window.equipmentSeries.options().visible;
            window.equipmentSeries.applyOptions({ visible: !isVisible });
        } else {
            // Create equipment indicators if they don't exist
            createEquipmentIndicators(chart);
        }
    }

    /**
     * Create characteristic indicators on the chart
     * @param {object} chart - The chart instance
     */
    function createCharacteristicIndicators(chart) {
        // Example implementation - create a new marker series for characteristics
        window.characteristicSeries = chart.addLineSeries({
            color: '#2962FF',
            lineWidth: 1,
            lineStyle: 2, // Dashed
            title: 'Characteristic',
            visible: true
        });

        // Add some sample data (would be replaced with real data in production)
        const characteristicData = getSampleCharacteristicData();
        window.characteristicSeries.setData(characteristicData);
    }

    /**
     * Create equipment indicators on the chart
     * @param {object} chart - The chart instance
     */
    function createEquipmentIndicators(chart) {
        // Example implementation - create a new marker series for equipment
        window.equipmentSeries = chart.addLineSeries({
            color: '#FF6D00',
            lineWidth: 1,
            lineStyle: 2, // Dashed
            title: 'Equipment',
            visible: true
        });

        // Add some sample data (would be replaced with real data in production)
        const equipmentData = getSampleEquipmentData();
        window.equipmentSeries.setData(equipmentData);
    }

    /**
     * Get sample data for characteristic indicators
     * @returns {Array} Array of data points
     */
    function getSampleCharacteristicData() {
        // In a real app, this would fetch from an API
        // For now, return some sample data
        return [
            { time: '2023-09-01', value: 100 },
            { time: '2023-09-02', value: 102 },
            { time: '2023-09-03', value: 104 },
            { time: '2023-09-04', value: 103 },
            { time: '2023-09-05', value: 105 }
        ];
    }

    /**
     * Get sample data for equipment indicators
     * @returns {Array} Array of data points
     */
    function getSampleEquipmentData() {
        // In a real app, this would fetch from an API
        // For now, return some sample data
        return [
            { time: '2023-09-01', value: 95 },
            { time: '2023-09-02', value: 96 },
            { time: '2023-09-03', value: 98 },
            { time: '2023-09-04', value: 99 },
            { time: '2023-09-05', value: 97 }
        ];
    }

    /**
     * Translate a text based on current language
     * @param {string} key - The text key to translate
     * @returns {string} Translated text
     */
    function translate(key) {
        // Get the translation for the current language, or fallback to English, or use the key itself
        return (translations[currentLanguage] && translations[currentLanguage][key]) ||
            (translations['en'] && translations['en'][key]) ||
            key;
    }

    /**
     * Translate all feature buttons to current language
     */
    function translateButtons() {
        // Find all feature buttons
        const featureButtons = document.querySelectorAll('[data-feature]');

        featureButtons.forEach(button => {
            const feature = button.getAttribute('data-feature');
            if (feature) {
                // Get the text node (skip the icon element)
                const textNodes = Array.from(button.childNodes).filter(node =>
                    node.nodeType === Node.TEXT_NODE ||
                    (node.nodeType === Node.ELEMENT_NODE && !node.classList.contains('fas'))
                );

                // If we found text nodes or non-icon elements, update their content
                if (textNodes.length > 0) {
                    // Update the last text node or element
                    const lastNode = textNodes[textNodes.length - 1];
                    if (lastNode.nodeType === Node.TEXT_NODE) {
                        lastNode.nodeValue = translate(feature);
                    } else {
                        lastNode.textContent = translate(feature);
                    }
                } else {
                    // If no text nodes found, append a new one
                    button.appendChild(document.createTextNode(translate(feature)));
                }
            }
        });
    }

} // End of initialization guard
