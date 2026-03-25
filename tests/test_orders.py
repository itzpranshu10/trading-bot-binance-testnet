"""Unit tests for order request construction."""

from __future__ import annotations

import logging
import unittest

from bot.orders import OrderManager


class FakeClient:
    def __init__(self) -> None:
        self.last_params = None
        self.response = {"status": "NEW"}
        self.raise_error = None

    def futures_create_order(self, **kwargs):
        self.last_params = kwargs
        if self.raise_error is not None:
            raise self.raise_error
        return self.response


class OrderManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("trading_bot")
        self.original_disabled = self.logger.disabled
        self.logger.disabled = True

    def tearDown(self) -> None:
        self.logger.disabled = self.original_disabled

    def test_market_order_builds_expected_params(self) -> None:
        client = FakeClient()
        manager = OrderManager(client)

        response = manager.place_futures_order("BTCUSDT", "BUY", "MARKET", 0.002)

        self.assertEqual({"status": "NEW"}, response)
        self.assertEqual(
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": 0.002,
            },
            client.last_params,
        )

    def test_limit_order_builds_expected_params(self) -> None:
        client = FakeClient()
        manager = OrderManager(client)

        manager.place_futures_order("BTCUSDT", "SELL", "LIMIT", 0.002, price=90000)

        self.assertEqual(
            {
                "symbol": "BTCUSDT",
                "side": "SELL",
                "type": "LIMIT",
                "quantity": 0.002,
                "price": "90000",
                "timeInForce": "GTC",
            },
            client.last_params,
        )

    def test_stop_limit_order_maps_to_binance_stop_type(self) -> None:
        client = FakeClient()
        manager = OrderManager(client)

        manager.place_futures_order(
            "BTCUSDT",
            "SELL",
            "STOP_LIMIT",
            0.002,
            price=90000,
            stop_price=90500,
        )

        self.assertEqual(
            {
                "symbol": "BTCUSDT",
                "side": "SELL",
                "type": "STOP",
                "quantity": 0.002,
                "price": "90000",
                "stopPrice": "90500",
                "timeInForce": "GTC",
            },
            client.last_params,
        )

    def test_unexpected_error_is_returned_as_error_dict(self) -> None:
        client = FakeClient()
        client.raise_error = RuntimeError("boom")
        manager = OrderManager(client)

        response = manager.place_futures_order("BTCUSDT", "BUY", "MARKET", 0.002)

        self.assertEqual({"error": "boom"}, response)


if __name__ == "__main__":
    unittest.main()
