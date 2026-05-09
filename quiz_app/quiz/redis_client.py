import redis
import redis.asyncio as async_redis
from django.conf import settings


def get_redis_url():
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"


redis_client = redis.from_url(get_redis_url(), decode_responses=True)
async_redis_client = async_redis.from_url(get_redis_url(), decode_responses=True)
