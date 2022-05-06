import os
import psycopg2.extensions
import datetime
from corsheaders.defaults import default_headers
import django_heroku
from urllib.parse import urlparse


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = str( os.environ.get('DJANGO_SECREY_KEY',"mylocalsecretkeyisbad!!")   ) 


#IF TRUE, USE THE PROD DATABASE, ELSE USE YOUR LOCAL SQLITE DB
#Automated environmental determination
HEROKU_PROD = str( os.environ.get('HEROKU_PRODUCTION',"NO") )
PRODUCTION = True if HEROKU_PROD=="YES" else False
DEBUG = False if HEROKU_PROD=="YES" else True


##############################################
####### HANDLE MEDIA STUFF HERE  #############
##############################################
if PRODUCTION == True:
    #ALL MEDIA WILL BE STORED IN AN AWS S3 BUCKET
    #VIEW THE AWS BUCKET DASHBOARD HERE WITH THE TEP AWS ACCT: https://s3.console.aws.amazon.com/s3/home?region=us-east-1#
    #VIEW OR CREATE YOUR AWS ACCESS KEYS HERE: https://console.aws.amazon.com/iam/home?#/users/tallyhq_app?section=security_credentials

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID','')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY','')
    AWS_STORAGE_BUCKET_NAME = 'pnc-tallyhq-public-bucket' 

    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {

        'CacheControl': 'max-age=86400',
    }
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'my_storage_backend.MediaStorage'
    AWS_DEFAULT_ACL = None

if PRODUCTION == False:
    ### FOR LOCAL DEVELOPMENT, MEDIA IS STORED IN A LOCAL MEDIA DIRECTORY 
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'

##############################################
########## END MEDIA #########################
##############################################


ALLOWED_HOSTS = ['*'] #,'.localhost','127.0.0.1','192.168.1.194']
#ALLOWED_HOSTS = ['localhost','127.0.0.1','gentle-crag-33999.herokuapp.com','192.168.1.194']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tallyhq',
]

MIDDLEWARE = [
    'tep.middleware.ThreadLocalUserMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'tep.urls'

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
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'tep.wsgi.application'




MANUAL_DB_URL = "postgres://gjkkiztnavaqsz:6d3c2b8e246c278d07020d5d5cfe98df21fe6b46bd38a25c9549b6bd3e456a54@ec2-107-22-228-141.compute-1.amazonaws.com:5432/dcp9cstoo90ebv"
FINAL_DB_URL = os.environ.get('HEROKU_POSTGRESQL_SILVER_URL',MANUAL_DB_URL)
parsed_url = urlparse(FINAL_DB_URL)


if PRODUCTION == True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': parsed_url.path.split('/')[-1],
            'USER': parsed_url.username,
            'PASSWORD':parsed_url.password,
            'HOST': parsed_url.hostname,
            'PORT': parsed_url.port,
        },
        'OPTIONS': {
            'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
        }
    }
else:
    DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR,'db.sqlite3')
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True




STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') #whitenoise uses this staticfiles directory
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'testlogger': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

#https://github.com/heroku/django-heroku. keep the staticfiles=False flag otherwise you get 500 error in prod
django_heroku.settings(locals(),staticfiles=False)
