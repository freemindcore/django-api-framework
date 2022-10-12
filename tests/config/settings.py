"""
With these settings, tests run faster.
"""

# Admin API auto-generation settings
AUTO_ADMIN_ENABLED_ALL_APPS = True
AUTO_ADMIN_INCLUDE_APPS = []
AUTO_ADMIN_EXCLUDE_APPS = []

# Django Settings
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "ninja_extra",
    "tests.easy_app",
    "easy",
)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

USE_I18N = True
USE_TZ = True
LANGUAGE_CODE = "en-us"

STATIC_URL = "/static/"
ROOT_URLCONF = "tests.easy_app.urls"

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# DB
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        # "TEST": {
        #     # this gets you in-memory sqlite for faster testing
        #     "ENGINE": "django.db.backends.sqlite3",
        # },
    }
}

# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
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

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


# Security
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "not very secret in tests"

# Debug
DEBUG_PROPAGATE_EXCEPTIONS = True
