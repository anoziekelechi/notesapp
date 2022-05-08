from notesapp.settings.common import *

DEBUG = True
ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'notesapp',
        'USER':'emmanuel',
        'PASSWORD':'kennedy1986',
        'HOST':'localhost',
    }
}