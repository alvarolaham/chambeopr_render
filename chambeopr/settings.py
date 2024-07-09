from pathlib import Path
import environ

# Initialize environment variables
env = environ.Env()
# Add a print statement to confirm the location of the .env file
environ.Env.read_env(env_file=Path(__file__).resolve().parent.parent / '.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    "myapp",
    "social_django",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "anymail",  # Add Anymail to the installed apps
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

ROOT_URLCONF = "chambeopr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# settings.py

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "myapp" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Ensure that you also have the following settings
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# Social Authentication
LOGIN_URL = "login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

# Email settings with Anymail (Mailjet)
EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
ANYMAIL = {
    "MAILJET_API_KEY": env("MAILJET_API_KEY"),
    "MAILJET_SECRET_KEY": env("MAILJET_SECRET_KEY"),
}
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="chambeopr@proton.me")

AUTH_USER_MODEL = "myapp.MyUser"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)  # Set to True if using HTTPS

# Template paths configuration
TEMPLATE_PATHS = {
    'signup': 'myapp/accounts/signup.html',
    'login': 'myapp/accounts/login.html',
    'password_reset': 'myapp/accounts/password_reset.html',
    'password_reset_code': 'myapp/accounts/password_reset_code.html',
    'password_reset_confirm': 'myapp/accounts/password_reset_confirm.html',
    'password_reset_complete': 'myapp/accounts/password_reset_complete.html',
    'password_reset_done': 'myapp/accounts/password_reset_done.html',
    'password_reset_email': 'myapp/accounts/password_reset_email.txt',
    'delete_account': 'myapp/accounts/delete_account.html',
    'home_services': 'myapp/services/home_services.html',
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
