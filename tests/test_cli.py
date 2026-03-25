"""CLI behavior tests using Typer's test runner."""

from __future__ import annotations

import logging
import os
import unittest
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

import cli as cli_module


class TradingBotCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.logger = logging.getLogger("trading_bot")
        self.original_disabled = self.logger.disabled
        self.logger.disabled = True

    def tearDown(self) -> None:
        self.logger.disabled = self.original_disabled

    def test_help_renders(self) -> None:
        result = self.runner.invoke(cli_module.app, ["--help"])

        self.assertEqual(0, result.exit_code)
        self.assertIn("Place a market, limit, or stop-limit order", result.output)

    def test_missing_credentials_fails_cleanly(self) -> None:
        with patch.dict(
            os.environ,
            {"BINANCE_API_KEY": "", "BINANCE_API_SECRET": ""},
            clear=False,
        ):
            result = self.runner.invoke(
                cli_module.app,
                ["--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--qty", "0.002"],
            )

        self.assertEqual(1, result.exit_code)
        self.assertIn("BINANCE_API_KEY or BINANCE_API_SECRET is missing", result.output)

    def test_validation_error_is_shown_to_user(self) -> None:
        result = self.runner.invoke(
            cli_module.app,
            [
                "--symbol",
                "BTCUSDT",
                "--side",
                "BUY",
                "--type",
                "LIMIT",
                "--qty",
                "0.002",
            ],
        )

        self.assertEqual(1, result.exit_code)
        self.assertIn("Validation error", result.output)

    def test_successful_market_order_prints_summary_and_response(self) -> None:
        fake_client_wrapper = MagicMock()
        fake_client_wrapper.client = object()
        fake_manager = MagicMock()
        fake_manager.place_futures_order.return_value = {
            "orderId": 123,
            "status": "NEW",
            "executedQty": "0.000",
            "avgPrice": "0.00",
            "symbol": "BTCUSDT",
        }

        with patch.dict(
            os.environ,
            {"BINANCE_API_KEY": "test_key", "BINANCE_API_SECRET": "test_secret"},
            clear=False,
        ), patch("cli.BinanceTestnetClient", return_value=fake_client_wrapper), patch(
            "cli.OrderManager", return_value=fake_manager
        ):
            result = self.runner.invoke(
                cli_module.app,
                ["--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--qty", "0.002"],
            )

        self.assertEqual(0, result.exit_code)
        self.assertIn("Order request summary", result.output)
        self.assertIn("Order placed successfully.", result.output)
        self.assertIn("Order ID: 123", result.output)
        fake_manager.place_futures_order.assert_called_once_with(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.002,
            price=None,
            stop_price=None,
        )

    def test_order_failure_is_shown_to_user(self) -> None:
        fake_client_wrapper = MagicMock()
        fake_client_wrapper.client = object()
        fake_manager = MagicMock()
        fake_manager.place_futures_order.return_value = {"error": "Rejected by exchange"}

        with patch.dict(
            os.environ,
            {"BINANCE_API_KEY": "test_key", "BINANCE_API_SECRET": "test_secret"},
            clear=False,
        ), patch("cli.BinanceTestnetClient", return_value=fake_client_wrapper), patch(
            "cli.OrderManager", return_value=fake_manager
        ):
            result = self.runner.invoke(
                cli_module.app,
                ["--symbol", "BTCUSDT", "--side", "SELL", "--type", "LIMIT", "--qty", "0.002", "--price", "90000"],
            )

        self.assertEqual(1, result.exit_code)
        self.assertIn("Order failed: Rejected by exchange", result.output)


if __name__ == "__main__":
    unittest.main()
