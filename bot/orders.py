"""Order placement logic for market, limit, and stop-limit orders."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from binance.exceptions import BinanceAPIException, BinanceOrderException

logger = logging.getLogger("trading_bot")


class OrderManager:
    """High-level wrapper for Binance futures order placement."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def place_futures_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        normalized_type = order_type.upper()
        api_type = "STOP" if normalized_type == "STOP_LIMIT" else normalized_type
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": api_type,
            "quantity": quantity,
        }

        if normalized_type == "LIMIT":
            params["price"] = str(price)
            params["timeInForce"] = "GTC"

        if normalized_type == "STOP_LIMIT":
            if price is None:
                raise ValueError("price is required for STOP_LIMIT orders.")
            if stop_price is None:
                raise ValueError("stop_price is required for STOP_LIMIT orders.")
            params["price"] = str(price)
            params["stopPrice"] = str(stop_price)
            params["timeInForce"] = "GTC"

        logger.info("API Request: %s", params)

        try:
            response = self.client.futures_create_order(**params)
            logger.info("API Response: %s", response)
            return response
        except BinanceAPIException as exc:
            logger.error(
                "Binance API error while placing order. status=%s message=%s",
                exc.status_code,
                exc.message,
            )
            return {"error": exc.message, "status_code": exc.status_code}
        except BinanceOrderException as exc:
            logger.error("Binance order error while placing order: %s", exc)
            return {"error": str(exc)}
        except Exception as exc:
            logger.exception("Unexpected error while placing order.")
            return {"error": str(exc)}
