import json
from datetime import date

import httpx
from fastapi import FastAPI

from config import settings
from redis import redis_pool


app = FastAPI()

async def get_value_from_cache(key: str) -> str:
    """
    Retrieve value from redis cache for key
    """
    value = await app.state.redis.get(key)
    return value

async def set_cache(key: str, value: str) -> None:
    """
    Set redis cache value for the key
    """
    await app.state.redis.set(key, value)

def get_currencies_supported_key() -> str:
    """
    Key string concatenated to a date for today e.g currencies_2021-03-17
    **Assumption these do not get updated often.
    """
    today = str(date.today())
    key = f"currencies_{today}"
    return key

async def get_request(client, url) -> dict:
    """
    Make get request to the url
    """
    resp = await client.get(url)
    return resp.json()

async def fetch_currencies() -> dict:
    """
    Fetch supported currencies.
    """
    async with httpx.AsyncClient() as client:
        url = f"{settings.base_api_url}/currencies.json"
        result = await get_request(client, url)
        return result

async def get_supported_currencies() -> str:
    """
    Fetch currencies supported by Exchange Rates API.
    If there is a cached response for the supported currencies today, it is returned
    Otherwise a request is sent to the Exchange rate API and response returned.
    """
    # Check for cached currencies before fetching
    key = get_currencies_supported_key()
    cached_value = await get_value_from_cache(key)
    if cached_value:
        return json.loads(cached_value)
    else:
        # No cached value found
        res = await fetch_currencies()
        if res:
            # Cache result for supported currencies today
            await set_cache(key, json.dumps(res))
        return res

@app.get("/currencies/")
async def list_currencies():
    """
    Currencies supported for conversions.
    """
    return await get_supported_currencies()

@app.on_event("startup")
async def create_redis():
    app.state.redis = await redis_pool()

@app.on_event("shutdown")
async def close_redis():
    app.state.redis.close()
