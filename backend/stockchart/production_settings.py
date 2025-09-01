"""
Production settings for deployment
"""
import os
from .settings import *

# Try to import dj_database_url for production deployments
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# Production settings
DEBUG = False
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    '.herokuapp.com',
    '.vercel.app',
    '.netlify.app'
]

# Database for production
if 'DATABASE_URL' in os.environ and HAS_DJ_DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }

# Static files for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://your-app.railway.app",
]

CORS_ALLOW_ALL_ORIGINS = True  # Only for development
