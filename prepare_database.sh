#!/bin/bash

echo "Making migrations for User and Subscription models..."
cd backend
python manage.py makemigrations users

echo "Making migrations for Payment models..."
python manage.py makemigrations payments

echo "Making migrations for Charts models..."
python manage.py makemigrations charts

echo "Making migrations for Market Data models..."
python manage.py makemigrations market_data

echo "Applying all migrations..."
python manage.py migrate

echo "Checking system status..."
python manage.py check

echo "Checking for API keys in environment..."

# Check and display API keys status
echo "API Keys Status:"
if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
  echo "  Alpha Vantage API Key: Not configured"
else
  echo "  Alpha Vantage API Key: Configured"
fi

if [ -z "$TWELVE_DATA_API_KEY" ]; then
  echo "  Twelve Data API Key: Not configured"
else
  echo "  Twelve Data API Key: Configured"
fi

if [ -z "$FINNHUB_API_KEY" ]; then
  echo "  Finnhub API Key: Not configured"
else
  echo "  Finnhub API Key: Configured"
fi

if [ -z "$POLYGON_API_KEY" ]; then
  echo "  Polygon API Key: Not configured"
else
  echo "  Polygon API Key: Configured"
fi

if [ -z "$TIINGO_API_KEY" ]; then
  echo "  Tiingo API Key: Not configured"
else
  echo "  Tiingo API Key: Configured"
fi

if [ -z "$MARKETSTACK_API_KEY" ]; then
  echo "  Marketstack API Key: Not configured"
else
  echo "  Marketstack API Key: Configured"
fi

if [ -z "$PAYPAL_CLIENT_ID" ]; then
  echo "  PayPal Client ID: Not configured"
else
  echo "  PayPal Client ID: Configured"
fi

if [ -z "$PAYPAL_CLIENT_SECRET" ]; then
  echo "  PayPal Client Secret: Not configured"
else
  echo "  PayPal Client Secret: Configured"
fi

if [ -z "$GOOGLE_CLIENT_ID" ]; then
  echo "  Google Client ID: Not configured"
else
  echo "  Google Client ID: Configured"
fi

echo "Migration and setup complete!"
