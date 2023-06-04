"""
Django's settings for swiftmovers project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import ast
import locale

import django
from django.utils.encoding import force_str

import ast
import logging
import os
import os.path
import warnings
from datetime import timedelta
from typing import List

import dj_database_url
import dj_email_url
import django_cache_url
import django_stubs_ext
import jaeger_client.config
import pkg_resources
import sentry_sdk
import sentry_sdk.utils
from celery.schedules import crontab
from django.conf import global_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from graphql.execution import executor
from pytimeparse import parse
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

from . import PatchedSubscriberExecutionContext, __version__
from .core.languages import LANGUAGES as CORE_LANGUAGES
from .core.schedules import initiated_sale_webhook_schedule

from pathlib import Path
import dj_database_url
import os
from .core.languages import LANGUAGES as CORE_LANGUAGES

# force encoding

django.utils.encoding.force_text = force_str

django_stubs_ext.monkeypatch()


def get_list(text):
    return [item.strip() for item in text.split(",")]


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
# Make this unique, and don't share it with anybody.

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_env("DEBUG", True)

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY and DEBUG:
    warnings.warn("SECRET_KEY not configured, using a random temporary key.")
    SECRET_KEY = get_random_secret_key()

RSA_PRIVATE_KEY = os.environ.get("RSA_PRIVATE_KEY", None)
RSA_PRIVATE_PASSWORD = os.environ.get("RSA_PRIVATE_PASSWORD", None)
JWT_MANAGER_PATH = os.environ.get(
    "JWT_MANAGER_PATH", "swiftmovers.core.jwt_manager.JWTManager"
)

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL = get_bool_env("ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL", False)

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

ADMINS = (
    ('Michael Goboola', 'michael.goboola@admin.com'),
)

AUTH_USER_MODEL = "account.User"

MANAGERS = ADMINS

APPEND_SLASH = False

_DEFAULT_CLIENT_HOSTS = "localhost,127.0.0.1"

ALLOWED_CLIENT_HOSTS = os.environ.get("ALLOWED_CLIENT_HOSTS")
if not ALLOWED_CLIENT_HOSTS:
    if DEBUG:
        ALLOWED_CLIENT_HOSTS = _DEFAULT_CLIENT_HOSTS
    else:
        raise ImproperlyConfigured(
            "ALLOWED_CLIENT_HOSTS environment variable must be set when DEBUG=False."
        )

ALLOWED_CLIENT_HOSTS = get_list(ALLOWED_CLIENT_HOSTS)

INTERNAL_IPS = get_list(os.environ.get("INTERNAL_IPS", "127.0.0.1"))

# Maximum time in seconds Django can keep the database connections opened.
# Set the value to 0 to disable connection persistence, database connections
# will be closed after each request.
DB_CONN_MAX_AGE = int(os.environ.get("DB_CONN_MAX_AGE", 600))

DATABASE_ROUTERS = ["swiftmovers.core.db_routers.PrimaryReplicaRouter"]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
LANGUAGES = CORE_LANGUAGES
LOCALE_PATHS = [os.path.join(PROJECT_ROOT, 'locale')]
USE_I18N = True
USE_L10N = True
USE_TZ = True

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

EMAIL_URL = os.environ.get("EMAIL_URL")
SENDGRID_USERNAME = os.environ.get("SENDGRID_USERNAME")
SENDGRID_PASSWORD = os.environ.get("SENDGRID_PASSWORD")
if not EMAIL_URL and SENDGRID_USERNAME and SENDGRID_PASSWORD:
    EMAIL_URL = (
        f"smtp://{SENDGRID_USERNAME}"
        f":{SENDGRID_PASSWORD}@smtp.sendgrid.net:587/?tls=True"
    )

email_config = dj_email_url.parse(
    EMAIL_URL or "console://demo@example.com:console@example/"
)

EMAIL_FILE_PATH: str = email_config["EMAIL_FILE_PATH"]
EMAIL_HOST_USER: str = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD: str = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST: str = email_config["EMAIL_HOST"]
EMAIL_PORT: int = email_config["EMAIL_PORT"]
EMAIL_BACKEND: str = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS: bool = email_config["EMAIL_USE_TLS"]
EMAIL_USE_SSL: bool = email_config["EMAIL_USE_SSL"]

# If enabled, make sure you have set proper storefront address in ALLOWED_CLIENT_HOSTS.
ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL = get_bool_env(
    "ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL", True
)

ENABLE_SSL = get_bool_env("ENABLE_SSL", False)

if ENABLE_SSL:
    SECURE_SSL_REDIRECT = not DEBUG

DEFAULT_FROM_EMAIL: str = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

MEDIA_ROOT: str = os.path.join(PROJECT_ROOT, "media")
MEDIA_URL: str = os.environ.get("MEDIA_URL", "/media/")

STATIC_ROOT: str = os.path.join(PROJECT_ROOT, "static")
STATIC_URL: str = os.environ.get("STATIC_URL", "/static/")
STATICFILES_DIRS = [
    ("images", os.path.join(PROJECT_ROOT, "swiftmovers", "static", "images"))
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

context_processors = [
    "django.template.context_processors.debug",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "swiftmovers.site.context_processors.site",
]

loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")

# Additional password algorithms that can be used by swiftmovers.
# The first algorithm defined by Django is the preferred one; users not using the
# first algorithm will automatically be upgraded to it upon login
PASSWORD_HASHERS = [
    *global_settings.PASSWORD_HASHERS,
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

# Application definition

INSTALLED_APPS = [
    # Django modules
    'django.contrib.postgres',
    'django_celery_beat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # External apps that need to go before django's
    'storages',
    # swiftmovers modules
    'swiftmovers.core',
    'swiftmovers.app',
    'swiftmovers.account',
    'swiftmovers.attribute',
    'swiftmovers.checkout',
    'swiftmovers.invoice',
    'swiftmovers.payment',
    'swiftmovers.product',
    'swiftmovers.page',
    'swiftmovers.plugins',
    'swiftmovers.giftcard',
    'swiftmovers.channel',
    'swiftmovers.menu',
    'swiftmovers.site',
    'swiftmovers.seo',
    'swiftmovers.csv',
    'swiftmovers.discount',
    'swiftmovers.permission',
    'swiftmovers.schedulers',
    'swiftmovers.shipping',
    'swiftmovers.graphql',
    'swiftmovers.reviews',
    'swiftmovers.tracking',
    'swiftmovers.tax',
    'swiftmovers.thumbnail',
    'swiftmovers.subscriptions',
    'swiftmovers.webhook',
    'swiftmovers.warehouse',
    'swiftmovers.order',
    # external apps
    'django_measurement',
    'django_prices',
    'django_countries',
    'django_prices_openexchangerates',
    'django_prices_vatlayer',
    'django_filters',
    'mptt',
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

ENABLE_DJANGO_EXTENSIONS = get_bool_env("ENABLE_DJANGO_EXTENSIONS", False)
if ENABLE_DJANGO_EXTENSIONS:
    INSTALLED_APPS += [
        "django_extensions",
    ]

ENABLE_DEBUG_TOOLBAR = get_bool_env("ENABLE_DEBUG_TOOLBAR", False)
if ENABLE_DEBUG_TOOLBAR:
    # Ensure the graphiql debug toolbar is actually installed before adding it
    try:
        __import__("graphiql_debug_toolbar")
    except ImportError as exc:
        msg = (
            f"{exc} -- Install the missing dependencies by "
            f"running `pip install -r requirements.txt`"
        )
        warnings.warn(msg)
    else:
        INSTALLED_APPS += ["django.forms", "debug_toolbar", "graphiql_debug_toolbar"]
        MIDDLEWARE.append("swiftmovers.graphql.middleware.DebugToolbarMiddleware")

        DEBUG_TOOLBAR_PANELS = [
            "ddt_request_history.panels.request_history.RequestHistoryPanel",
            "debug_toolbar.panels.timer.TimerPanel",
            "debug_toolbar.panels.headers.HeadersPanel",
            "debug_toolbar.panels.request.RequestPanel",
            "debug_toolbar.panels.sql.SQLPanel",
            "debug_toolbar.panels.profiling.ProfilingPanel",
        ]
        DEBUG_TOOLBAR_CONFIG = {"RESULTS_CACHE_SIZE": 100}

WSGI_APPLICATION = 'swiftmovers.wsgi.application'

# database names

DATABASE_CONNECTION_DEFAULT_NAME = 'default'
DATABASE_CONNECTION_REPLICA_NAME = 'replica'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    DATABASE_CONNECTION_DEFAULT_NAME:
        {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'swiftmovers',
            'USER': 'admin',
            'PASSWORD': 'swift',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        },
    DATABASE_CONNECTION_REPLICA_NAME:
        {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'swiftmovers',
            'USER': 'admin',
            'PASSWORD': 'swift',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
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

# LOGGING

# Make the `logging` Python module capture `warnings.warn()` calls
# This is needed in order to log them as JSON when DEBUG=False
logging.captureWarnings(True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["default"]},
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        "json": {
            "()": "swiftmovers.core.logging.JsonFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "format": (
                    "%(asctime)s %(levelname)s %(lineno)s %(message)s %(name)s "
                    + "%(pathname)s %(process)d %(threadName)s"
            ),
        },
        "celery_json": {
            "()": "swiftmovers.core.logging.JsonCeleryFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "format": (
                "%(asctime)s %(levelname)s %(celeryTaskId)s %(celeryTaskName)s "
            ),
        },
        "celery_task_json": {
            "()": "swiftmovers.core.logging.JsonCeleryTaskFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "format": (
                "%(asctime)s %(levelname)s %(celeryTaskId)s %(celeryTaskName)s "
                "%(message)s "
            ),
        },
        "verbose": {
            "format": (
                "%(asctime)s %(levelname)s %(name)s %(message)s "
                "[PID:%(process)d:%(threadName)s]"
            )
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "json",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server" if DEBUG else "json",
        },
        "celery_app": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "celery_json",
        },
        "celery_task": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "celery_task_json",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {"level": "INFO", "propagate": True},
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.app.trace": {
            "handlers": ["celery_app"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["celery_task"],
            "level": "INFO",
            "propagate": False,
        },
        "swiftmovers": {"level": "DEBUG", "propagate": True},
        "swiftmovers.graphql.errors.handled": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "graphql.execution.utils": {"propagate": False, "handlers": ["null"]},
        "graphql.execution.executor": {"propagate": False, "handlers": ["null"]},
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    }
]

DEFAULT_COUNTRY = os.environ.get("DEFAULT_COUNTRY", "UG")
DEFAULT_DECIMAL_PLACES = 3
DEFAULT_MAX_DIGITS = 12
DEFAULT_CURRENCY_CODE_LENGTH = 3

# The default max length for the display name of the
# sender email address.
# Following the recommendation of https://tools.ietf.org/html/rfc5322#section-2.1.1
DEFAULT_MAX_EMAIL_DISPLAY_NAME_LENGTH = 78

COUNTRIES_OVERRIDE = {"EU": "European Union"}

OPENEXCHANGERATES_API_KEY = os.environ.get("OPENEXCHANGERATES_API_KEY")

GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get("GOOGLE_ANALYTICS_TRACKING_ID")


def get_host():
    from django.contrib.sites.models import Site

    return Site.objects.get_current().domain


PAYMENT_HOST = get_host

PAYMENT_MODEL = "order.Payment"

MAX_USER_ADDRESSES = int(os.environ.get("MAX_USER_ADDRESSES", 100))

TEST_RUNNER = "swiftmovers.tests.runner.PytestTestRunner"


PLAYGROUND_ENABLED = get_bool_env("PLAYGROUND_ENABLED", True)

ALLOWED_HOSTS = get_list(os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1"))
ALLOWED_GRAPHQL_ORIGINS: List[str] = get_list(
    os.environ.get("ALLOWED_GRAPHQL_ORIGINS", "*")
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

LANGUAGES = CORE_LANGUAGES

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# See https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_LOCATION = os.environ.get("AWS_LOCATION", "")
AWS_MEDIA_BUCKET_NAME = os.environ.get("AWS_MEDIA_BUCKET_NAME")
AWS_MEDIA_CUSTOM_DOMAIN = os.environ.get("AWS_MEDIA_CUSTOM_DOMAIN")
AWS_QUERYSTRING_AUTH = get_bool_env("AWS_QUERYSTRING_AUTH", False)
AWS_QUERYSTRING_EXPIRE = get_bool_env("AWS_QUERYSTRING_EXPIRE", 3600)
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_STATIC_CUSTOM_DOMAIN")
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", None)
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", None)
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = os.environ.get("AWS_DEFAULT_ACL", None)
AWS_S3_FILE_OVERWRITE = get_bool_env("AWS_S3_FILE_OVERWRITE", True)

# Google Cloud Storage configuration
# See https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
GS_PROJECT_ID = os.environ.get("GS_PROJECT_ID")
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
GS_LOCATION = os.environ.get("GS_LOCATION", "")
GS_CUSTOM_ENDPOINT = os.environ.get("GS_CUSTOM_ENDPOINT")
GS_MEDIA_BUCKET_NAME = os.environ.get("GS_MEDIA_BUCKET_NAME")
GS_AUTO_CREATE_BUCKET = get_bool_env("GS_AUTO_CREATE_BUCKET", False)
GS_QUERYSTRING_AUTH = get_bool_env("GS_QUERYSTRING_AUTH", False)
GS_DEFAULT_ACL = os.environ.get("GS_DEFAULT_ACL", None)
GS_MEDIA_CUSTOM_ENDPOINT = os.environ.get("GS_MEDIA_CUSTOM_ENDPOINT", None)
GS_EXPIRATION = timedelta(seconds=parse(os.environ.get("GS_EXPIRATION", "1 day")))
GS_FILE_OVERWRITE = get_bool_env("GS_FILE_OVERWRITE", True)

# If GOOGLE_APPLICATION_CREDENTIALS is set there is no need to load OAuth token
# See https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    GS_CREDENTIALS = os.environ.get("GS_CREDENTIALS")

# Azure Storage configuration
# See https://django-storages.readthedocs.io/en/latest/backends/azure.html
AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER = os.environ.get("AZURE_CONTAINER")
AZURE_SSL = os.environ.get("AZURE_SSL")

if AWS_STORAGE_BUCKET_NAME:
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
elif GS_BUCKET_NAME:
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

if AWS_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "swiftmovers.core.storages.S3MediaStorage"
elif GS_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "swiftmovers.core.storages.GCSMediaStorage"
elif AZURE_CONTAINER:
    DEFAULT_FILE_STORAGE = "swiftmovers.core.storages.AzureMediaStorage"

PLACEHOLDER_IMAGES = {
    32: "images/placeholder32.png",
    64: "images/placeholder64.png",
    128: "images/placeholder128.png",
    256: "images/placeholder256.png",
    512: "images/placeholder512.png",
    1024: "images/placeholder1024.png",
    2048: "images/placeholder2048.png",
    4096: "images/placeholder4096.png",
}


AUTHENTICATION_BACKENDS = [
    "swiftmovers.core.auth_backend.JSONWebTokenBackend",
    "swiftmovers.core.auth_backend.PluginBackend",
]

# Expired checkouts settings - defines after what time checkouts will be deleted
ANONYMOUS_CHECKOUTS_TIMEDELTA = timedelta(
    seconds=parse(os.environ.get("ANONYMOUS_CHECKOUTS_TIMEDELTA", "30 days"))
)
USER_CHECKOUTS_TIMEDELTA = timedelta(
    seconds=parse(os.environ.get("USER_CHECKOUTS_TIMEDELTA", "90 days"))
)
EMPTY_CHECKOUTS_TIMEDELTA = timedelta(
    seconds=parse(os.environ.get("EMPTY_CHECKOUTS_TIMEDELTA", "6 hours"))
)

# Exports settings - defines after what time exported files will be deleted
EXPORT_FILES_TIMEDELTA = timedelta(
    seconds=parse(os.environ.get("EXPORT_FILES_TIMEDELTA", "30 days"))
)

# CELERY SETTINGS
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = (
    os.environ.get("CELERY_BROKER_URL", os.environ.get("CLOUDAMQP_URL")) or ""
)
CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", None)
CELERY_TASK_ROUTES = {
    "swiftmovers.plugins.webhook.tasks.observability_reporter_task": {
        "queue": "observability"
    },
    "swiftmovers.plugins.webhook.tasks.observability_send_events": {
        "queue": "observability"
    },
}

# Expire orders task setting
BEAT_EXPIRE_ORDERS_AFTER_TIMEDELTA = timedelta(
    seconds=parse(os.environ.get("BEAT_EXPIRE_ORDERS_AFTER_TIMEDELTA", "5 minutes"))
)

# Defines after how many seconds should the task triggered by the Celery beat
# entry 'update-products-search-vectors' expire if it wasn't picked up by a worker.
BEAT_UPDATE_SEARCH_EXPIRE_AFTER_SEC = 20

# Defines the Celery beat scheduler entries.
#
# Note: if a Celery task triggered by a Celery beat entry has an expiration
# @task(expires=...), the Celery beat scheduler entry should also define
# the expiration value. This makes sure if the task or scheduling is wrapped
# by custom code (e.g., a swiftmovers fork), the expiration is still present.
CELERY_BEAT_SCHEDULE = {
    "delete-empty-allocations": {
        "task": "swiftmovers.warehouse.tasks.delete_empty_allocations_task",
        "schedule": timedelta(days=1),
    },
    "deactivate-preorder-for-variants": {
        "task": "swiftmovers.product.tasks.deactivate_preorder_for_variants_task",
        "schedule": timedelta(hours=1),
    },
    "delete-expired-reservations": {
        "task": "swiftmovers.warehouse.tasks.delete_expired_reservations_task",
        "schedule": timedelta(days=1),
    },
    "delete-expired-checkouts": {
        "task": "swiftmovers.checkout.tasks.delete_expired_checkouts",
        "schedule": crontab(hour=0, minute=0),
    },
    "delete-outdated-event-data": {
        "task": "swiftmovers.core.tasks.delete_event_payloads_task",
        "schedule": timedelta(days=1),
    },
    "deactivate-expired-gift-cards": {
        "task": "swiftmovers.giftcard.tasks.deactivate_expired_cards_task",
        "schedule": crontab(hour=0, minute=0),
    },
    "update-stocks-quantity-allocated": {
        "task": "swiftmovers.warehouse.tasks.update_stocks_quantity_allocated_task",
        "schedule": crontab(hour=0, minute=0),
    },
    "delete-old-export-files": {
        "task": "swiftmovers.csv.tasks.delete_old_export_files",
        "schedule": crontab(hour=1, minute=0),
    },
    "send-sale-toggle-notifications": {
        "task": "swiftmovers.discount.tasks.send_sale_toggle_notifications",
        "schedule": initiated_sale_webhook_schedule,
    },
    "update-products-search-vectors": {
        "task": "swiftmovers.product.tasks.update_products_search_vector_task",
        "schedule": timedelta(seconds=20),
        "options": {"expires": BEAT_UPDATE_SEARCH_EXPIRE_AFTER_SEC},
    },
    "expire-orders": {
        "task": "swiftmovers.order.tasks.expire_orders_task",
        "schedule": BEAT_EXPIRE_ORDERS_AFTER_TIMEDELTA,
    },
}

# The maximum wait time between each is_due() call on schedulers
# It needs to be higher than the frequency of the schedulers to avoid unnecessary
# is_due() calls
CELERY_BEAT_MAX_LOOP_INTERVAL = 300  # 5 minutes

EVENT_PAYLOAD_DELETE_PERIOD = timedelta(
    seconds=parse(os.environ.get("EVENT_PAYLOAD_DELETE_PERIOD", "14 days"))
)

# Observability settings
OBSERVABILITY_BROKER_URL = os.environ.get("OBSERVABILITY_BROKER_URL")
OBSERVABILITY_ACTIVE = bool(OBSERVABILITY_BROKER_URL)
OBSERVABILITY_REPORT_ALL_API_CALLS = get_bool_env(
    "OBSERVABILITY_REPORT_ALL_API_CALLS", False
)
OBSERVABILITY_MAX_PAYLOAD_SIZE = int(
    os.environ.get("OBSERVABILITY_MAX_PAYLOAD_SIZE", 25 * 1000)
)
OBSERVABILITY_BUFFER_SIZE_LIMIT = int(
    os.environ.get("OBSERVABILITY_BUFFER_SIZE_LIMIT", 1000)
)
OBSERVABILITY_BUFFER_BATCH_SIZE = int(
    os.environ.get("OBSERVABILITY_BUFFER_BATCH_SIZE", 100)
)
OBSERVABILITY_REPORT_PERIOD = timedelta(
    seconds=parse(os.environ.get("OBSERVABILITY_REPORT_PERIOD", "20 seconds"))
)
OBSERVABILITY_BUFFER_TIMEOUT = timedelta(
    seconds=parse(os.environ.get("OBSERVABILITY_BUFFER_TIMEOUT", "5 minutes"))
)
if OBSERVABILITY_ACTIVE:
    CELERY_BEAT_SCHEDULE["observability-reporter"] = {
        "task": "swiftmovers.plugins.webhook.tasks.observability_reporter_task",
        "schedule": OBSERVABILITY_REPORT_PERIOD,
        "options": {"expires": OBSERVABILITY_REPORT_PERIOD.total_seconds()},
    }
    if OBSERVABILITY_BUFFER_TIMEOUT < OBSERVABILITY_REPORT_PERIOD * 2:
        warnings.warn(
            "OBSERVABILITY_REPORT_PERIOD is too big compared to "
            "OBSERVABILITY_BUFFER_TIMEOUT. That can lead to a loss of events."
        )

# Change this value if your application is running behind a proxy,
# e.g. HTTP_CF_Connecting_IP for Cloudflare or X_FORWARDED_FOR
REAL_IP_ENVIRON = get_list(os.environ.get("REAL_IP_ENVIRON", "REMOTE_ADDR"))

# Slugs for menus pre-created in Django migrations
DEFAULT_MENUS = {"top_menu_name": "navbar", "bottom_menu_name": "footer"}

# Slug for channel pre-created in Django migrations
DEFAULT_CHANNEL_SLUG = os.environ.get("DEFAULT_CHANNEL_SLUG", "default-channel")

# Set this to `True` if you want to create default channel, warehouse, product type and
# category during migrations. It makes it easier for the users to create their first
# product.
POPULATE_DEFAULTS = get_bool_env("POPULATE_DEFAULTS", True)


#  Sentry
sentry_sdk.utils.MAX_STRING_LENGTH = 4096
SENTRY_DSN = os.environ.get("SENTRY_DSN")
SENTRY_OPTS = {"integrations": [CeleryIntegration(), DjangoIntegration()]}


def SENTRY_INIT(dsn: str, sentry_opts: dict):
    """Init function for sentry.

    Will only be called if SENTRY_DSN is not None, during core start, can be
    overriden in separate settings file.
    """
    sentry_sdk.init(dsn, release=__version__, **sentry_opts)
    ignore_logger("graphql.execution.utils")
    ignore_logger("graphql.execution.executor")


GRAPHQL_PAGINATION_LIMIT = 100
GRAPHQL_MIDDLEWARE: List[str] = []

# Set GRAPHQL_QUERY_MAX_COMPLEXITY=0 in env to disable (not recommended)
GRAPHQL_QUERY_MAX_COMPLEXITY = int(
    os.environ.get("GRAPHQL_QUERY_MAX_COMPLEXITY", 50000)
)

# Max number entities that can be requested in single query by Apollo Federation
#  protocol implements no securities on its own part - malicious actor
# may build a query that requests for potentially few thousands of entities.
# Set FEDERATED_QUERY_MAX_ENTITIES=0 in env to disable (not recommended)
FEDERATED_QUERY_MAX_ENTITIES = int(os.environ.get("FEDERATED_QUERY_MAX_ENTITIES", 100))

# configuration of the plugins

BUILTIN_PLUGINS = []

EXTERNAL_PLUGINS = []
installed_plugins = pkg_resources.iter_entry_points("swiftmovers.plugins")
for entry_point in installed_plugins:
    plugin_path = "{}.{}".format(entry_point.module_name, entry_point.attrs[0])
    if plugin_path not in BUILTIN_PLUGINS and plugin_path not in EXTERNAL_PLUGINS:
        if entry_point.name not in INSTALLED_APPS:
            INSTALLED_APPS.append(entry_point.name)
        EXTERNAL_PLUGINS.append(plugin_path)

PLUGINS = BUILTIN_PLUGINS + EXTERNAL_PLUGINS


if (
    not DEBUG
    and ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL
    and ALLOWED_CLIENT_HOSTS == get_list(_DEFAULT_CLIENT_HOSTS)
):
    raise ImproperlyConfigured(
        "Make sure you've added storefront address to ALLOWED_CLIENT_HOSTS "
        "if ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL is enabled."
    )

# Timeouts for webhook requests. Sync webhooks (eg. payment webhook) need more time
# for getting response from the server.
WEBHOOK_TIMEOUT = 10
WEBHOOK_SYNC_TIMEOUT = 20

# Since we split checkout complete logic into two separate transactions, in order to
# mimic stock lock, we apply short reservation for the stocks. The value represents
# time of the reservation in seconds.
RESERVE_DURATION = 45

# Initialize a simple and basic Jaeger Tracing integration
# for open-tracing if enabled.
#
# Refer to our guide on https://docs.swiftmovers.io/docs/next/guides/opentracing-jaeger/.
#
# If running locally, set:
#   JAEGER_AGENT_HOST=localhost
if "JAEGER_AGENT_HOST" in os.environ:
    jaeger_client.Config(
        config={
            "sampler": {"type": "const", "param": 1},
            "local_agent": {
                "reporting_port": os.environ.get(
                    "JAEGER_AGENT_PORT", jaeger_client.config.DEFAULT_REPORTING_PORT
                ),
                "reporting_host": os.environ.get("JAEGER_AGENT_HOST"),
            },
            "logging": get_bool_env("JAEGER_LOGGING", False),
        },
        service_name="swiftmovers",
        validate=True,
    ).initialize_tracer()


# Some cloud providers (Heroku) export REDIS_URL variable instead of CACHE_URL
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHE_URL = os.environ.setdefault("CACHE_URL", REDIS_URL)
CACHES = {"default": django_cache_url.config()}
CACHES["default"]["TIMEOUT"] = parse(os.environ.get("CACHE_TIMEOUT", "7 days"))

JWT_EXPIRE = True
JWT_TTL_ACCESS = timedelta(seconds=parse(os.environ.get("JWT_TTL_ACCESS", "5 minutes")))
JWT_TTL_APP_ACCESS = timedelta(
    seconds=parse(os.environ.get("JWT_TTL_APP_ACCESS", "5 minutes"))
)
JWT_TTL_REFRESH = timedelta(seconds=parse(os.environ.get("JWT_TTL_REFRESH", "30 days")))


JWT_TTL_REQUEST_EMAIL_CHANGE = timedelta(
    seconds=parse(os.environ.get("JWT_TTL_REQUEST_EMAIL_CHANGE", "1 hour")),
)

CHECKOUT_PRICES_TTL = timedelta(
    seconds=parse(os.environ.get("CHECKOUT_PRICES_TTL", "1 hour"))
)

# The maximum SearchVector expression count allowed per index SQL statement
# If the count is exceeded, the expression list will be truncated
INDEX_MAXIMUM_EXPR_COUNT = 4000

# Maximum related objects that can be indexed in an order
SEARCH_ORDERS_MAX_INDEXED_TRANSACTIONS = 20
SEARCH_ORDERS_MAX_INDEXED_PAYMENTS = 20
SEARCH_ORDERS_MAX_INDEXED_DISCOUNTS = 20
SEARCH_ORDERS_MAX_INDEXED_LINES = 100

# Maximum related objects that can be indexed in a product
PRODUCT_MAX_INDEXED_ATTRIBUTES = 1000
PRODUCT_MAX_INDEXED_ATTRIBUTE_VALUES = 100
PRODUCT_MAX_INDEXED_VARIANTS = 1000


# Patch SubscriberExecutionContext class from `graphql-core-legacy` package
# to fix bug causing not returning errors for subscription queries.

executor.SubscriberExecutionContext = PatchedSubscriberExecutionContext  # type: ignore

# Optional queue names for Celery tasks.
# Set None to route to the default queue, or a string value to use a separate one
#
# Queue name for update search vector
UPDATE_SEARCH_VECTOR_INDEX_QUEUE_NAME = os.environ.get(
    "UPDATE_SEARCH_VECTOR_INDEX_QUEUE_NAME", None
)
# Queue name for "async webhook" events
WEBHOOK_CELERY_QUEUE_NAME = os.environ.get("WEBHOOK_CELERY_QUEUE_NAME", None)

# Lock time for request password reset mutation per user (seconds)
RESET_PASSWORD_LOCK_TIME = parse(
    os.environ.get("RESET_PASSWORD_LOCK_TIME", "15 minutes")
)

