import os
import requests

print("Crypto Early Trend Scanner V3 Started")

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
    name = coin["name"]
    name_lower = name.lower()


    if symbol in stablecoins:
        continue


    if (
        "usd" in name_lower
        or "dollar" in name_lower
        or "stable" in name_lower
    ):
        continue


    price = coin.get("current_price", 0)

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


    #
    # Confidence Engine
    #

    momentum = 0
    volume_score = 0
    liquidity = 0
    early_trend = 0
    risk = 0


    # Momentum

    if 5 <= change <= 20:
        momentum += 20

    elif 20 < change <= 40:
        momentum += 15

    elif change > 40:
        momentum += 8


    # Volume

    if volume >= 50000000:
        volume_score += 15

    if volume >= 200000000:
        volume_score += 10


    # Liquidity

    if volume_ratio >= 5:
        liquidity += 10

    if volume_ratio >= 15:
        liquidity += 10


    # Early trend

    if change >= 5:
        early_trend += 5

    if change <= 25:
        early_trend += 10


    # Risk

    if market_cap >= 1000000000:
        risk += 10

    elif market_cap >= 100000000:
        risk += 7

    else:
        risk += 4

    confidence = (
        momentum
        + volume_score
        + liquidity
        + early_trend
        + risk
    )


    if confidence >= 60:

        if confidence >= 85:
            opportunity = "🟢 Strong Early Opportunity"

        elif confidence >= 70:
            opportunity = "🟡 Early Opportunity"

        else:
            opportunity = "🔴 High Risk Opportunity"


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
                "risk": risk
            }
        )



signals.sort(
    key=lambda x: x["confidence"],
    reverse=True
)



if signals:

    report = (
        "🚨 Crypto Early Trend Scanner V3\n\n"
    )


    rank = 1


    for item in signals[:5]:

        report += (
            f"🏆 {rank}. {item['symbol']} - {item['name']}\n"
            f"{item['opportunity']}\n\n"

            f"🎯 Confidence: "
            f"{item['confidence']}/100\n\n"

            f"📈 Momentum: "
            f"{item['momentum']}/30\n"

            f"📊 Volume: "
            f"{item['volume_score']}/25\n"

            f"💧 Liquidity: "
            f"{item['liquidity']}/20\n"

            f"🚀 Early Trend: "
            f"{item['early_trend']}/15\n"

            f"⚠️ Risk: "
            f"{item['risk']}/10\n\n"

            f"💰 Price: ${item['price']}\n"

            f"📈 7D: {item['change']:.2f}%\n"

            f"💎 Market Cap: "
            f"${item['market_cap']:,.0f}\n"

            f"📊 Volume: "
            f"${item['volume']:,.0f}\n"

            f"🔥 Vol/Cap: "
            f"{item['ratio']:.2f}%\n\n"
        )


        rank += 1


else:

    report = (
        "🚨 Crypto Early Trend Scanner V3\n\n"
        "No high confidence opportunities found."
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
