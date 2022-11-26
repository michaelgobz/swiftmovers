"""
Django settings for swiftmovers project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import ast
from pathlib import Path
import dj_database_url
import os
from .core.languages import LANGUAGES as CORE_LANGUAGES


# utility functions
def get_bool_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#g#us34=x47@=oe&bhs2rwz$d@o-hnyb7aqh*3jz$_+zb%)w@b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL = get_bool_env("ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL", False)

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Application definition

INSTALLED_APPS = [
    # django modules
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'graphene_django',
    'dj_database_url',
    'django_mysql',
    # mvp modules
    'swiftmovers.swift',
    'swiftmovers.core',
    'swiftmovers.accounts',
    'swiftmovers.checkouts',
    'swiftmovers.invoices',
    'swiftmovers.payments',
    'swiftmovers.shipping',
    'swiftmovers.graphqlcore',
    'swiftmovers.orders',
    'swiftmovers.items',
    # external apps
    'django_measurement',
    'django_prices',
    'django_countries',
    'django_filters',
    'phonenumber_field',
    'phonenumbers'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'swiftmovers.urls'
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ]
        },
    },
]

WSGI_APPLICATION = 'swiftmovers.wsgi.application'

# database names

DATABASE_DEFAULT_NAME = 'default'
DATABASE_REPLICA_NAME = 'replica'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    DATABASE_DEFAULT_NAME: dj_database_url.config(
        default='postgres://swiftAdmin:swiftAdmin@localhost:5432/swift', conn_max_age=800
    )
    # TODO :  add replication user

}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

LANGUAGES = CORE_LANGUAGES

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GRAPHENE = {
    'SCHEMA': 'swiftmovers.schema.schema'
}

AUTH_USER_MODEL = "accounts.User"

DEFAULT_COUNTRY = os.environ.get("DEFAULT_COUNTRY", "US")
DEFAULT_DECIMAL_PLACES = 3
DEFAULT_MAX_DIGITS = 12
DEFAULT_CURRENCY_CODE_LENGTH = 3
