import os

ROOT = os.path.dirname(os.path.dirname(__file__))

DEBUG = os.environ.get('DEBUG', True)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'login'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

INSTALLED_APPS = [
    'rest_framework',
    'api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.OrderingFilter'),
    'EXCEPTION_HANDLER': 'api.exceptions.api_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
}

ROOT_URLCONF = 'project.urls'

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

EMAIL_FROM = os.environ.get('MAIL_FROM', 'notifications@water-dragon-api.localhost')
EMAIL_HOST = os.environ.get('MAIL_HOST', '0.0.0.0')
EMAIL_PORT = os.environ.get('MAIL_PORT', 1025)
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
EMAIL_HOST_USER = os.environ.get('MAIL_USER', '')
EMAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)
EMAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)

MINIO_ACCESSKEY = os.environ.get('MINIO_ACCESS_KEY', 'access-key')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'test')
MINIO_SERVER = os.environ.get('MINIO_SERVER', '0.0.0.0:9000')
MINIO_SECRET = os.environ.get('MINIO_SECRET_KEY', 'secret-key')
MINIO_SECURE = os.environ.get('MINIO_SECURE', False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'db'),
        'USER': os.environ.get('DB_USER', 'db'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'secret'),
        'HOST': os.environ.get('DB_HOST', '0.0.0.0'),
        'PORT': os.environ.get('DB_PORT', '5432')
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SECRET_KEY = os.environ.get('SESSION_SECRET', 'secret')

SECURE_PROXY_SSL_HEADER = ['HTTP_X_FORWARDED_PROTO', 'https']
ALLOWED_HOSTS = ['*']
