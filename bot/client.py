"""API authentication and Binance client setup."""

from __future__ import annotations

import logging

from binance.client import Client
from requests.exceptions import RequestException

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"
FUTURES_TESTNET_URL = f"{FUTURES_TESTNET_BASE_URL}/fapi"


class FuturesOnlyTestnetClient(Client):
    """Binance client variant that skips the default spot ping during initialization."""

    def ping(self):  # type: ignore[override]
        logger.info("Skipping default spot ping during client initialization.")
        return {}


class BinanceTestnetClient:
    """Thin wrapper around the Binance client configured for USDT-M futures testnet."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        self.client = FuturesOnlyTestnetClient(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,
        )
        self.client.FUTURES_TESTNET_URL = FUTURES_TESTNET_URL

        try:
            logger.info("Pinging Binance Futures Testnet at %s", FUTURES_TESTNET_URL)
            self.client.futures_ping()
            logger.info("Connected to Testnet at %s", FUTURES_TESTNET_BASE_URL)
        except RequestException as exc:
            logger.exception("Network error while connecting to Binance Futures Testnet.")
            raise ConnectionError(
                "Unable to reach Binance Futures Testnet. Check your network access and try again."
            ) from exc
        except Exception:
            logger.exception("Connection to Binance Futures Testnet failed.")
            raise
