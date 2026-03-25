"""CLI input validation helpers."""

from __future__ import annotations

import re
from typing import Optional

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> None:
    normalized_symbol = symbol.strip().upper()
    normalized_side = side.strip().upper()
    normalized_type = order_type.strip().upper()

    if not normalized_symbol:
        raise ValueError("Symbol is required.")

    if not SYMBOL_PATTERN.fullmatch(normalized_symbol):
        raise ValueError(
            "Invalid symbol format. Use a Binance futures symbol such as BTCUSDT."
        )

    if normalized_side not in {"BUY", "SELL"}:
        raise ValueError(f"Invalid side: {side}. Must be BUY or SELL.")

    if normalized_type not in {"MARKET", "LIMIT", "STOP_LIMIT"}:
        raise ValueError(
            f"Invalid type: {order_type}. Must be MARKET, LIMIT, or STOP_LIMIT."
        )

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    if normalized_type == "LIMIT" and (price is None or price <= 0):
        raise ValueError("Price must be a positive number for LIMIT orders.")

    if normalized_type == "MARKET" and price is not None:
        raise ValueError("Price must not be supplied for MARKET orders.")

    if normalized_type == "STOP_LIMIT" and (price is None or price <= 0):
        raise ValueError("Price must be a positive number for STOP_LIMIT orders.")

    if normalized_type == "STOP_LIMIT" and (stop_price is None or stop_price <= 0):
        raise ValueError("stop_price must be a positive number for STOP_LIMIT orders.")

    if normalized_type in {"MARKET", "LIMIT"} and stop_price is not None:
        raise ValueError("stop_price must only be supplied for STOP_LIMIT orders.")
