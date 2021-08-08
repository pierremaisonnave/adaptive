"""
Production Settings for Heroku
"""
import environ

# If using in your own project, update the project namespace below
from royalty.settings.base import *

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# False if not in os.environ
DEBUG = env('DEBUG')

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

#ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
ALLOWED_HOSTS = [ '127.0.0.1','localhost','www.swissroy.ch','swissroy.ch','swissroy-public.herokuapp.com']
#ALLOWED_HOSTS = ['www.swissroy.ch','swissroy-public.herokuapp.com','swissroy.ch'],
#ALLOWED_HOSTS = ['hellotest666.herokuapp.com','localhost']

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
}






#S3 BUCKETS CONFIG


AWS_ACCESS_KEY_ID=env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME=env('AWS_STORAGE_BUCKET_NAME')


EMAIL_PAGE_DOMAIN ='https://www.swissroy.ch/' #'https://swissroy-public.herokuapp.com/' 
EMAIL_FROM_ADDRESS =env('EMAIL_FROM')

EMAIL_HOST_USER = env('EMAIL_ID') 
DEFAULT_FROM_EMAIL= env('EMAIL_FROM') 
EMAIL_HOST_PASSWORD = env('EMAIL_PW')

#CAPTCHA
GOOGLE_RECAPTCHA_SITE_KEY=env('GOOGLE_RECAPTCHA_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY =env('GOOGLE_RECAPTCHA_SECRET_KEY')
#conneciton to database
DATABASE_URL_VIEW=env("DATABASE_URL_VIEW")
