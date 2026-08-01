import os
import requests

print("Crypto Weekly Scanner Started")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
coingecko_api_key = os.getenv("COINGECKO_API_KEY")

stablecoins = [
    "USDT",
    "USDC",
    "USDS",
    "USD1",
    "USDG",
    "DAI",
    "TUSD",
    "PYUSD",
    "FDUSD",
    "USDE",
    "USDP"
]

coins_url = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd"
    "&order=market_cap_desc"
    "&per_page=250"
    "&page=1"
    "&price_change_percentage=7d"
)

headers = {}

if coingecko_api_key:
    headers["x-cg-demo-api-key"] = coingecko_api_key

response = requests.get(
    coins_url,
    headers=headers,
    timeout=10
)

coins = response.json()

signals = []

for coin in coins:

    symbol = coin["symbol"].upper()
    name_lower = coin["name"].lower()

    if symbol in stablecoins:
        continue

    if "usd" in name_lower or "dollar" in name_lower or "stable" in name_lower:
        continue

    name = coin["name"]
    price = coin["current_price"]

    change = coin.get(
        "price_change_percentage_7d_in_currency",
        0
    )

    if change < 5:
        continue

    volume = coin.get(
        "total_volume",
        0
    )

    market_cap = coin.get(
        "market_cap",
        0
    )

    if market_cap == 0:
        continue

    if volume < 10000000:
        continue

    volume_ratio = (volume / market_cap) * 100

    score = 0

    if change >= 5:
        score += 3

    if change >= 15:
        score += 3

    if change >= 30:
        score += 2

    if volume >= 50000000:
        score += 1

    if volume >= 200000000:
        score += 1

    if volume_ratio >= 5:
        score += 2

    if market_cap >= 500000000:
        score += 1

    if market_cap >= 2000000000:
        score += 1

    if score >= 6:

        signals.append(
            {
                "symbol": symbol,
                "name": name,
                "score": score,
                "price": price,
                "change": change,
                "volume": volume,
                "ratio": volume_ratio
            }
        )


signals.sort(
    key=lambda x: x["score"],
    reverse=True
)


if signals:

    report = "📊 Weekly Scanner Signals\n\n"

    rank = 1

    for item in signals:

        report += (
            f"🏆 {rank}. {item['symbol']} - {item['name']}\n"
            f"⭐ Score: {item['score']}/12\n"
            f"💰 Price: ${item['price']}\n"
            f"📈 7D: {item['change']:.2f}%\n"
            f"📊 Volume: ${item['volume']:,.0f}\n"
            f"🔥 Vol/Cap: {item['ratio']:.2f}%\n\n"
        )

        rank += 1

else:

    report = (
        "📊 Weekly Scanner\n\n"
        "No strong signals found."
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

    if result.ok:
        print("Telegram report sent successfully")
    else:
        print("Telegram report failed")

else:
    print("Telegram settings are missing")
