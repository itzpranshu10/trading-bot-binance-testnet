# Binance Futures Testnet Trading Bot

This repository contains my implementation of the Python developer application task: a small, structured CLI application for placing Binance Futures Testnet USDT-M orders with validation, logging, and clear failure handling.

## Features

- Places `MARKET` and `LIMIT` orders on Binance Futures Testnet
- Supports both `BUY` and `SELL`
- Bonus support for `STOP_LIMIT`
- Validates CLI inputs before sending requests
- Logs API requests, responses, and failures to `bot.log`
- Uses a separate client layer, order layer, validation layer, and CLI entry point

## Deliverables Included

- Source code
- `README.md` with setup, run examples, and assumptions
- `requirements.txt`
- `bot.log` containing one real `MARKET` order and one real `LIMIT` order on Binance Futures Testnet

## Project Structure

```text
trading_bot/
|-- bot/
|   |-- __init__.py
|   |-- client.py
|   |-- logging_config.py
|   |-- orders.py
|   `-- validators.py
|-- .env
|-- .env.example
|-- .gitignore
|-- bot.log
|-- cli.py
|-- README.md
`-- requirements.txt
```

## Setup

1. Create or activate a Binance Futures Testnet account.
2. Generate Futures Testnet API credentials.
3. Create a virtual environment and install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and set your credentials:

```env
BINANCE_API_KEY=your_testnet_key_here
BINANCE_API_SECRET=your_testnet_secret_here
```

## Binance Testnet Endpoint

All futures API interactions target Binance Futures Testnet:

`https://testnet.binancefuture.com`

The client wrapper configures the Python Binance client to use the futures testnet endpoint for USDT-M orders.

## How to Run

Run commands from the `trading_bot` directory.

### MARKET order

```powershell
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

### LIMIT order

```powershell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 90000
```

### Bonus STOP_LIMIT order

```powershell
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --qty 0.002 --price 90000 --stop-price 90500
```

## Example Output

```text
Order request summary
  Symbol: BTCUSDT
  Side: BUY
  Type: MARKET
  Quantity: 0.001
Order placed successfully.
Order response details
  Order ID: 123456789
  Status: NEW
  Executed Qty: 0
  Avg Price: 0.0
  Symbol: BTCUSDT
```

## Logging

Application logs are written to `bot.log` in the project root.

Logged events include:

- connectivity checks to Binance Futures Testnet
- order request payloads
- order responses
- validation failures
- API errors
- network failures

## Assumptions

- The user has valid Binance Futures Testnet API credentials.
- The account is enabled for USDT-M Futures Testnet trading.
- Quantity and price precision are accepted by Binance for the selected symbol.
- This project focuses on order placement, not strategy or position management.

## Validation and Error Handling

- Rejects invalid sides and unsupported order types
- Rejects missing or invalid `price` for `LIMIT`
- Rejects missing or invalid `price` and `stop_price` for `STOP_LIMIT`
- Rejects invalid symbol format
- Surfaces Binance API errors and network failures clearly in both CLI output and log file

## Deliverables Status

- Source code: included
- `requirements.txt`: included
- `README.md`: included
- Log file output: `bot.log` with one MARKET order and one LIMIT order
