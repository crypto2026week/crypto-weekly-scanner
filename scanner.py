import os
import requests

print("Crypto Weekly Scanner Started")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

coins = [
    "bitcoin",
    "ethereum",
    "binancecoin"
]

report = "📊 Crypto Weekly Scanner Report\n\n"

for coin in coins:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"

    response = requests.get(url, timeout=10)

    data = response.json()

    price = data[coin]["usd"]

    report += f"{coin}: ${price}\n"

print(report)

if telegram_token and telegram_chat_id:

    telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    payload = {
        "chat_id": telegram_chat_id,
        "text": report
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
