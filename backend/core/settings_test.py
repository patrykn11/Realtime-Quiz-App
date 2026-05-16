from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres_test',       
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'db',                  
        'PORT': '5432',
    }
}

REDIS_HOST = "redis"               
REDIS_PORT = 6380                   
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


DEBUG = False
ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}