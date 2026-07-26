"""
Django settings for finance project.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-3ce!l0a^&xc!a4&^&2=l47rt2(1dta5x^#3hf+_qcilepikf7t")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])


# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_htmx',
    'account',
    'core',
    'portfolio',
    'social',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'account.middleware.FirebaseAuthMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'finance.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.firebase_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'finance.wsgi.application'

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


# Database
# No Django models are backed by a relational database anymore (Firestore is
# the datastore, via the Admin SDK) — this entry only exists because Django's
# settings module requires the key to be present.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'unused.sqlite3',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth routes (used by account.decorators.firebase_login_required)
LOGIN_URL = 'account:login'


# Firebase
FIREBASE_PROJECT_ID = env('FIREBASE_PROJECT_ID', default='finance-98314')
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = env('FIREBASE_SERVICE_ACCOUNT_KEY_PATH', default='')
FIRESTORE_EMULATOR_HOST = env('FIRESTORE_EMULATOR_HOST', default='')
FIREBASE_AUTH_EMULATOR_HOST = env('FIREBASE_AUTH_EMULATOR_HOST', default='')
USE_FIREBASE_EMULATOR = bool(FIRESTORE_EMULATOR_HOST or FIREBASE_AUTH_EMULATOR_HOST)

# Client-safe config for the Firebase JS SDK. These are placeholders until a
# real web app is registered on the Firebase project (see plan §7) — fine for
# emulator-only development, must be replaced before going to production.
FIREBASE_WEB_CONFIG = {
    'apiKey': env('FIREBASE_WEB_API_KEY', default='demo-api-key'),
    'authDomain': env('FIREBASE_WEB_AUTH_DOMAIN', default=f'{FIREBASE_PROJECT_ID}.firebaseapp.com'),
    'projectId': FIREBASE_PROJECT_ID,
    'appId': env('FIREBASE_WEB_APP_ID', default='demo-app-id'),
}
