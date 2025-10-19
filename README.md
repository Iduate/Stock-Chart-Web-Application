# Stock Chart Web Application

A professional stock chart prediction platform with **TradingView-inspired design** built using Django backend and modern web technologies. This application provides a complete trading anal## 📈 Implementation Status & Recent Updates

### ✅ Recently Completed (Latest Updates)
- **🎨 TradingView Design System**: Complete UI overhaul with professional trading platform aesthetics
- **📊 Professional Admin Dashboard**: TradingView-styled admin interface with Chart.js integration
- **🔧 Database Schema Fixes**: Resolved PostgreSQL constraints and missing columns
- **🔐 Authentication Improvements**: Fixed admin login with custom token middleware
- **📱 Mobile Optimization**: Responsive design improvements for all devices
- **🎯 Chart Controls**: Enhanced chart interaction buttons and controls
- **🌐 Multi-page Consistency**: Unified design system across all application pages

### ✅ Core Features Completed
- **🏗️ Project Architecture**: Complete Django setup with modular app structure
- **🗃️ Database Models**: User, Chart, Market Data, Payment models fully implemented
- **🔧 Admin Interface**: Professional Korean/English admin panel with custom styling
- **🎨 Frontend Foundation**: TradingView-inspired responsive design system
- **📡 API Framework**: RESTful API structure with Django REST Framework
- **📈 Market Data Integration**: Real-time data fetching capabilities implemented
- **💰 Payment System**: PayPal and cryptocurrency payment infrastructure
- **🔐 User Authentication**: OAuth2 structure + custom token authentication
- **📱 Responsive Design**: Mobile-first interface with touch optimizationment with advanced charting, prediction systems, and competitive features.

## 🎨 Design Philosophy

This application features a **professional TradingView-style interface** with:
- **Dark Theme**: Modern dark UI matching professional trading platforms
- **Consistent Design System**: Custom CSS variables for brand consistency
- **Responsive Layout**: Mobile-first design with Bootstrap integration
- **Professional Typography**: Clean, readable fonts optimized for financial data
- **Interactive Elements**: Smooth animations and hover effects

## 🚀 Features

### Core Functionality
- **📊 Real-time Market Data**: Live stock, crypto, and international market data
- **🔮 Advanced Chart Predictions**: AI-powered prediction system with profit tracking
- **🏆 Competitive Rankings**: Leaderboard system based on prediction accuracy
- **💳 Integrated Payments**: PayPal and cryptocurrency payment support
- **🌍 Multi-language Support**: Korean and English localization
- **👥 Social Features**: User profiles, prediction sharing, and community interaction
- **⚡ Real-time Updates**: Live market data and prediction updates
- **🎯 Professional Admin Dashboard**: TradingView-styled admin interface

### Market Coverage
- 🪙 **Cryptocurrencies**: Bitcoin, Ethereum, and major altcoins
- 🇺🇸 **US Markets**: NYSE, NASDAQ stocks
- 🇰🇷 **Korean Markets**: KOSPI, KOSDAQ
- 🌏 **International**: Japanese, Indian, UK, Canadian, European, Taiwanese markets

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL with advanced indexing
- **Authentication**: OAuth2 (Google, Apple), JWT tokens
- **Task Queue**: Celery with Redis
- **API Integration**: Yahoo Finance, Alpha Vantage, TwelveData

### Frontend
- **Core**: HTML5, CSS3, Modern JavaScript (ES6+)
- **Design System**: TradingView-inspired dark theme with custom CSS variables
- **Styling**: Bootstrap 5 + Custom CSS with professional trading interface
- **Charts**: Chart.js for interactive financial visualizations
- **Responsive**: Mobile-first design with touch-optimized controls
- **Performance**: Optimized loading and smooth animations

### Infrastructure & Deployment
- **Development**: Django development server with hot reload
- **Production**: Railway/Heroku deployment ready
- **Database**: PostgreSQL with advanced indexing and constraints
- **Static Files**: Optimized Django static file handling
- **Environment**: Python virtual environment (.venv) with dependency management
- **Authentication**: Custom token middleware with admin session compatibility

## Market Data Coverage
- 🪙 Cryptocurrencies
- 🇰🇷 Korean Stocks
- 🇺🇸 US Stocks
- 🇯🇵🇮🇳🇬🇧🇨🇦🇫🇷🇩🇪🇹🇼 Japanese, Indian, UK, Canadian, French, German, Taiwanese markets

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.8+ (recommended 3.11+)
- **PostgreSQL**: 12+ for database
- **Git**: For version control
- **Virtual Environment**: Python venv or virtualenv

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Iduate/Stock-Chart-Web-Application.git
   cd Stock-Chart-Web-Application
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

### 🌐 Access Points

- **🏠 Homepage**: http://127.0.0.1:8000/ (TradingView-styled interface)
- **⚙️ Admin Panel**: http://127.0.0.1:8000/admin/ (Professional dashboard)
  - Username: `admin` | Password: `admin123`
  - Username: `Iduate` | Password: `password123`
- **📡 API Status**: http://127.0.0.1:8000/api/status/
- **📊 Market Data API**: http://127.0.0.1:8000/api/market/
- **🔮 Predictions API**: http://127.0.0.1:8000/api/charts/predictions/
- **💳 Payments API**: http://127.0.0.1:8000/api/payments/

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
# Django Configuration
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/stockchart_db

# OAuth2 Social Authentication
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret

# Payment Integration
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
CRYPTO_API_KEY=your-crypto-payment-api-key

# Market Data APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
TWELVE_DATA_API_KEY=your-twelve-data-key
YAHOO_FINANCE_API_KEY=your-yahoo-finance-key

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### VS Code Development Tasks

Use `Ctrl+Shift+P` in VS Code and search for:
- **🚀 Django Development Server**: Start the development server
- **🔄 Django 마이그레이션**: Apply database migrations  
- **📝 Django 마이그레이션 생성**: Create new migrations

## 📁 Project Structure

```
Stock Chart Web/
├── 📂 backend/                     # Django Backend Application
│   ├── 📂 stockchart/             # Main Django Project
│   │   ├── settings.py            # Django configuration
│   │   ├── urls.py                # URL routing
│   │   ├── views.py               # Main views
│   │   └── wsgi.py                # WSGI configuration
│   ├── 📂 users/                  # User Management System
│   │   ├── models.py              # User models & profiles
│   │   ├── views.py               # Authentication views
│   │   └── serializers.py         # API serializers
│   ├── 📂 charts/                 # Chart Prediction System
│   │   ├── models.py              # Prediction models
│   │   ├── views.py               # Chart API endpoints
│   │   └── serializers.py         # Chart data serializers
│   ├── 📂 market_data/            # Market Data Integration
│   │   ├── models.py              # Market data models
│   │   ├── services.py            # External API services
│   │   ├── views.py               # Market data endpoints
│   │   └── views_fixed.py         # Enhanced market views
│   ├── 📂 payment_system/         # Payment Processing
│   │   ├── models.py              # Payment models
│   │   └── views.py               # Payment endpoints
│   ├── 📂 templates/              # HTML Templates
│   │   ├── home.html              # Homepage template
│   │   └── index.html             # Main index
│   └── 📂 static/                 # Django static files
├── 📂 frontend/                   # Frontend Assets & TradingView Design
│   ├── 📂 css/                    # Professional Stylesheets
│   │   ├── style.css              # Main TradingView-inspired styles
│   │   ├── market-data.css        # Market-specific components
│   │   ├── chart-controls.css     # Chart interaction styles
│   │   ├── stock-symbols.css      # Stock symbol displays
│   │   └── mobile-fixes.css       # Mobile responsive fixes
│   ├── 📂 js/                     # JavaScript Modules
│   │   ├── app.js                 # Main application logic
│   │   ├── app_clean.js           # Optimized production version
│   │   └── market-data.js         # Market data handling
│   ├── 📂 admin/                  # Professional Admin Interface
│   │   ├── index.html             # TradingView-styled admin dashboard
│   │   └── js/admin.js            # Admin dashboard functionality
│   ├── 📂 templates/              # Page Templates
│   │   ├── home.html              # Main homepage
│   │   ├── charts.html            # Chart analysis page
│   │   ├── prediction.html        # Prediction interface
│   │   ├── ranking.html           # User rankings
│   │   ├── subscription.html      # Payment & subscription
│   │   └── events.html            # Trading events
│   ├── index.html                 # Frontend entry point
│   └── favicon.ico                # Site icon
├── 📄 requirements.txt            # Python dependencies
├── 📄 railway.json               # Railway deployment config
└── 📄 README.md                  # This documentation
```

## 💳 Buy Crypto with Card (MoonPay)

We support a simple fiat-to-crypto on-ramp via MoonPay so users can purchase Bitcoin (BTC) or Ethereum (ETH) with credit/debit cards.

Environment variables (set in `backend/.env` or hosting dashboard):

```
MOONPAY_API_KEY=your-moonpay-api-key
MOONPAY_SECRET_KEY=your-moonpay-secret
MOONPAY_SANDBOX=true
```

Backend endpoint:
- POST `/api/payments/onramp/moonpay/init/` → returns `{ url }` (signed MoonPay URL)

Frontend:
- Open `frontend/buy-crypto.html` to start a purchase. On success/cancel, users are redirected to `payment-success.html` or `payment-cancel.html`.

Notes:
- KYC may be required by the provider. We do not custody funds; assets are sent to the user’s wallet.


## 📈 Current Implementation Status

### ✅ Completed Features
- **🏗️ Project Structure**: Complete Django setup with modular architecture
- **🗃️ Database Models**: User, Chart, Market Data, Payment models implemented
- **🔧 Admin Interface**: Comprehensive Korean admin panel
- **🎨 Frontend Foundation**: Bootstrap-based responsive design
- **📡 API Framework**: RESTful API structure with DRF
- **� Market Data Integration**: Real-time data fetching capabilities
- **💰 Payment System**: PayPal and crypto payment structure
- **🔐 User Authentication**: OAuth2 setup ready for API keys
- **� Responsive Design**: Mobile-friendly interface

### 🔄 In Progress
- **🔑 OAuth2 Integration**: Google/Apple API credential integration
- **💳 Payment Processing**: Final PayPal/crypto payment implementation
- **📈 Advanced Algorithms**: Machine learning prediction model training
- **🌐 Localization**: Korean/English translation system completion

### 📋 Next Development Phase  
- **🔔 Real-time Notifications**: WebSocket implementation for live updates
- **🏆 Competition System**: Tournament and trading event management
- **📊 Advanced Analytics**: Comprehensive prediction performance analysis
- **🚀 Production Optimization**: Performance tuning and cloud deployment
- **🧪 Testing Suite**: Comprehensive unit and integration tests

## 🎨 TradingView Design Features

### Color Palette
```css
:root {
    --tv-bg-primary: #1e222d;      /* Main background */
    --tv-bg-secondary: #2a2e39;    /* Panel backgrounds */
    --tv-bright-blue: #2962ff;     /* Accent color */
    --tv-text-primary: #d1d4dc;    /* Primary text */
    --tv-text-secondary: #868993;  /* Secondary text */
    --tv-success: #4caf50;         /* Success states */
    --tv-danger: #f23645;          /* Error states */
}
```

### Design Components
- **📊 Professional Charts**: Chart.js with TradingView color schemes
- **🎛️ Advanced Controls**: Custom styled form controls and buttons
- **📱 Responsive Layout**: Breakpoint-optimized for all devices
- **⚡ Smooth Animations**: CSS transitions and hover effects
- **🎯 Interactive Elements**: Touch-friendly controls with visual feedback

## 🛠️ Development Tools & Scripts

### Automated Setup Scripts
- **`setup_vscode.bat`**: VS Code workspace configuration
- **`install_packages.bat`**: Automated dependency installation
- **`prepare_database.bat`**: Database setup and migrations
- **`activate.bat`**: Virtual environment activation
- **`fix_all_issues.bat`**: Comprehensive issue resolution

### Development Commands
```bash
# Database Management
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py shell              # Django shell access

# User Management
python manage.py createsuperuser    # Create admin user
python manage.py collectstatic      # Collect static files

# Development Server
python manage.py runserver          # Start development server
```

## 📊 Database Schema

### Key Models
- **User Model**: Extended Django user with trading profiles
- **Chart Model**: Prediction charts with validation
- **MarketData Model**: Real-time financial data storage
- **Payment Model**: Transaction and subscription tracking
- **Event Model**: Trading competitions and tournaments

### Recent Database Fixes
- ✅ Added missing `free_access_count` column
- ✅ Resolved NOT NULL constraint issues
- ✅ Fixed unique constraints for referral codes
- ✅ Optimized indexes for performance

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 🚀 Deployment

### Railway Deployment
This project is configured for Railway deployment:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

### Manual Deployment
1. Set up production database
2. Configure environment variables
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic`
5. Start with Gunicorn: `gunicorn stockchart.wsgi:application`

## 📞 Support

- **📧 Email**: davididuate11@gmail.com
- **🐛 Issues**: [GitHub Issues](https://github.com/Iduate/Stock-Chart-Web-Application/issues)
- **📖 Documentation**: Check the `/docs` folder (coming soon)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django Community for the excellent framework
- Chart.js for beautiful chart visualizations
- Bootstrap team for responsive design components
- Financial data providers (Yahoo Finance, Alpha Vantage, TwelveData)

## 🔄 Recent Updates & Changelog

### Version 2.0.0 - TradingView Professional Design (Latest)
- **🎨 Complete UI Overhaul**: Implemented TradingView-inspired dark theme
- **📊 Professional Admin Dashboard**: Custom admin interface with Chart.js
- **🔧 Database Fixes**: Resolved PostgreSQL schema issues and constraints
- **🔐 Authentication Improvements**: Fixed admin login with middleware exclusions
- **📱 Mobile Optimization**: Enhanced responsive design for all devices
- **🎯 Chart Controls**: Improved chart interaction and user experience

### Technical Improvements
- **Custom CSS Variables**: Professional color system implementation
- **Token Authentication**: Custom middleware with admin compatibility
- **Database Schema**: Fixed missing columns and constraint violations
- **Performance**: Optimized static file loading and CSS organization

---

**⭐ Star this repository if you find it helpful!**

Built with ❤️ by [Iduate](https://github.com/Iduate) | Professional TradingView-Inspired Design
