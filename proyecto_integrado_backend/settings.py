from pathlib import Path
import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# En local lee el archivo .env; en Render las variables vienen del panel
# (load_dotenv NO pisa las variables que ya existen en el entorno).
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------
# Seguridad: todo se controla por variables de entorno
# ---------------------------------------------------------------------
# Por defecto es False (producción). En tu PC agrega DEBUG=True a tu .env
DEBUG = os.environ.get("DEBUG", "False") == "True"

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-solo-para-desarrollo-local"
    else:
        raise ImproperlyConfigured("Falta la variable de entorno SECRET_KEY.")

ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

# Render termina el HTTPS en su proxy: sin esto Django cree que todo es http
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_limarGO',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proyecto_integrado_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'app_limarGO' / 'templates' / 'app_limarGO'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'proyecto_integrado_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
# Toma DATABASE_URL del entorno. En Render: la "Internal Database URL" de tu Postgres.
# En local: la del .env (localhost). SSL solo en producción.
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# STATICFILES_STORAGE fue eliminado en Django 5.1: ahora se usa STORAGES.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'login'


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}