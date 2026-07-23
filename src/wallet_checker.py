from datetime import date
from http import HTTPStatus

import requests

from coins import Coin
from logger import get_logger

logger = get_logger("wallet-checker-script")

STALE_CYCLES_LIMIT = 2
BLACKLIST_HOURS = 6


def _get_herominers_balance(coin: Coin) -> int | None:
    wallet_address = coin.wallet.split(".")[0]
    url = coin.api_url.format(wallet=wallet_address)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            stats = data.get("stats", {})
            if stats.get("hashrate", 1) == 0:
                logger.warning(f"{coin.name}: hashrate 0 na pool, possível estagnação.")
            return int(stats.get("balance", 0))
    except Exception as e:
        logger.error(f"Erro ao consultar HeroMiners para {coin.name}: {e}")
    return None


def _get_xdag_balance(coin: Coin) -> int | None:
    wallet_address = coin.wallet.split(".")[0]
    url = coin.api_url.format(wallet=wallet_address)
    today = date.today().isoformat()
    try:
        response = requests.get(
            url,
            params={"addresses_directions[]": "input", "addresses_date_from": today},
            timeout=10,
        )
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            entries = data.get("block_as_address", [])
            total = sum(int(float(e.get("amount", 0)) * 1e9) for e in entries if e.get("direction") == "input")
            return total
    except Exception as e:
        logger.error(f"Erro ao consultar XDAG Explorer para {coin.name}: {e}")
    return None


def get_balance(coin: Coin) -> int | None:
    if coin == Coin.XDAG:
        return _get_xdag_balance(coin)
    return _get_herominers_balance(coin)
