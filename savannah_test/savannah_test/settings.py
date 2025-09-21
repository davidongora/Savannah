import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-zn&s#*ul!1%7ag8qm+*k)_1trhqaoc!5hnvkh*5z32=sc@rz%s')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '185.240.51.176']
if os.getenv('ALLOWED_HOSTS'):
    ALLOWED_HOSTS.extend(os.getenv('ALLOWED_HOSTS').split(','))
if not DEBUG:
    ALLOWED_HOSTS.extend(['*.vercel.app'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'oauth2_provider',
    'mozilla_django_oidc',
    'django_filters',
    'corsheaders',
    'core',
    'customers',
    'orders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'savannah_test.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'savannah_test.wsgi.application'

DATABASES = {
    'default': { 
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'customer_order_db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'root'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

OAUTH2_PROVIDER = {
    'SCOPES': {
        'openid': 'OpenID Connect scope',
        'profile': 'Profile information',
        'email': 'Email address',
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 24 * 60 * 60,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600,
    'ROTATE_REFRESH_TOKEN': True,
    'OIDC_ENABLED': True,
    'OIDC_RSA_PRIVATE_KEY': os.getenv('OIDC_RSA_PRIVATE_KEY', ''),
}

OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID', 'savannah-client')
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET', 'savannah-secret')
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT', 'http://185.240.51.176:8003/o/authorize/')
OIDC_OP_TOKEN_ENDPOINT = os.getenv('OIDC_OP_TOKEN_ENDPOINT', 'http://185.240.51.176:8003/o/token/')
OIDC_OP_USER_ENDPOINT = os.getenv('OIDC_OP_USER_ENDPOINT', 'http://185.240.51.176:8003/o/userinfo/')
OIDC_OP_JWKS_ENDPOINT = os.getenv('OIDC_OP_JWKS_ENDPOINT', 'http://185.240.51.176:8003/o/.well-known/jwks.json')
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_RP_SCOPES = 'openid profile email'
OIDC_CREATE_USER = True
OIDC_USERNAME_ALGO = 'mozilla_django_oidc.utils.generate_username'
OIDC_AUTHENTICATE_CLASS = 'mozilla_django_oidc.views.OIDCAuthenticationRequestView'
OIDC_CALLBACK_CLASS = 'mozilla_django_oidc.views.OIDCAuthenticationCallbackView'

AUTHENTICATION_BACKENDS = [
    'core.oidc_auth.SavannahOIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Africa's Talking SMS Configuration
AFRICAS_TALKING_API_KEY = os.getenv('AFRICAS_TALKING_API_KEY')
AFRICAS_TALKING_USERNAME = os.getenv('AFRICAS_TALKING_USERNAME')
AFRICAS_TALKING_SANDBOX = os.getenv('AFRICAS_TALKING_SANDBOX', 'True').lower() == 'true'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


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

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://185.240.51.176:8003",
]

CSRF_TRUSTED_ORIGINS = [
    "http://185.240.51.176:8003",
    "http://localhost:8003",
    "http://127.0.0.1:8003",
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AFRICAS_TALKING_API_KEY = os.getenv('AFRICAS_TALKING_API_KEY')
AFRICAS_TALKING_USERNAME = os.getenv('AFRICAS_TALKING_USERNAME')
AFRICAS_TALKING_SANDBOX = os.getenv('AFRICAS_TALKING_SANDBOX', 'True') == 'True'
