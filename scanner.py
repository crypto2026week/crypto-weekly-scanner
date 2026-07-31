import os
import requests
import ccxt

print("Crypto Weekly Scanner Started")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

exchange = ccxt.binance()

symbols = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT"
]

report = "📊 Crypto Weekly Scanner Report\n\n"

for symbol in symbols:
    ticker = exchange.fetch_ticker(symbol)
    price = ticker["last"]

    report += f"{symbol}: {price} USDT\n"

print(report)

if telegram_token and telegram_chat_id:

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    payload = {
        "chat_id": telegram_chat_id,
        "text": report
    }

    response = requests.post(url, data=payload, timeout=10)

    print(response.text)

    if response.ok:
        print("Telegram report sent successfully")
    else:
        print("Telegram report failed")

else:
    print("Telegram settings are missing")
