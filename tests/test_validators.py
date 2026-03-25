"""Unit tests for CLI input validation."""

from __future__ import annotations

import unittest

from bot.validators import validate_order_params


class ValidateOrderParamsTests(unittest.TestCase):
    def test_market_order_accepts_valid_inputs(self) -> None:
        validate_order_params("BTCUSDT", "BUY", "MARKET", 0.002)

    def test_invalid_side_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid side"):
            validate_order_params("BTCUSDT", "HOLD", "MARKET", 0.002)

    def test_limit_order_requires_price(self) -> None:
        with self.assertRaisesRegex(ValueError, "Price must be a positive number for LIMIT"):
            validate_order_params("BTCUSDT", "SELL", "LIMIT", 0.002)

    def test_market_order_rejects_price(self) -> None:
        with self.assertRaisesRegex(ValueError, "Price must not be supplied for MARKET"):
            validate_order_params("BTCUSDT", "BUY", "MARKET", 0.002, price=90000)

    def test_stop_limit_requires_price_and_stop_price(self) -> None:
        with self.assertRaisesRegex(ValueError, "Price must be a positive number for STOP_LIMIT"):
            validate_order_params("BTCUSDT", "SELL", "STOP_LIMIT", 0.002, stop_price=90500)

        with self.assertRaisesRegex(ValueError, "stop_price must be a positive number"):
            validate_order_params("BTCUSDT", "SELL", "STOP_LIMIT", 0.002, price=90000)

    def test_stop_price_only_allowed_for_stop_limit(self) -> None:
        with self.assertRaisesRegex(ValueError, "stop_price must only be supplied"):
            validate_order_params(
                "BTCUSDT",
                "SELL",
                "LIMIT",
                0.002,
                price=90000,
                stop_price=90500,
            )

    def test_symbol_format_is_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid symbol format"):
            validate_order_params("BTC-USD", "BUY", "MARKET", 0.002)


if __name__ == "__main__":
    unittest.main()
