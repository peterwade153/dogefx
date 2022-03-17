import json
from datetime import date

import httpx
from fastapi import Body, FastAPI

from config import settings
from redis import redis_pool
from schemas import ExchangeItem


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

def get_exchange_rate_key(item: ExchangeItem) -> str:
    """
    Generate a caching key for exchanging currency from one to another for today
    """
    key = f"{item.currency_from}_{item.currency_to}_{item.historic_date}"
    return key

async def fetch_exchange_conversion(item: ExchangeItem) -> dict:
    """
    Fetch exchange rates for conversion from one currency to another
    """
    async with httpx.AsyncClient() as client:
        url = f"{settings.base_api_url}/historical/{item.historic_date}"\
            f".json?app_id={settings.api_key}&base={item.currency_from}&symbols={item.currency_to}"
        result = await get_request(client, url)
        return result

async def currency_converter(item: ExchangeItem) -> float:
    """
    Converts an amount from one currency to a desired currency
    """
    result = 0.00
    amount = item.amount
    cache_key = get_exchange_rate_key(item)
    cached_exchange_rate = await get_value_from_cache(cache_key)
    if cached_exchange_rate:
        result = amount * float(cached_exchange_rate)
        return result
    # Fetch rate from API
    res = await fetch_exchange_conversion(item)
    if 'rates' in res:
        exchange_rate = res['rates'][item.currency_to]
        result =  exchange_rate * amount
        await set_cache(cache_key, str(exchange_rate))
    return result

@app.get("/currencies/")
async def list_currencies():
    """
    Endpoint returns Currencies supported for conversions.
    """
    return await get_supported_currencies()

@app.post("/convert/")
async def convert_currency(
    item: ExchangeItem = Body( 
        ...,
        examples={
            "normal": {
                "summary": "A conversion request",
                "description": "Converts from currency to another, on the current exchange rate",
                "value": { 
                    "currency_from": "GBP",
                    "currency_to": "USD",
                    "amount": 22,
                    }
                }, 
            "historic_request": {
                "summary": "A historic conversion request", 
                "description": "Converts from currency to another,"
                    "using exchange rate on the historic date. This goes back to 1st Jan 1999", 
                "value": { 
                    "currency_from": "GBP",
                    "currency_to": "USD",
                    "amount": 22,
                    "historic_date": "2022-01-17"
                    } 
                } 
            },
        ),
    ):
    """
    Converts from one currency to another using exchange rates
    from https://openexchangerates.org/ 
    """
    if item.historic_date is None:
        item.historic_date = str(date.today())
    result = await currency_converter(item)
    return result

@app.on_event("startup")
async def create_redis():
    app.state.redis = await redis_pool()

@app.on_event("shutdown")
async def close_redis():
    app.state.redis.close()
