import os
import requests

print("Crypto Weekly Scanner Started")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

coins_url = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd"
    "&order=market_cap_desc"
    "&per_page=100"
    "&page=1"
    "&price_change_percentage=7d"
)

response = requests.get(coins_url, timeout=10)

coins = response.json()

signals = []

for coin in coins:
    name = coin["name"]
    symbol = coin["symbol"].upper()
    price = coin["current_price"]

    change = coin.get(
        "price_change_percentage_7d_in_currency",
        0
    )

    if change >= 5:
        signals.append(
            f"🚀 {symbol} - {name}\n"
            f"Price: ${price}\n"
            f"7D Change: +{change:.2f}%\n"
        )

if signals:
    report = (
        "📊 Weekly Scanner Signals\n\n"
        + "\n".join(signals)
    )
else:
    report = (
        "📊 Weekly Scanner\n\n"
        "No strong signals found this scan."
    )

print(report)

if telegram_token and telegram_chat_id:

    telegram_url = (
        f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    )

    payload = {
        "chat_id": telegram_chat_id,
        "text": report[:4000]
    }

    result = requests.post(
        telegram_url,
        data=payload,
        timeout=10
    )

    print(result.text)

    if result.ok:
        print("Telegram report sent successfully")
    else:
        print("Telegram report failed")

else:
    print("Telegram settings are missing")
