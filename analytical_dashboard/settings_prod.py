# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    "default":{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dashboard_prod',
        'USER': 'postgres_user',
        'PASSWORD': 'pg123',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST':{
            'NAME':'dashboard_test'
        }
    }
}