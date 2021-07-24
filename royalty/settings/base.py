"""
Django settings for royalty project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# create primary key ba default   :https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =True #os.getenv('DEBUG')

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST'), '127.0.0.1','localhost']



# Application definition

INSTALLED_APPS = [
    'django_cleanup.apps.CleanupConfig', # should go after your apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'whitenoise.runserver_nostatic', 
    'royalty_app',  

    'django_email_verification',
    'storages', #AWS 
    'django_filters',

    "debug_toolbar", #use to generate the toolbar to view bugs

]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'royalty.urls'

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

WSGI_APPLICATION = 'royalty.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#postgres://atzrmjyxcymhtd:c73ec4bb9461274ff04a5fad3951cb0da2b0fcd13c60936d86b5d1cb69905b71@ec2-54-83-82-187.compute-1.amazonaws.com:5432/db309563b7l4j5

#see https://www.enterprisedb.com/postgres-tutorials/how-use-postgresql-django


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_NAME'),#'db309563b7l4j5',
        'USER': os.getenv('POSTGRES_USER'),#'atzrmjyxcymhtd',
        'PASSWORD': os.getenv('POSTGRES_PWD'),#'c73ec4bb9461274ff04a5fad3951cb0da2b0fcd13c60936d86b5d1cb69905b71',
        'HOST': os.getenv('POSTGRES_HOST'),#'ec2-54-83-82-187.compute-1.amazonaws.com',
        'PORT': '5432',
    }
    
}
'''



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
AUTH_USER_MODEL = 'royalty_app.User'

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/



#S3 BUCKETS CONFIG

AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME=os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_FILE_OVERWRITE = False # prevent user from overwritting
AWS_DEFAULT_ACL= None

use_aws = True
if use_aws:
    #static file

    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    '''
    The below code can be used. it helps secure the static file. Yet, it slow down the app
    STATIC_URL = 'static/'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]
    STATICFILES_STORAGE = 'royalty_app.storage_backends.StaticRootS3BotoStorage'
    '''

    #Media file
    MEDIA_URL = 'media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    DEFAULT_FILE_STORAGE = 'royalty_app.storage_backends.MediaRootS3BotoStorage'
 
else:
    #static file
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    #Media file
    MEDIA_URL = 'media/' # on the display, "media" appear in the url , it's just a question of appearance, 
    MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
 
#AWS_QUERYSTRING_AUTH = False


DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'PNG': ".png"} #used in order for the profile pict to be saved as PNG and not APNG

# Steps to verify your email:
def verified_callback(user):
    user.is_active = True

EMAIL_VERIFIED_CALLBACK = verified_callback
EMAIL_FROM_ADDRESS = os.getenv('EMAIL_FROM')
EMAIL_MAIL_SUBJECT = 'SwissRoy- Confirm your email'
EMAIL_MAIL_HTML = 'password_confirmation/mail_body.html'
EMAIL_MAIL_PLAIN = 'password_confirmation/mail_body.txt'
EMAIL_TOKEN_LIFE = 60 * 60
EMAIL_PAGE_TEMPLATE = 'password_confirmation/confirm_template.html'
EMAIL_PAGE_DOMAIN = 'http://localhost:8000/' 

# For Django Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_ID') 
DEFAULT_FROM_EMAIL= os.getenv('EMAIL_FROM') 
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PW')


#Used to debug
INTERNAL_IPS=[
    os.getenv('ALLOWED_HOST'),
    '127.0.0.1',
    'localhost'
]

#CAPTCHA
GOOGLE_RECAPTCHA_SITE_KEY=os.getenv('GOOGLE_RECAPTCHA_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY =os.getenv('GOOGLE_RECAPTCHA_SECRET_KEY')