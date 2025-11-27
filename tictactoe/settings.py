

from pathlib import Path
from environ import Env

env = Env()
Env.read_env()
ENVIRONMENT = env('ENVIRONMENT', default='production')
ENVIRONMENT = 'production'

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['localhost','127.0.0.1','https://tictactoe-game-tls9.onrender.com']


# Application definition
INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'crispy_bootstrap5',
    'crispy_forms',
    'django_recaptcha',
    'channels',
    'accounts',
    'game',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'tictactoe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

ASGI_APPLICATION = 'tictactoe.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
if ENVIRONMENT == 'development':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    import dj_database_url
    DATABASES = {
        'default' : dj_database_url.parse(env('DATABASE_URL'))
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#static
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

#Setting
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'menu'
LOGIN_URL = 'login'

#recaptcha
RECAPTCHA_PUBLIC_KEY = '6LdmGRcsAAAAAIY47j76VFe1FQH5B2V9LXtydQMZ'
RECAPTCHA_PRIVATE_KEY = '6LdmGRcsAAAAAAkDdbklzIE-FTrfDCXlBNBJn9XV'

#backend email
AUTHENTICATION_BACKENDS = ['accounts.backends.EmailBackend']
AUTH_USER_MODEL = 'accounts.CustomUser'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

##EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_FROM = env('EMAIL_ADDRESS')
EMAIL_HOST_USER = env('EMAIL_ADDRESS')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = f'TicTacToe {env('EMAIL_ADDRESS')}'
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
SITE_ID = 1

#channel-redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ['redis://default:jLphbMAHyLvZlhBM8jNuWSGLUvtBHS5D@redis-17501.c85.us-east-1-2.ec2.cloud.redislabs.com:17501/0'],
            "prefix": "channels:",
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://default:jLphbMAHyLvZlhBM8jNuWSGLUvtBHS5D@redis-17501.c85.us-east-1-2.ec2.cloud.redislabs.com:17501/0',
        'KEY_PREFIX': 'cache:', 
    }
}

PASSWORD_RESET_TIMEOUT  = 14400