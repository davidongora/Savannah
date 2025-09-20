from .settings import *
import os

# Import test mocks early to patch HTTP requests
try:
    import test_mocks
except ImportError:
    pass

# Override settings for testing
TESTING = True

# Completely disable OIDC authentication during tests
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Use simple test authentication that doesn't make HTTP calls
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'test_auth.TestAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Disable all external services
OIDC_ENABLED = False

# Remove OIDC middleware if present
MIDDLEWARE = [m for m in MIDDLEWARE if 'oidc' not in m.lower()]

# Use in-memory cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable migrations for testing since we use raw SQL schema
MIGRATION_MODULES = {
    'customers': None,
    'orders': None,
    'auth': None,
    'contenttypes': None,
    'sessions': None,
    'admin': None,
    'oauth2_provider': None,
}

# Test-safe external service settings
AFRICAS_TALKING_API_KEY = 'test-key'
AFRICAS_TALKING_USERNAME = 'test-username'
AFRICAS_TALKING_SANDBOX = True

# Remove OIDC settings to prevent any connection attempts
OIDC_RP_CLIENT_ID = None
OIDC_RP_CLIENT_SECRET = None
OIDC_OP_AUTHORIZATION_ENDPOINT = None
OIDC_OP_TOKEN_ENDPOINT = None
OIDC_OP_USER_ENDPOINT = None
OIDC_OP_JWKS_ENDPOINT = None