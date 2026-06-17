from .base import *
from urllib.parse import urlparse

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# CORS settings for production
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_origins:
    CORS_ALLOWED_ORIGINS = cors_origins.split(',')
else:
    CORS_ALLOWED_ORIGINS = []

# Parse DATABASE_URL for PostGIS backend
db_url = os.environ.get('DATABASE_URL')
if db_url:
    parsed = urlparse(db_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or 5432,
        }
    }

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

# Security headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
