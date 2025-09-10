// Mobile Content Display Fix
// This script ensures all content sections are visible on mobile devices

document.addEventListener('DOMContentLoaded', function () {
    // Wait a bit for other scripts to load
    setTimeout(function () {
        fixMobileContentDisplay();
    }, 500);

    // Also run on window load
    window.addEventListener('load', function () {
        setTimeout(fixMobileContentDisplay, 300);
    });
});

function fixMobileContentDisplay() {
    const isMobile = window.innerWidth <= 768;

    if (!isMobile) return;

    console.log('🔧 Applying mobile content display fixes...');

    // Force display of main content sections
    const sections = [
        '.main-chart-section',
        '.features-section',
        '.market-data',
        'section[id="market-data"]',
        '.cta-section',
        '.footer',
        'main',
        '.main-content'
    ];

    sections.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            if (element) {
                // Force visibility
                element.style.display = 'block';
                element.style.visibility = 'visible';
                element.style.opacity = '1';
                element.style.position = 'relative';
                element.style.zIndex = '1';
                element.style.clear = 'both';

                // Ensure no hidden overflow
                element.style.overflow = 'visible';

                // Ensure proper mobile padding
                if (!element.style.padding || element.style.padding === '0px') {
                    element.style.padding = '40px 0';
                }
            }
        });
    });

    // Fix hero section height on mobile
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        heroSection.style.minHeight = '70vh';
        heroSection.style.maxHeight = '80vh';
        heroSection.style.padding = '100px 0 60px';

        // Ensure hero background elements are behind content
        const heroBackground = heroSection.querySelector('.hero-background');
        const heroGradient = heroSection.querySelector('.hero-gradient');
        const heroParticles = heroSection.querySelector('.hero-particles');

        if (heroBackground) heroBackground.style.zIndex = '-1';
        if (heroGradient) heroGradient.style.zIndex = '-1';
        if (heroParticles) heroParticles.style.zIndex = '-1';

        // Ensure hero container is properly positioned
        const heroContainer = heroSection.querySelector('.hero-container');
        if (heroContainer) {
            heroContainer.style.position = 'relative';
            heroContainer.style.zIndex = '2';
            heroContainer.style.display = 'flex';
            heroContainer.style.flexDirection = 'column';
            heroContainer.style.alignItems = 'center';
            heroContainer.style.textAlign = 'center';
        }
    }

    // Fix chart container on mobile
    const chartContainers = document.querySelectorAll('#heroChart, .chart-preview, .chart-container-hero');
    chartContainers.forEach(container => {
        if (container) {
            container.style.width = '100%';
            container.style.minHeight = '300px';
            container.style.maxHeight = '400px';
            container.style.position = 'relative';
            container.style.overflow = 'hidden';
            container.style.display = 'block';
            container.style.visibility = 'visible';
        }
    });

    // Ensure containers don't overflow viewport
    const containers = document.querySelectorAll('.container');
    containers.forEach(container => {
        if (container) {
            container.style.maxWidth = '100%';
            container.style.paddingLeft = '20px';
            container.style.paddingRight = '20px';
            container.style.overflowX = 'hidden';
        }
    });

    // Fix section headers visibility
    const sectionHeaders = document.querySelectorAll('.section-header');
    sectionHeaders.forEach(header => {
        if (header) {
            header.style.display = 'block';
            header.style.textAlign = 'center';
            header.style.padding = '20px 0';
            header.style.marginBottom = '30px';
        }
    });

    // Fix market data section specifically  
    const marketDataSection = document.querySelector('.market-data') || document.querySelector('#market-data');
    if (marketDataSection) {
        marketDataSection.style.display = 'block';
        marketDataSection.style.visibility = 'visible';
        marketDataSection.style.opacity = '1';
        marketDataSection.style.backgroundColor = '#f8f9fa';
        marketDataSection.style.minHeight = '400px';
        marketDataSection.style.padding = '40px 0';
        marketDataSection.style.position = 'relative';
        marketDataSection.style.zIndex = '1';

        console.log('✅ Market data section fixed');
    }

    // Fix features section
    const featuresSection = document.querySelector('.features-section');
    if (featuresSection) {
        featuresSection.style.display = 'block';
        featuresSection.style.visibility = 'visible';
        featuresSection.style.opacity = '1';
        featuresSection.style.backgroundColor = '#fafafa';
        featuresSection.style.borderTop = '1px solid #ddd';
        featuresSection.style.padding = '40px 0';
        featuresSection.style.position = 'relative';
        featuresSection.style.zIndex = '1';

        // Fix features grid
        const featuresGrid = featuresSection.querySelector('.features-grid');
        if (featuresGrid) {
            featuresGrid.style.display = 'grid';
            featuresGrid.style.gridTemplateColumns = '1fr';
            featuresGrid.style.gap = '20px';
        }

        console.log('✅ Features section fixed');
    }

    // Fix CTA section
    const ctaSection = document.querySelector('.cta-section');
    if (ctaSection) {
        ctaSection.style.display = 'block';
        ctaSection.style.visibility = 'visible';
        ctaSection.style.opacity = '1';
        ctaSection.style.backgroundColor = '#2962FF';
        ctaSection.style.color = 'white';
        ctaSection.style.padding = '60px 0';
        ctaSection.style.textAlign = 'center';
        ctaSection.style.position = 'relative';
        ctaSection.style.zIndex = '1';

        console.log('✅ CTA section fixed');
    }

    // Fix footer
    const footer = document.querySelector('.footer');
    if (footer) {
        footer.style.display = 'block';
        footer.style.visibility = 'visible';
        footer.style.opacity = '1';
        footer.style.backgroundColor = '#333';
        footer.style.color = 'white';
        footer.style.padding = '40px 0 20px';
        footer.style.position = 'relative';
        footer.style.zIndex = '1';

        console.log('✅ Footer fixed');
    }

    // Scroll to top to ensure user can see the content
    window.scrollTo(0, 0);

    console.log('✅ Mobile content display fixes applied');

    // Debug: Log all main sections
    const allSections = document.querySelectorAll('section, main, .section');
    console.log(`📊 Found ${allSections.length} main sections on page`);
    allSections.forEach((section, index) => {
        const rect = section.getBoundingClientRect();
        const isVisible = rect.height > 0 && getComputedStyle(section).visibility !== 'hidden';
        console.log(`Section ${index + 1}:`, {
            className: section.className,
            id: section.id,
            height: rect.height,
            visible: isVisible,
            display: getComputedStyle(section).display
        });
    });
}

// Run fix on resize as well
let resizeTimeout;
window.addEventListener('resize', function () {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function () {
        if (window.innerWidth <= 768) {
            fixMobileContentDisplay();
        }
    }, 300);
});

// Export for manual testing
window.fixMobileContentDisplay = fixMobileContentDisplay;
