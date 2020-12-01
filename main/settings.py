import os
from decouple import config, Csv
from dj_database_url import parse as db_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.postgres',
    'rest_framework',
    'upsets.apps.UpsetsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'main.wsgi.application'

# For now all the endpoints are public and read-only,
# we do not care about cross-origin requests
CORS_ALLOW_ALL_ORIGINS = True

# API KEYS
TWITTER_BEARER_TOKEN = config('TWITTER_BEARER_TOKEN', default=None)

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if config('GAE_APPLICATION', default=None):
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': '/cloudsql/'+config('DB_PROD_CONNECTION_NAME'),
            'NAME': config('DB_PROD_DATABASE'),
            'USER': config('DB_PROD_USERNAME'),
            'PASSWORD': config('DB_PROD_PASSWORD'),
        }
    }
elif config('DB_MODE', default='local') == 'prod':
    # Running in locally, but access the Google Cloud SQL instance in
    # production via the proxy (more details in README)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'NAME': config('DB_PROD_DATABASE'),
            'USER': config('DB_PROD_USERNAME'),
            'PASSWORD': config('DB_PROD_PASSWORD'),
        }
    }
else:
    # Running in development, so use the local Postgres database.
    DATABASES = {
        'default': config('LOCAL_DATABASE_URL', cast=db_url)
    }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('[%(asctime)s] [%(process)d] [%(levelname)s] ' +
                       '[%(name)s] pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S %z'
        },
        'simple': {
            'format': '	%(name)s %(asctime)s %(levelname)-8s %(message)s'
        },
        'console_color': {
            '()': 'colorlog.ColoredFormatter',
            'format': ('%(log_color)s%(name)s %(asctime)s %(levelname)-8s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'log_colors': {
                'DEBUG':    'thin_white',
                'INFO':     'white',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            }
        },
        'console_db_queries': {
            '()': 'colorlog.ColoredFormatter',
            'format': ('%(log_color)s%(name)s %(asctime)s %(levelname)-8s %(message).'+config('DB_LOGS_MAX_CHARS', default='120')+'s'),
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'log_colors': {
                'DEBUG':    'cyan',
            }
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'prod_console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_false']
        },
        'debug_console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console_color',
            'filters': ['require_debug_true']
        },
        'db_queries_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console_db_queries',
            'filters': ['require_debug_true']
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['prod_console', 'debug_console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['prod_console', 'debug_console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.db.backends': {
            'handlers': ['prod_console', 'debug_console'] +
                        (['db_queries_console'] if config('DB_LOGS', default=False) else []),
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {
            'handlers': ['mail_admins', 'debug_console', 'prod_console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'data_processing': {
            'handlers': ['mail_admins', 'debug_console', 'prod_console'],
            'level': 'DEBUG'
        }
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static'


REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
    }
}
