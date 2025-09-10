/**
 * Mobile-Desktop UI Parity Fix
 * Ensures mobile version has EXACTLY the same design as desktop
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('🎯 Mobile-Desktop Parity: Ensuring identical UI across devices...');

    // Force desktop layout on mobile
    function enforceDesktopLayout() {
        const heroContainer = document.querySelector('.hero-container');
        if (heroContainer && window.innerWidth <= 768) {
            // Maintain side-by-side layout even on mobile
            heroContainer.style.setProperty('display', 'grid', 'important');
            heroContainer.style.setProperty('grid-template-columns', '1fr 1fr', 'important');
            heroContainer.style.setProperty('gap', '20px', 'important');
            heroContainer.style.setProperty('align-items', 'center', 'important');
            heroContainer.style.setProperty('max-width', '1400px', 'important');
            heroContainer.style.setProperty('margin', '0 auto', 'important');
            heroContainer.style.setProperty('padding', '0 15px', 'important');

            console.log('✅ Desktop hero layout enforced on mobile');
        }
    }

    // Maintain desktop text alignment
    function enforceDesktopAlignment() {
        if (window.innerWidth <= 768) {
            const heroContent = document.querySelector('.hero-content');
            if (heroContent) {
                // Keep desktop left alignment
                heroContent.style.setProperty('text-align', 'left', 'important');

                // Apply to child elements
                const textElements = heroContent.querySelectorAll('.hero-title, .hero-description, h1, h2, p');
                textElements.forEach(el => {
                    el.style.setProperty('text-align', 'left', 'important');
                });

                // Align flex containers to start
                const flexElements = heroContent.querySelectorAll('.trust-indicator, .hero-features, .hero-buttons');
                flexElements.forEach(el => {
                    el.style.setProperty('justify-content', 'flex-start', 'important');
                    el.style.setProperty('align-items', 'flex-start', 'important');
                });

                console.log('✅ Desktop text alignment enforced on mobile');
            }
        }
    }

    // Ensure chart stays visible and properly sized
    function enforceChartVisibility() {
        const chartContainers = document.querySelectorAll('.chart-container-hero, #heroChart, .hero-image');
        chartContainers.forEach(container => {
            if (container) {
                container.style.setProperty('display', 'block', 'important');
                container.style.setProperty('visibility', 'visible', 'important');
                container.style.setProperty('opacity', '1', 'important');
                container.style.setProperty('order', '2', 'important');

                // Proper sizing for mobile
                if (window.innerWidth <= 768) {
                    const chartDiv = container.querySelector('.chart-container-hero') || container;
                    if (chartDiv) {
                        chartDiv.style.setProperty('height', '250px', 'important');
                        chartDiv.style.setProperty('width', '100%', 'important');
                    }
                }

                console.log('✅ Chart visibility enforced');
            }
        });
    }

    // Force all content sections to be visible
    function enforceContentVisibility() {
        const allSections = [
            '.hero', '.hero-container', '.hero-content', '.hero-image',
            '.prediction-section', '.features-section', '.pricing-section',
            '.ranking-section', '.chart-section', '.main-chart-section'
        ];

        allSections.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (element) {
                    element.style.setProperty('display', 'block', 'important');
                    element.style.setProperty('visibility', 'visible', 'important');
                    element.style.setProperty('opacity', '1', 'important');
                    element.style.setProperty('position', 'relative', 'important');
                    element.style.setProperty('z-index', '1', 'important');

                    element.removeAttribute('hidden');
                    element.classList.remove('hidden');
                }
            });
        });

        console.log('✅ All content sections forced visible');
    }

    // Inject critical CSS to override any hiding rules
    function injectParityCSS() {
        const style = document.createElement('style');
        style.id = 'mobile-desktop-parity';
        style.textContent = `
            /* Mobile-Desktop UI Parity - Override all hiding rules */
            @media (max-width: 768px) {
                /* Force desktop hero layout */
                .hero-container {
                    display: grid !important;
                    grid-template-columns: 1fr 1fr !important;
                    gap: 20px !important;
                    align-items: center !important;
                    max-width: 1400px !important;
                    margin: 0 auto !important;
                    padding: 0 15px !important;
                }
                
                /* Keep desktop text alignment */
                .hero-content,
                .hero-content .hero-title,
                .hero-content .hero-description,
                .hero-content h1,
                .hero-content h2,
                .hero-content p {
                    text-align: left !important;
                }
                
                /* Keep desktop flex alignment */
                .hero-content .trust-indicator,
                .hero-content .hero-features,
                .hero-content .hero-buttons {
                    justify-content: flex-start !important;
                    align-items: flex-start !important;
                }
                
                /* Ensure chart stays visible */
                .hero-image,
                .chart-container-hero,
                #heroChart {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    order: 2 !important;
                }
                
                /* Force all sections visible */
                .hero,
                .hero-container,
                .hero-content,
                .hero-image,
                .prediction-section,
                .features-section,
                .pricing-section,
                .ranking-section,
                .chart-section,
                .main-chart-section {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    position: relative !important;
                }
            }
        `;

        // Remove existing parity CSS if it exists
        const existing = document.getElementById('mobile-desktop-parity');
        if (existing) existing.remove();

        document.head.appendChild(style);
        console.log('✅ Desktop parity CSS injected');
    }

    // Main execution function
    function enforceDesktopParity() {
        injectParityCSS();
        enforceContentVisibility();
        enforceDesktopLayout();
        enforceDesktopAlignment();
        enforceChartVisibility();

        console.log('🎉 Mobile-Desktop Parity: All desktop UI consistency enforced!');
    }

    // Initial run
    enforceDesktopParity();

    // Re-run on resize
    let resizeTimeout;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function () {
            console.log('🔄 Re-enforcing desktop parity after resize...');
            enforceDesktopParity();
        }, 250);
    });

    // Monitor for DOM changes and re-apply fixes
    const observer = new MutationObserver(function (mutations) {
        let shouldRerun = false;
        mutations.forEach(function (mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                shouldRerun = true;
            }
        });

        if (shouldRerun) {
            setTimeout(enforceDesktopParity, 100);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('📱→🖥️ Mobile-Desktop Parity System: Fully initialized!');
});
