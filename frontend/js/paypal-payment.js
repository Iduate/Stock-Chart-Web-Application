/**
 * PayPal Payment Integration
 */

// Initialize PayPal SDK
function initPayPalSDK() {
    // Load PayPal JavaScript SDK
    const script = document.createElement('script');
    script.src = 'https://www.paypal.com/sdk/js?client-id=AWKycg751iEUFo55mqSGSxf802qz3izpCn-9nXnTOC05WQy-Gsoqc15JkLdAfxPcPOxe1AWKn0m2ZtGO&currency=USD';
    script.async = true;
    document.head.appendChild(script);

    // Initialize buttons when SDK is loaded
    script.onload = () => {
        // Find all PayPal button containers
        document.querySelectorAll('.paypal-button-container').forEach(container => {
            const planId = container.getAttribute('data-plan-id');
            const planPrice = container.getAttribute('data-plan-price');
            const planCurrency = container.getAttribute('data-currency') || 'USD';

            // Initialize PayPal button for this container
            initPayPalButton(container, planId, planPrice, planCurrency);
        });
    };
}

// Initialize a PayPal button for a specific plan
function initPayPalButton(container, planId, planPrice, currency) {
    paypal.Buttons({
        style: {
            color: 'blue',
            shape: 'rect',
            label: 'pay',
            height: 40
        },

        // Create order
        createOrder: function (data, actions) {
            return fetch('/api/payments/payments/create-paypal-order/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + (localStorage.getItem('token') || '')
                },
                body: JSON.stringify({
                    plan_id: planId,
                    currency: currency
                })
            })
                .then(response => response.json())
                .then(data => {
                    // Return the order ID
                    return data.order_id;
                });
        },

        // Order approved
        onApprove: function (data, actions) {
            // Show loading message
            showNotification('처리 중', '결제를 처리 중입니다...', 'info');

            // Capture the payment
            return fetch('/api/payments/payments/capture-paypal-payment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + (localStorage.getItem('token') || '')
                },
                body: JSON.stringify({
                    order_id: data.orderID
                })
            })
                .then(response => response.json())
                .then(data => {
                    // Payment successful
                    if (data.status === 'completed') {
                        showNotification('결제 완료', '구독이 성공적으로 활성화되었습니다!', 'success');

                        // Redirect to success page or update UI
                        setTimeout(() => {
                            window.location.href = '/payment-success.html';
                        }, 2000);
                    } else {
                        showNotification('결제 실패', '결제 처리 중 문제가 발생했습니다.', 'error');
                    }
                });
        },

        // Error handling
        onError: function (err) {
            console.error('PayPal error:', err);
            showNotification('결제 오류', '결제 처리 중 오류가 발생했습니다.', 'error');
        }
    }).render(container);
}

// Helper function to display notifications
function showPaymentNotification(title, message, type) {
    // Check if we have a notification system
    if (typeof showNotification === 'function') {
        showNotification(title, message, type);
    } else {
        alert(`${title}: ${message}`);
    }
}

// Initialize PayPal when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on subscription page
    if (document.querySelector('.subscription-section')) {
        initPayPalSDK();
    }
});
