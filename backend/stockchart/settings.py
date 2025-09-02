"""
주식 차트 예측 웹사이트를 위한 Django 설정 파일

이 프로젝트는 사용자가 주식과 암호화폐의 미래 가격을 예측하고
결과를 공유할 수 있는 플랫폼입니다.
"""

from pathlib import Path
from decouple import config
import os

# Try to import dj_database_url for production deployments
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# 프로젝트 기본 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 보안 설정
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key')

# Railway에서 정적 파일 서빙을 위해 DEBUG=True 유지
DEBUG = config('DEBUG', default=True, cast=bool)

# Railway 환경 감지 및 디버그 모드 강제 활성화
RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT', False)
if RAILWAY_ENVIRONMENT or os.environ.get('RAILWAY_PROJECT_ID'):
    DEBUG = True  # Railway에서는 정적 파일 서빙을 위해 강제로 DEBUG=True
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '*.stockchart.kr',
    '*.railway.app',
    '*.herokuapp.com',
    '*.vercel.app'
]

# 애플리케이션 정의
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'oauth2_provider',
    'users',
    'charts',
    'payment_system',
    'market_data',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stockchart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'stockchart.wsgi.application'

# 데이터베이스 설정
# 데이터베이스 설정
if 'DATABASE_URL' in os.environ and HAS_DJ_DATABASE_URL:
    # Production: Use Railway/Heroku database URL
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Development: Use local PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME', default='stockchart_db'),
            'USER': config('DATABASE_USER', default='postgres'),
            'PASSWORD': config('DATABASE_PASSWORD', default='password'),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='5432'),
        }
    }

# 비밀번호 검증
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 국제화 설정
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ko', '한국어'),
    ('en', 'English'),
    ('ja', '日本語'),
    ('zh-hans', '简体中文'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# 정적 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR.parent / 'frontend',  # frontend 디렉토리 추가
]

# 추가 정적 파일 설정 (Railway 호환성)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# 정적 파일 저장소 설정 (기본 Django 저장소 사용)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 로깅 설정 (디버깅용)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'stockchart.static_serve': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Django REST Framework 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# OAuth2 설정
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': '읽기 권한',
        'write': '쓰기 권한',
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 3600 * 24 * 7,
}

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://stockchart.kr",
]

# 개발 환경에서 모든 Origin 허용 (보안상 주의)
CORS_ALLOW_ALL_ORIGINS = True

# API 엔드포인트에 대한 CORS 허용
CORS_ALLOW_CREDENTIALS = True

# 사용자 정의 설정
AUTH_USER_MODEL = 'users.User'

# 이메일 설정
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery 설정
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')

# API 키 설정
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
APPLE_CLIENT_ID = config('APPLE_CLIENT_ID', default='')
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')
ALPHA_VANTAGE_API_KEY = config('ALPHA_VANTAGE_API_KEY', default='')
TWELVE_DATA_API_KEY = config('TWELVE_DATA_API_KEY', default='')
FINNHUB_API_KEY = config('FINNHUB_API_KEY', default='')
POLYGON_API_KEY = config('POLYGON_API_KEY', default='')
TIINGO_API_KEY = config('TIINGO_API_KEY', default='')
MARKETSTACK_API_KEY = config('MARKETSTACK_API_KEY', default='')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
