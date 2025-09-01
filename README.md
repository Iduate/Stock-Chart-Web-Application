# Stock Chart Web Application

A comprehensive stock chart prediction platform with the following features:

## Core Features
- **User Registration**: Social login via Google and Apple
- **Chart Predictions**: Users can predict future stock/crypto prices
- **Chart Board**: Public sharing of predictions with profit rankings
- **Payment System**: PayPal integration with free tier limitations
- **Multi-language Support**: Country-based subdomains
- **Admin Panel**: Complete management system in Korean
- **Event System**: Competitions for prediction accuracy

## Technology Stack
- **Backend**: Python Django with REST API
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Database**: PostgreSQL
- **APIs**: Yahoo Finance, Alpha Vantage, TwelveData for market data
- **Payment**: PayPal, crypto payment gateways
- **Authentication**: OAuth2 (Google, Apple)

## Market Data Coverage
- 🪙 Cryptocurrencies
- 🇰🇷 Korean Stocks
- 🇺🇸 US Stocks
- 🇯🇵🇮🇳🇬🇧🇨🇦🇫🇷🇩🇪🇹🇼 Japanese, Indian, UK, Canadian, French, German, Taiwanese markets

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (for Celery tasks)

### Quick Start
1. **Clone and setup**:
   ```bash
   cd "C:\Users\Hp\Desktop\Stock Chart Web\backend"
   ```

2. **Install dependencies** (already done):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations** (already done):
   ```bash
   python manage.py migrate
   ```

4. **Create superuser** (already done):
   ```bash
   python manage.py createsuperuser
   # Username: Iduate
   # Email: davididuate11@gmail.com
   ```

5. **Start the server**:
   ```bash
   python manage.py runserver
   ```

### Environment Variables
Create a `.env` file in the backend directory with:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://postgres:password@localhost:5432/stockchart_db
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
TWELVE_DATA_API_KEY=your-twelve-data-key
```

## Access Points

### Web Interface
- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
  - Username: `Iduate`
  - Password: (as set during superuser creation)

### API Endpoints
- **API Status**: http://127.0.0.1:8000/api/status/
- **User Authentication**: http://127.0.0.1:8000/api/auth/
- **Chart Predictions**: http://127.0.0.1:8000/api/charts/predictions/
- **Market Data**: http://127.0.0.1:8000/api/market/
- **Payment System**: http://127.0.0.1:8000/api/payments/
- **OAuth2**: http://127.0.0.1:8000/o/

## VS Code Tasks
Use Ctrl+Shift+P and run:
- **Django 개발 서버 실행**: Start the development server
- **Django 마이그레이션**: Apply database migrations
- **Django 마이그레이션 생성**: Create new migrations

## Project Structure
```
Stock Chart Web/
├── backend/                    # Django backend
│   ├── stockchart/            # Main Django project
│   ├── users/                 # User management app
│   ├── charts/                # Chart predictions app
│   ├── payment_system/        # Payment processing app
│   ├── market_data/           # Market data app
│   ├── templates/             # HTML templates
│   ├── static/                # Static files
│   └── manage.py              # Django management script
├── frontend/                  # Frontend assets
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

## Features Implementation Status
- ✅ **Project Structure**: Complete Django setup
- ✅ **Database Models**: User, Chart, Market, Payment models
- ✅ **Admin Interface**: Korean admin panel
- ✅ **Basic Frontend**: Bootstrap-based homepage
- ✅ **API Framework**: REST API structure
- 🔄 **Authentication**: OAuth2 setup (needs API keys)
- 🔄 **Payment Integration**: PayPal/Crypto (needs API keys)
- 🔄 **Market Data**: Real-time data fetching (needs API keys)
- 🔄 **Chart Predictions**: Prediction logic
- 🔄 **Social Features**: Ranking, comments, likes

## Next Steps
1. Configure OAuth2 providers (Google, Apple)
2. Set up PayPal and crypto payment APIs
3. Implement market data fetching from APIs
4. Add chart prediction algorithms
5. Enhance frontend with interactive charts
6. Implement real-time notifications
7. Add multi-language support
8. Deploy to production

## License
MIT License
