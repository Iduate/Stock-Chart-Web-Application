/**
 * Notification system for user feedback
 */

// Show a notification toast
function showNotification(title, message, type = 'info') {
    // Make sure this function is available globally
    window.showNotification = showNotification;
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    // Add title if provided
    if (title) {
        const titleEl = document.createElement('h4');
        titleEl.className = 'notification-title';
        titleEl.textContent = title;
        notification.appendChild(titleEl);
    }

    // Add message
    const messageEl = document.createElement('p');
    messageEl.className = 'notification-message';
    messageEl.textContent = message;
    notification.appendChild(messageEl);

    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'notification-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = function () {
        container.removeChild(notification);
    };
    notification.appendChild(closeBtn);

    // Add to container
    container.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode === container) {
            container.removeChild(notification);
        }
    }, 5000);
}

// Add CSS styles for notifications
document.addEventListener('DOMContentLoaded', () => {
    // Create style element
    const style = document.createElement('style');
    style.textContent = `
        .notification-container {
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }
        
        .notification {
            background-color: #333;
            color: white;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.4);
            margin-bottom: 15px;
            padding: 18px 25px;
            width: 350px;
            position: relative;
            animation: notification-in 0.5s ease-out forwards;
            opacity: 0.95;
        }
        
        .notification-title {
            margin: 0 0 8px 0;
            font-size: 18px;
            font-weight: bold;
        }
        
        .notification-message {
            margin: 0;
            font-size: 16px;
            line-height: 1.4;
        }
        
        .notification-close {
            position: absolute;
            top: 10px;
            right: 15px;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 22px;
            color: white;
            opacity: 0.8;
            transition: opacity 0.2s;
        }
        
        .notification-close:hover {
            opacity: 1;
        }
        
        .notification-info {
            border-left: 6px solid #2196F3;
            background: linear-gradient(to right, #1e3c72, #2a5298);
        }
        
        .notification-success {
            border-left: 6px solid #4CAF50;
            background: linear-gradient(to right, #134e5e, #71b280);
        }
        
        .notification-warning {
            border-left: 6px solid #FF9800;
            background: linear-gradient(to right, #ff8008, #ffc837);
            color: #333;
        }
        
        .notification-error {
            border-left: 6px solid #F44336;
            background: linear-gradient(to right, #cb2d3e, #ef473a);
        }
        
        @keyframes notification-in {
            0% {
                transform: translateX(100%);
                opacity: 0;
            }
            50% {
                transform: translateX(-10px);
            }
            100% {
                transform: translateX(0);
                opacity: 0.95;
            }
        }
        
        /* Add a subtle pulse effect for important notifications */
        @keyframes notification-pulse {
            0% { box-shadow: 0 5px 15px rgba(0,0,0,0.4); }
            50% { box-shadow: 0 5px 25px rgba(0,0,0,0.6); }
            100% { box-shadow: 0 5px 15px rgba(0,0,0,0.4); }
        }
        
        .notification-error, .notification-warning {
            animation: notification-in 0.5s ease-out forwards, notification-pulse 2s infinite;
        }
    `;

    document.head.appendChild(style);
});
