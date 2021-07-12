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

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
#ALLOWED_HOSTS = ['hellotest666.herokuapp.com','localhost']

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'heb8ab9md',
    'API_KEY': '826471698252942',
    'API_SECRET': 'rkOC3zdEmILXcGYxhg3sdiNmF9M',
}




DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
