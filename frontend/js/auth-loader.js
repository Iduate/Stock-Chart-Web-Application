/**
 * Script to ensure Google Sign-In is properly loaded at the start
 */
document.addEventListener('DOMContentLoaded', function () {
    console.log('Document loaded, initializing auth systems...');

    // Make sure the notification system is initialized
    if (typeof showNotification !== 'function') {
        console.warn('Notification system not loaded, creating fallback');
        window.showNotification = function (title, message) {
            alert(title + ': ' + message);
        };
    }

    // Pre-load Google Auth API
    if (typeof initGoogleAuth === 'function') {
        setTimeout(function () {
            console.log('Pre-loading Google Auth...');
            initGoogleAuth();
        }, 1000); // Slight delay to ensure other scripts are loaded
    }
});
