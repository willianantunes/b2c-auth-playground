import os

from logging import Formatter
from pathlib import Path

from b2c_auth_playground.apps.core.apps import CoreConfig

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-c=%dkk#bxs_og2!=q@en!en)(412xa$oueg%8aofr!m*26ad=("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    CoreConfig.name,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "b2c_auth_playground.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "b2c_auth_playground.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Logging
# https://docs.djangoproject.com/en/3.1/topics/logging/


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": Formatter,
            "format": "%(asctime)s - level=%(levelname)s - %(name)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "": {"level": os.getenv("ROOT_LOG_LEVEL", "INFO"), "handlers": ["console"]},
        "b2c_auth_playground": {
            "level": os.getenv("PROJECT_LOG_LEVEL", "DEBUG"),
            "handlers": ["console"],
            "propagate": False,
        },
        "django": {"level": os.getenv("DJANGO_LOG_LEVEL", "INFO"), "handlers": ["console"]},
        "django.db.backends": {"level": os.getenv("DJANGO_DB_BACKENDS_LOG_LEVEL", "INFO"), "handlers": ["console"]},
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#####
# Custom settings for B2C

B2B_TENANT = "xptoorg"
authority_template = f"https://{B2B_TENANT}.b2clogin.com/{B2B_TENANT}.onmicrosoft.com/{{user_flow}}"

# In order to communicate with MS

B2C_YOUR_APP_CLIENT_APPLICATION_ID = "32c47165-ef06-4cfd-80ef-ca3d2b282cc8"
B2C_YOUR_APP_CLIENT_CREDENTIAL = ".m97Q~uOj2PohUcoFiVXCaGa21-rC.EU.mriy"

B2C_YOUR_APP_RESOURCE_OWNER_APPLICATION_ID = "d4be734f-8746-4738-8f84-726bc46abae0"
B2C_YOUR_APP_RESOURCE_CLIENT_CREDENTIAL = "8oa7Q~FISBxt~CKKitKEt96cmMdAmKR1gKa8D"

# b2c-test-single-tenant
# B2C_YOUR_APP_CLIENT_APPLICATION_ID = "8a2e4f9f-550b-4b9a-a74e-673790af1e3d"
# B2C_YOUR_APP_CLIENT_CREDENTIAL = "WnU7Q~bTc1dX5GxS.3dQfBeI_SG2_XJ6Lz8Xw"

# b2c-test-multitenant
# B2C_YOUR_APP_CLIENT_APPLICATION_ID = "3e9263cd-657e-4654-bf8c-aecae4c558e6"
# B2C_YOUR_APP_CLIENT_CREDENTIAL = "QX07Q~eVOiZfSW-LzFWy6.Fu6DvZbUAdaxbqI"

B2C_YOUR_APP_APPLICATION_ID_URI = f"https://xptoorg.onmicrosoft.com/{B2C_YOUR_APP_CLIENT_APPLICATION_ID}"


# <QueryDict: {'error': ['invalid_request'], 'error_description': ["AADB2C90117: The scope 'User.ReadBasic.All' provided in the request is not supported.\r\nCorrelation ID: 4f20b0aa-2e50-4508-8fde-3f9aca1e20de\r\nTimestamp: 2021-09-23 17:09:55Z\r\n"], 'state': ['gVYBafGhXCPFcHLK']}>
# https://stackoverflow.com/a/45853520/3899136
# https://stackoverflow.com/a/62693315/3899136
# https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-permissions-and-consent#openid-connect-scopes
# You don't need to add ['profile', 'offline_access', 'openid'] because MSAL do it for you, just add custom scopes here!
# At the end, if you include `email`, MSAL will understand: ['profile', 'offline_access', 'openid', 'email']
B2C_SCOPES = [
    # You should add this permission to your App to receive an `access_token`!
    # "https://xptoorg.onmicrosoft.com/app-be-xpto-23092021/XPTO.Read.Situations"
]
B2C_SCOPES_RESOURCE_OWNER = [
    "openid",
    B2C_YOUR_APP_RESOURCE_OWNER_APPLICATION_ID,
]

# Authorities
USER_FLOWS_SIGN_UP_SIGN_IN = "B2C_1_sign-in-sign-up"
USER_FLOWS_PROFILE_EDITING = "B2C_1_profile_editing"
USER_FLOWS_RESOURCE_OWNER = "B2C_1_resource-owner"

B2C_AUTHORITY_SIGN_UP_SIGN_IN = authority_template.format(user_flow=USER_FLOWS_SIGN_UP_SIGN_IN)
B2C_AUTHORITY_PROFILE_EDITING = authority_template.format(user_flow=USER_FLOWS_PROFILE_EDITING)
B2C_AUTHORITY_RESOURCE_OWNER = authority_template.format(user_flow=USER_FLOWS_RESOURCE_OWNER)
