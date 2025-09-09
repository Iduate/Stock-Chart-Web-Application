@echo off
echo Making migrations for User and Subscription models...
cd backend
python manage.py makemigrations users

echo Making migrations for Payment models...
python manage.py makemigrations payments

echo Making migrations for Charts models...
python manage.py makemigrations charts

echo Making migrations for Market Data models...
python manage.py makemigrations market_data

echo Applying all migrations...
python manage.py migrate

echo Checking system status...
python manage.py check

echo Checking for API keys in environment...

:: Check and display API keys status
echo API Keys Status:
if "%ALPHA_VANTAGE_API_KEY%"=="" (
  echo   Alpha Vantage API Key: Not configured
) else (
  echo   Alpha Vantage API Key: Configured
)

if "%TWELVE_DATA_API_KEY%"=="" (
  echo   Twelve Data API Key: Not configured
) else (
  echo   Twelve Data API Key: Configured
)

if "%FINNHUB_API_KEY%"=="" (
  echo   Finnhub API Key: Not configured
) else (
  echo   Finnhub API Key: Configured
)

if "%POLYGON_API_KEY%"=="" (
  echo   Polygon API Key: Not configured
) else (
  echo   Polygon API Key: Configured
)

if "%TIINGO_API_KEY%"=="" (
  echo   Tiingo API Key: Not configured
) else (
  echo   Tiingo API Key: Configured
)

if "%MARKETSTACK_API_KEY%"=="" (
  echo   Marketstack API Key: Not configured
) else (
  echo   Marketstack API Key: Configured
)

if "%PAYPAL_CLIENT_ID%"=="" (
  echo   PayPal Client ID: Not configured
) else (
  echo   PayPal Client ID: Configured
)

if "%PAYPAL_CLIENT_SECRET%"=="" (
  echo   PayPal Client Secret: Not configured
) else (
  echo   PayPal Client Secret: Configured
)

if "%GOOGLE_CLIENT_ID%"=="" (
  echo   Google Client ID: Not configured
) else (
  echo   Google Client ID: Configured
)

echo Migration and setup complete!
pause
