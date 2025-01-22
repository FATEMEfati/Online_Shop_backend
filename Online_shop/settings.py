
"""
Django settings for Online_shop project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta
from celery.schedules import crontab


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_DIR / 'staticfiles'


ARVAN_ENDPOINT = os.getenv("ARVAN_ENDPOINT", "https://s3.ir-thr-at1.arvanstorage.com")
ARVAN_BUCKET_NAME = os.getenv("ARVAN_BUCKET_NAME", "maktabshop-storage")
ARVAN_ACCESS_KEY = os.getenv("ARVAN_ACCESS_KEY", "ddf20595-9019-41ff-b148-bd3710cdea6e")
ARVAN_SECRET_KEY = os.getenv("ARVAN_SECRET_KEY", "c1b4aa9583754d5a331554a918e5600f63d11e0f0aadcf1e20629cb816337691")

# AWS S3 settings
AWS_ACCESS_KEY_ID = ARVAN_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = ARVAN_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = ARVAN_BUCKET_NAME
AWS_S3_ENDPOINT_URL = ARVAN_ENDPOINT
AWS_S3_REGION_NAME = ''  # Set if needed, otherwise keep it empty

# Storage settings
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",  # Use S3Boto3Storage for compatibility
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = f'https://s3.ir-thr-at1.arvanstorage.com/{AWS_STORAGE_BUCKET_NAME}/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = 'static/'





# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lv_ar-&)i8h(t+(suz+x^i@f$@+_uaz-!0y9!0#93%ste@i%7c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'admin_interface',
    'colorfield', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'Orders',
    'Products',
    'User',
    'Discount',
    'storages',
    
]
ADMIN_SITE_HEADER = 'MaktabShop Admin'
ADMIN_SITE_TITLE = 'MaktabShop'
ADMIN_INDEX_TITLE = 'Welcome to MaktabShop'
ADMIN_INTERFACE_COLOR_SCHEME = 'dark'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# JWT Settings (optional)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # other settings...
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'User.middleware.TokenAuthenticationMiddleware',
    
]

ROOT_URLCONF = 'Online_shop.urls'

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8001",
]

CORS_ALLOW_CREDENTIALS = True


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

WSGI_APPLICATION = 'Online_shop.wsgi.application'
CORS_ALLOW_ALL_ORIGINS = True

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'fateme',
        'PASSWORD': 'Math1379',
        'HOST': '194.5.193.46',
        'PORT': '5432',
    }
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'User.User'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # Adjust as needed
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fatemenoormohammadi.dc@gmail.com'
EMAIL_HOST_PASSWORD = 'ternebdogxftuhli'

SECURE_COOKIES = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_SECURE = True

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/1"
CELERY_TASK_SERIALIZER = 'json'
# CELERY_IMPORTS = ("tasks", )
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {
    'delete-unactivated-users-every-day': {
        'task': 'User.tasks.delete_unactivated_users',
        'schedule': crontab(minute='*/5'),  
    },
    'delete-unpaid-orders-every-15-minutes': {
        'task': 'User.tasks.delete_unpaid_orders',
        'schedule': crontab(minute='*/5'),  
    },
    'clear-old-cart-items-every-20-seconds': {
        'task': 'User.tasks.clear_old_cart_items',
        'schedule': crontab(minute='*/1'),  # Run every 5 seconds
    },
}