# Stock Chart Web Application

A comprehensive stock chart prediction platform built with Django and modern web technologies. This application allows users to analyze market data, make predictions, and compete with other traders in a gamified environment.

## 🚀 Features

### Core Functionality
- **📊 Real-time Market Data**: Support for stocks, cryptocurrencies, and international markets
- **🔮 Chart Predictions**: Advanced prediction system with profit tracking
- **🏆 Competitive Rankings**: Leaderboard system based on prediction accuracy
- **💳 Payment Integration**: PayPal and cryptocurrency payment support
- **🌍 Multi-language Support**: International market support with localization
- **👥 Social Features**: User profiles, prediction sharing, and community features
- **⚡ Real-time Updates**: Live market data and prediction updates

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
- **Styling**: Bootstrap 5, Custom CSS with responsive design
- **Charts**: Chart.js for interactive visualizations
- **AJAX**: Real-time data updates without page refresh

### Infrastructure & Deployment
- **Development**: Django development server
- **Production**: Ready for Railway/Heroku deployment
- **Static Files**: Django static file handling
- **Environment**: Python virtual environment (.venv)

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

- **🏠 Homepage**: http://127.0.0.1:8000/
- **⚙️ Admin Panel**: http://127.0.0.1:8000/admin/
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
├── 📂 frontend/                   # Frontend Assets
│   ├── 📂 css/                    # Stylesheets
│   │   ├── style.css              # Main styles
│   │   └── market-data.css        # Market-specific styles
│   ├── 📂 js/                     # JavaScript Files
│   │   ├── app.js                 # Main application logic
│   │   ├── app_clean.js           # Optimized version
│   │   └── app_backup.js          # Backup version
│   ├── 📂 images/                 # Image assets
│   ├── index.html                 # Frontend entry point
│   └── favicon.ico                # Site icon
├── 📄 requirements.txt            # Python dependencies
├── 📄 railway.json               # Railway deployment config
└── 📄 README.md                  # This documentation
```

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
- **🔑 OAuth2 Integration**: Awaiting Google/Apple API credentials
- **💳 Payment Processing**: Finalizing PayPal/crypto implementation
- **📈 Chart Algorithms**: Advanced prediction logic development
- **🌐 Multi-language**: Localization system implementation

### 📋 Upcoming Features
- **🔔 Real-time Notifications**: WebSocket integration
- **🏆 Competition System**: Tournament and event management
- **📊 Advanced Analytics**: Detailed prediction analysis
- **🚀 Production Deployment**: Cloud platform optimization

## 🤝 Contributing

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

---

**⭐ Star this repository if you find it helpful!**

Built with ❤️ by [Iduate](https://github.com/Iduate)
