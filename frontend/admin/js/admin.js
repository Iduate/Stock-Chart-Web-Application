// Admin Dashboard JavaScript - TradingView Style
document.addEventListener('DOMContentLoaded', function () {
    // Initialize dashboard
    initDashboard();
    setupEventListeners();
    loadDashboardData();
});

// Dashboard initialization
function initDashboard() {
    // Set default active section
    showSection('dashboard');

    // Initialize charts
    initCharts();
}

// Event listeners setup
function setupEventListeners() {
    // Sidebar toggle for mobile
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

// Section management
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.admin-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
        const link = item.querySelector('a');
        if (link && link.getAttribute('href') === '#' + sectionId) {
            item.classList.add('active');
        }
    });

    // Update page title
    const pageTitle = document.getElementById('pageTitle');
    const sectionTitles = {
        'dashboard': '대시보드',
        'users': '사용자 관리',
        'predictions': '예측 관리',
        'payments': '결제 관리',
        'stocks': '종목 관리',
        'events': '이벤트 관리',
        'analytics': '분석',
        'settings': '설정'
    };

    if (pageTitle && sectionTitles[sectionId]) {
        pageTitle.textContent = sectionTitles[sectionId];
    }
}

// Sidebar toggle for mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.admin-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// Charts initialization
function initCharts() {
    // User Registration Chart
    const userChartCtx = document.getElementById('userRegistrationChart');
    if (userChartCtx) {
        new Chart(userChartCtx, {
            type: 'line',
            data: {
                labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                datasets: [{
                    label: '신규 사용자',
                    data: [120, 150, 180, 220, 280, 340],
                    borderColor: '#2962FF',
                    backgroundColor: 'rgba(41, 98, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#d1d4dc'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#868993'
                        },
                        grid: {
                            color: '#2a2e39'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#868993'
                        },
                        grid: {
                            color: '#2a2e39'
                        }
                    }
                }
            }
        });
    }

    // Prediction Chart
    const predictionChartCtx = document.getElementById('predictionChart');
    if (predictionChartCtx) {
        new Chart(predictionChartCtx, {
            type: 'bar',
            data: {
                labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                datasets: [{
                    label: '예측 생성',
                    data: [450, 520, 680, 750, 820, 950],
                    backgroundColor: '#26a69a',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#d1d4dc'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#868993'
                        },
                        grid: {
                            color: '#2a2e39'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#868993'
                        },
                        grid: {
                            color: '#2a2e39'
                        }
                    }
                }
            }
        });
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Update header stats
        updateHeaderStats();

        // Load recent activities
        loadRecentActivities();

        // Refresh data every 30 seconds
        setTimeout(loadDashboardData, 30000);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update header statistics
function updateHeaderStats() {
    // Simulate API data
    const stats = {
        totalUsers: Math.floor(Math.random() * 100) + 1200,
        activePredictions: Math.floor(Math.random() * 50) + 150,
        todayRevenue: '₩' + (Math.floor(Math.random() * 500000) + 500000).toLocaleString()
    };

    // Update DOM elements
    const totalUsersEl = document.getElementById('totalUsers');
    const activePredictionsEl = document.getElementById('activePredictions');
    const todayRevenueEl = document.getElementById('todayRevenue');

    if (totalUsersEl) totalUsersEl.textContent = stats.totalUsers;
    if (activePredictionsEl) activePredictionsEl.textContent = stats.activePredictions;
    if (todayRevenueEl) todayRevenueEl.textContent = stats.todayRevenue;
}

// Load recent activities
function loadRecentActivities() {
    const activities = [
        {
            icon: 'fas fa-user-plus',
            text: '새로운 사용자가 가입했습니다',
            time: '2분 전'
        },
        {
            icon: 'fas fa-chart-line',
            text: 'AAPL 예측이 생성되었습니다',
            time: '5분 전'
        },
        {
            icon: 'fas fa-credit-card',
            text: '프리미엄 결제가 완료되었습니다',
            time: '10분 전'
        }
    ];

    const activitiesContainer = document.getElementById('recentActivities');
    if (activitiesContainer) {
        activitiesContainer.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <p>${activity.text}</p>
                    <small>${activity.time}</small>
                </div>
            </div>
        `).join('');
    }
}

// Form submission handler
function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '저장 중...';
    submitBtn.disabled = true;

    // Simulate API call
    setTimeout(() => {
        // Reset button
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

        // Show success message
        showNotification('설정이 성공적으로 저장되었습니다.', 'success');
    }, 1000);
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '16px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '9999',
        transform: 'translateX(300px)',
        transition: 'transform 0.3s ease'
    });

    // Set color based on type
    const colors = {
        success: '#26a69a',
        error: '#ef5350',
        warning: '#ff9800',
        info: '#2962FF'
    };
    notification.style.background = colors[type] || colors.info;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(300px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Logout function
function logout() {
    if (confirm('정말 로그아웃하시겠습니까?')) {
    window.location.href = '../index.html';
    }
}

// Export functions for global access
window.showSection = showSection;
window.toggleSidebar = toggleSidebar;
window.logout = logout;
