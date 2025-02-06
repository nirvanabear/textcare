"""
Django settings for TextCare project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import environ
import logging


# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = f"{env('SECRET_KEY')}"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# DEBUG = f"{env('DEBUG')}"


# ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog.apps.CatalogConfig', 
    'whatsapp.apps.WhatsappConfig',
    'chat.apps.ChatConfig',
    'channels',
]

    # 'daphne',
    # 'channels',

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TextCare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'TextCare.wsgi.application'
ASGI_APPLICATION = 'TextCare.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # },
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_v2',
        'USER': f"{env('DB_USER')}",
        'PASSWORD': f"{env('DB_PASSWORD')}",
        'HOST': 'localhost',
        'PORT': '5432',
    },    
}

# Channel Layers
# https://testdriven.io/blog/django-channels/
# Command-line to download and spin up Redis: 
# docker run -p 6379:6379 -d redis:5

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = 'static/'

# Specifies directory where static files of the application are located:
# More efficient serving via Apache, rather than Django handling them.
# STATIC_ROOT = os.path.join(BASE_DIR, "static/")


# Serving static files via Nginx, not Django.
STATIC_ROOT = f"/var/www/{env('EC2_DNS_NAME')}/static"
# STATIC_ROOT = "/home/ubuntu/django/framework/staticfiles"
STATICFILES_DIRS = [
    "/home/ubuntu/django/framework/static",
    "/home/ubuntu/django/framework/catalog/static",
    "/home/ubuntu/django/framework/whatsapp/static",
]

ALLOWED_HOSTS=[f".{env('EC2_DNS_NAME')}", f"{env('IP_ADDRESS')}", f"{env('EC2_HOST_NAME')}","localhost"]

CSRF_TRUSTED_ORIGINS = [f"https://{env('EC2_DNS_NAME')}",]


# Logging
# https://docs.djangoproject.com/en/5.1/topics/logging/#top

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/home/ubuntu/django/framework/config/logging/debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}




##### PRODUCTION DEPLOYMENT #####

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# The absolute path to the directory where collectstatic will collect static files for deployment.

# STATIC_ROOT = BASE_DIR / 'staticfiles'


# The URL to use when referring to static files (where they will be served from)

# Static file serving.
# https://whitenoise.readthedocs.io/en/stable/django.html#add-compression-and-caching-support
# STORAGES = {
#     # ...
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }
