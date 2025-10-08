/**
 * Collapsible Sidebar Manager
 * Provides functionality to collapse/expand both left sidebar and right trading panel
 */

class CollapsibleSidebar {
    constructor() {
        this.container = document.querySelector('.figma-container');
        this.leftSidebar = document.querySelector('.figma-sidebar');
        this.rightPanel = document.querySelector('.figma-trading-panel');
        
        this.isLeftCollapsed = false;
        this.isRightCollapsed = false;
        
        this.init();
    }
    
    init() {
        this.createToggleButtons();
        this.bindEvents();
        this.loadSavedState();
    }
    
    createToggleButtons() {
        // Create left sidebar toggle button
        if (this.leftSidebar) {
            const leftToggle = document.createElement('button');
            leftToggle.className = 'toggle-btn sidebar-toggle';
            leftToggle.innerHTML = '<i class="fas fa-chevron-left"></i>';
            leftToggle.title = '사이드바 접기/펼치기';
            this.leftSidebar.appendChild(leftToggle);
        }
        
        // Create right panel toggle button
        if (this.rightPanel) {
            const rightToggle = document.createElement('button');
            rightToggle.className = 'toggle-btn trading-panel-toggle';
            rightToggle.innerHTML = '<i class="fas fa-chevron-right"></i>';
            rightToggle.title = '트레이딩 패널 접기/펼치기';
            this.rightPanel.appendChild(rightToggle);
        }
    }
    
    bindEvents() {
        // Left sidebar toggle
        const leftToggle = document.querySelector('.sidebar-toggle');
        if (leftToggle) {
            leftToggle.addEventListener('click', () => this.toggleLeftSidebar());
        }
        
        // Right panel toggle
        const rightToggle = document.querySelector('.trading-panel-toggle');
        if (rightToggle) {
            rightToggle.addEventListener('click', () => this.toggleRightPanel());
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl + [ to toggle left sidebar
            if (e.ctrlKey && e.key === '[') {
                e.preventDefault();
                this.toggleLeftSidebar();
            }
            
            // Ctrl + ] to toggle right panel
            if (e.ctrlKey && e.key === ']') {
                e.preventDefault();
                this.toggleRightPanel();
            }
        });
    }
    
    toggleLeftSidebar() {
        this.isLeftCollapsed = !this.isLeftCollapsed;
        
        if (this.isLeftCollapsed) {
            this.leftSidebar.classList.add('collapsed');
        } else {
            this.leftSidebar.classList.remove('collapsed');
        }
        
        this.updateContainerState();
        this.updateToggleIcon('left');
        this.saveState();
    }
    
    toggleRightPanel() {
        this.isRightCollapsed = !this.isRightCollapsed;
        
        if (this.isRightCollapsed) {
            this.rightPanel.classList.add('collapsed');
        } else {
            this.rightPanel.classList.remove('collapsed');
        }
        
        this.updateContainerState();
        this.updateToggleIcon('right');
        this.saveState();
    }
    
    updateContainerState() {
        // Remove all collapse classes
        this.container.classList.remove('left-collapsed', 'right-collapsed', 'both-collapsed');
        
        // Add appropriate classes based on state
        if (this.isLeftCollapsed && this.isRightCollapsed) {
            this.container.classList.add('both-collapsed');
        } else if (this.isLeftCollapsed) {
            this.container.classList.add('left-collapsed');
        } else if (this.isRightCollapsed) {
            this.container.classList.add('right-collapsed');
        }
    }
    
    updateToggleIcon(side) {
        if (side === 'left') {
            const leftToggle = document.querySelector('.sidebar-toggle i');
            if (leftToggle) {
                leftToggle.className = this.isLeftCollapsed ? 
                    'fas fa-chevron-right' : 'fas fa-chevron-left';
            }
        } else if (side === 'right') {
            const rightToggle = document.querySelector('.trading-panel-toggle i');
            if (rightToggle) {
                rightToggle.className = this.isRightCollapsed ? 
                    'fas fa-chevron-left' : 'fas fa-chevron-right';
            }
        }
    }
    
    saveState() {
        localStorage.setItem('sidebarState', JSON.stringify({
            leftCollapsed: this.isLeftCollapsed,
            rightCollapsed: this.isRightCollapsed
        }));
    }
    
    loadSavedState() {
        try {
            const savedState = localStorage.getItem('sidebarState');
            if (savedState) {
                const state = JSON.parse(savedState);
                
                if (state.leftCollapsed) {
                    this.toggleLeftSidebar();
                }
                
                if (state.rightCollapsed) {
                    this.toggleRightPanel();
                }
            }
        } catch (error) {
            console.warn('Could not load sidebar state:', error);
        }
    }
    
    // Public methods for external control
    collapseLeft() {
        if (!this.isLeftCollapsed) {
            this.toggleLeftSidebar();
        }
    }
    
    expandLeft() {
        if (this.isLeftCollapsed) {
            this.toggleLeftSidebar();
        }
    }
    
    collapseRight() {
        if (!this.isRightCollapsed) {
            this.toggleRightPanel();
        }
    }
    
    expandRight() {
        if (this.isRightCollapsed) {
            this.toggleRightPanel();
        }
    }
    
    collapseAll() {
        this.collapseLeft();
        this.collapseRight();
    }
    
    expandAll() {
        this.expandLeft();
        this.expandRight();
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.collapsibleSidebar = new CollapsibleSidebar();
});

// Responsive behavior - auto-collapse on small screens
window.addEventListener('resize', () => {
    if (window.collapsibleSidebar) {
        const width = window.innerWidth;
        
        // Auto-collapse on tablet and mobile
        if (width <= 1024) {
            window.collapsibleSidebar.collapseAll();
        } else if (width >= 1200) {
            // Auto-expand on large screens if user hasn't manually collapsed
            const savedState = localStorage.getItem('sidebarState');
            if (!savedState) {
                window.collapsibleSidebar.expandAll();
            }
        }
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CollapsibleSidebar;
}