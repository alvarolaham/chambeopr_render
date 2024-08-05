import os
from pathlib import Path
import environ
import dj_database_url

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(env_file=Path(__file__).resolve().parent.parent / ".env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        "bookiao.herokuapp.com",
        "bookiao-ae61444b7814.herokuapp.com",
        "localhost",
        "127.0.0.1",
        "www.bookiao.com",
        "bookiao.com"
    ],
)

# Application definition
INSTALLED_APPS = [
    "myapp",
    "anymail",
    "storages",  # Add storages for AWS S3
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chambeopr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "chambeopr.wsgi.application"

# Database configuration
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
}

TEST_RUNNER = "myapp.tests.test_runner.PostgresTestRunner"

# AWS S3 configuration
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = "us-east-1"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

# Static and media files configuration
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "myapp" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Password validation
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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Authentication settings
LOGIN_URL = "login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)

# Email settings
EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
ANYMAIL = {
    "MAILJET_API_KEY": env("MAILJET_API_KEY"),
    "MAILJET_SECRET_KEY": env("MAILJET_SECRET_KEY"),
}
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

AUTH_USER_MODEL = "myapp.MyUser"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Session settings
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
SESSION_SAVE_EVERY_REQUEST = True

# Template paths
TEMPLATE_PATHS = {
    "signup": "myapp/accounts/signup.html",
    "login": "myapp/accounts/login.html",
    "password_reset": "myapp/accounts/password_reset.html",
    "password_reset_code": "myapp/accounts/password_reset_code.html",
    "password_reset_confirm": "myapp/accounts/password_reset_confirm.html",
    "password_reset_complete": "myapp/accounts/password_reset_complete.html",
    "password_reset_done": "myapp/accounts/password_reset_done.html",
    "password_reset_email": "myapp/accounts/password_reset_email.txt",
    "delete_account": "myapp/accounts/delete_account.html",
    "home_services": "myapp/services/home_services.html",
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'myapp': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
