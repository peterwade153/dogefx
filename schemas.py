from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, validator


class ExchangeItem(BaseModel):
    """
    Exchange item to convert from currency to another
    attrs:
        currency_from: Currency a given amount is exchanged from
        currency_to: Currency to which a given amount is exchanged
        amount: Amount to be exchanged
        historic_date: Date for which to make currency exchange is to be made
    """
    currency_from: str
    currency_to: str
    amount: float
    historic_date: Optional[date] = None

    @validator("historic_date", pre=True)
    def ensure_date_format(cls, value):
        if value:
            return datetime.strptime(value, "%Y-%m-%d").date()
