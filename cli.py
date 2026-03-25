"""Typer CLI entry point."""

from __future__ import annotations

import os
from typing import Optional

import typer
from dotenv import load_dotenv

from bot.client import BinanceTestnetClient
from bot.logging_config import setup_logging
from bot.orders import OrderManager
from bot.validators import validate_order_params

load_dotenv()
logger = setup_logging()
app = typer.Typer(
    add_completion=False,
    help="Place Binance Futures Testnet USDT-M orders from the command line.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    stop_price: Optional[float],
) -> None:
    typer.echo("Order request summary")
    typer.echo(f"  Symbol: {symbol}")
    typer.echo(f"  Side: {side}")
    typer.echo(f"  Type: {order_type}")
    typer.echo(f"  Quantity: {quantity}")
    if order_type == "LIMIT":
        typer.echo(f"  Price: {price}")
    if order_type == "STOP_LIMIT":
        typer.echo(f"  Price: {price}")
        typer.echo(f"  Stop Price: {stop_price}")


def _print_order_response(response: dict) -> None:
    typer.secho("Order placed successfully.", fg="green", bold=True)
    typer.echo("Order response details")
    typer.echo(f"  Order ID: {response.get('orderId', 'N/A')}")
    typer.echo(f"  Status: {response.get('status', 'N/A')}")
    typer.echo(f"  Executed Qty: {response.get('executedQty', 'N/A')}")
    typer.echo(f"  Avg Price: {response.get('avgPrice', 'N/A')}")
    typer.echo(f"  Symbol: {response.get('symbol', 'N/A')}")


def _credentials_missing(api_key: Optional[str], api_secret: Optional[str]) -> bool:
    placeholder_values = {
        None,
        "",
        "your_testnet_key_here",
        "your_testnet_secret_here",
        "your_api_key",
        "your_api_secret",
    }
    return api_key in placeholder_values or api_secret in placeholder_values


@app.command()
def execute(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Option(..., "--side", help="BUY or SELL"),
    order_type: str = typer.Option(
        "MARKET", "--type", help="MARKET, LIMIT, or STOP_LIMIT"
    ),
    quantity: float = typer.Option(..., "--qty", help="Order quantity"),
    price: Optional[float] = typer.Option(
        None,
        "--price",
        "-p",
        help="Limit price. Required for LIMIT and STOP_LIMIT orders.",
    ),
    stop_price: Optional[float] = typer.Option(
        None,
        "--stop-price",
        help="Stop trigger price. Required for STOP_LIMIT orders.",
    ),
) -> None:
    """Place a market, limit, or stop-limit order on Binance Futures Testnet."""

    try:
        validate_order_params(symbol, side, order_type, quantity, price, stop_price)

        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        if _credentials_missing(api_key, api_secret):
            logger.error("API credentials are missing from the .env file.")
            typer.secho("Error: BINANCE_API_KEY or BINANCE_API_SECRET is missing.", fg="red")
            raise typer.Exit(code=1)

        normalized_symbol = symbol.strip().upper()
        normalized_side = side.strip().upper()
        normalized_type = order_type.strip().upper()

        _print_order_summary(
            normalized_symbol,
            normalized_side,
            normalized_type,
            quantity,
            price,
            stop_price,
        )

        bot_client = BinanceTestnetClient(api_key, api_secret)
        manager = OrderManager(bot_client.client)
        response = manager.place_futures_order(
            symbol=normalized_symbol,
            side=normalized_side,
            order_type=normalized_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )

        if "error" in response:
            typer.secho(f"Order failed: {response['error']}", fg="red", bold=True)
            raise typer.Exit(code=1)

        _print_order_response(response)
    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        typer.secho(f"Validation error: {exc}", fg="yellow")
        raise typer.Exit(code=1)
    except ConnectionError as exc:
        logger.error("Connection error: %s", exc)
        typer.secho(f"Connection error: {exc}", fg="red")
        raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as exc:
        logger.exception("Fatal CLI error.")
        typer.secho(f"Fatal error: {exc}", fg="red")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
