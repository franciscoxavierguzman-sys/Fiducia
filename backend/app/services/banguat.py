from decimal import Decimal
import re

import httpx

BANGUAT_EXCHANGE_RATE_URL = "https://www.banguat.gob.gt/tipo_cambio"


def get_banguat_usd_gtq_rate() -> Decimal:
    response = httpx.get(BANGUAT_EXCHANGE_RATE_URL, timeout=4.0)
    response.raise_for_status()
    match = re.search(r"\b\d+\.\d{4,6}\b", response.text)
    if match is None:
        raise ValueError("Banguat exchange rate was not found")
    return Decimal(match.group(0))
