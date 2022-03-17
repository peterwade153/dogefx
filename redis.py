from aioredis import Redis, from_url

from config import settings


async def redis_pool() -> Redis:
    """
    Create a Redis client backed by a pool of connections
    """
    redis = await from_url(settings.redis_url)
    return redis
