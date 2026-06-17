from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Standalone SQLite database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email Backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
