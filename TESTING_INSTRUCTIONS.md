# Testing the Access Limit System

This guide explains how to test the newly implemented access limit system for the Stock Chart Web Application.

## Features Implemented

1. **Visit Tracking System**:
   - Anonymous users are limited to 3 visits to premium content
   - Free registered users are limited to 3 visits to premium content
   - Paid users have unlimited access

2. **Automatic Chart Publication**:
   - All user predictions are automatically published on the public chart board
   - Visibility is controlled based on user access level

3. **Automatic Accuracy Calculation**:
   - Predictions are automatically compared with actual market data when the target date passes
   - User accuracy ratings are updated automatically

## Testing Instructions

### 1. Anonymous User Access Limits

1. Open an incognito/private browser window (to ensure no existing session)
2. Navigate to the site and visit premium content pages:
   - `/charts.html`
   - `/prediction.html`
   - `/ranking.html`
3. After 3 visits to these pages, you should be redirected to the subscription page
4. The subscription page should show a warning about reaching the free access limit

### 2. Free Registered User Access Limits

1. Create a new user account or use an existing free account
2. Log in and visit premium content pages
3. After 3 visits, you should see a payment prompt
4. Try accessing additional premium content and verify you're redirected to subscription

### 3. Paid User Unlimited Access

1. Log in as a paid user (or modify a user's type to 'paid' in the admin panel)
2. Verify you can access all premium content without restrictions
3. No limit warnings should appear

### 4. Chart Prediction Publishing

1. Log in as any user
2. Create a new prediction (select stock, future date, price)
3. Verify the prediction appears on the public chart board automatically

### 5. Automatic Accuracy Calculation

1. Create a prediction with a target date in the past
2. Run the update command: `python manage.py update_predictions`
3. Check that the prediction status changes to 'completed'
4. Verify accuracy and profit calculations are performed

### Admin Testing Tools

1. **Reset Visit Counter**: 
   - For admin users, use the `/api/users/reset-free-visits/` endpoint to reset counters
   - This allows for repeated testing of the limit system

2. **Update Predictions Manually**:
   - Run `python manage.py update_predictions` to manually trigger updates
   - Check prediction status changes and accuracy calculations

## Known Limitations

1. Session-based tracking is used for anonymous users, which means:
   - Clearing cookies/cache will reset the counter for anonymous users
   - Different browsers or devices will have separate counters

2. The system assumes market data is available for all prediction target dates:
   - If market data is unavailable, accuracy calculations will be skipped

## Troubleshooting

If you encounter issues with the access limit system:

1. **Visit counter not incrementing**:
   - Check browser console for JavaScript errors
   - Verify the middleware is correctly installed in settings.py

2. **Payment prompts not showing**:
   - Ensure the subscription page has the proper alert code
   - Check that the CSS for the alert is loaded

3. **Predictions not updating**:
   - Check that the update command is running correctly
   - Verify market data is available for the stocks being predicted
