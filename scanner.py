import os
import requests

print("Crypto Early Trend Scanner V4.1 Started")


telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
coingecko_api_key = os.getenv("COINGECKO_API_KEY")


excluded_symbols = [
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
    "USDP",
    "PAXG",
    "XAUT"
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
    name = coin["name"]
    name_lower = name.lower()


    if symbol in excluded_symbols:
        continue


    if (
        "usd" in name_lower
        or "dollar" in name_lower
        or "stable" in name_lower
        or "gold" in name_lower
    ):
        continue


    price = coin.get(
        "current_price",
        0
    )


    change = coin.get(
        "price_change_percentage_7d_in_currency",
        0
    )


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


    if volume < 5000000:
        continue


    volume_ratio = (
        volume / market_cap
    ) * 100


    # V4.1 Confidence Engine

    momentum = 0
    volume_score = 0
    liquidity = 0
    early_trend = 0
    market_cap_score = 0
    volume_spike = 0


    # Momentum Detection

    if 5 <= change <= 20:
        momentum += 25

    elif 20 < change <= 35:
        momentum += 15

    elif change > 35:
        momentum += 5

    # Volume Power

    if volume >= 50000000:
        volume_score += 15

    if volume >= 200000000:
        volume_score += 10


    # Volume Spike Detection

    if volume_ratio >= 10:
        volume_spike += 15

    elif volume_ratio >= 5:
        volume_spike += 8


    # Liquidity

    if volume_ratio >= 5:
        liquidity += 10

    if volume_ratio >= 15:
        liquidity += 10


    # Early Trend Detection

    if 5 <= change <= 20:
        early_trend += 15

    elif change > 20:
        early_trend += 5


    # Market Cap Opportunity

    if 50000000 <= market_cap <= 500000000:
        market_cap_score += 10

    elif 500000000 < market_cap <= 1000000000:
        market_cap_score += 7

    else:
        market_cap_score += 4


    confidence = (
        momentum
        + volume_score
        + liquidity
        + early_trend
        + market_cap_score
        + volume_spike
    )


    if confidence >= 70:

        if confidence >= 90:
            opportunity = "🟢 Strong Early Signal"

        elif confidence >= 80:
            opportunity = "🟡 Good Early Signal"

        else:
            opportunity = "🔴 Watchlist"


        signals.append(
            {
                "symbol": symbol,
                "name": name,
                "confidence": confidence,
                "opportunity": opportunity,
                "price": price,
                "change": change,
                "volume": volume,
                "market_cap": market_cap,
                "ratio": volume_ratio,
                "momentum": momentum,
                "volume_score": volume_score,
                "liquidity": liquidity,
                "early_trend": early_trend,
                "market_cap_score": market_cap_score,
                "volume_spike": volume_spike
            }
        )


signals.sort(
    key=lambda x: x["confidence"],
    reverse=True
)


if signals:

    report = (
        "🚨 Crypto Early Trend Scanner V4.1\n\n"
    )


    rank = 1


    for item in signals[:5]:

        report += (
            f"🏆 {rank}. {item['symbol']} - {item['name']}\n"
            f"{item['opportunity']}\n\n"

            f"🎯 Confidence: "
            f"{item['confidence']}/100\n\n"

            f"📈 Momentum: {item['momentum']}/25\n"
            f"📊 Volume: {item['volume_score']}/25\n"
            f"🔥 Volume Spike: {item['volume_spike']}/15\n"
            f"💧 Liquidity: {item['liquidity']}/20\n"
            f"🚀 Early Trend: {item['early_trend']}/15\n"
            f"🏦 Market Cap: {item['market_cap_score']}/10\n\n"

            f"💰 Price: ${item['price']}\n"
            f"📈 7D: {item['change']:.2f}%\n"
            f"💎 Market Cap: ${item['market_cap']:,.0f}\n"
            f"📊 Volume: ${item['volume']:,.0f}\n"
            f"🔥 Vol/Cap: {item['ratio']:.2f}%\n\n"
        )

        rank += 1


else:

    report = (
        "🚨 Crypto Early Trend Scanner V4.1\n\n"
        "No early signals found."
    )


print(report)


if telegram_token and telegram_chat_id:

    telegram_url = (
        f"https://api.telegram.org/bot"
        f"{telegram_token}/sendMessage"
    )


    payload = {
        "chat_id": telegram_chat_id,
        "text": report[:4000]
    }


    result = requests.post(
        telegram_url,
        data=payload,
        timeout=30
    )


    if result.ok:
        print(
            "Telegram report sent successfully"
        )

    else:
        print(
            "Telegram report failed"
        )


else:

    print(
        "Telegram settings are missing"
    )
