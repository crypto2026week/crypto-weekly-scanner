import os
import requests

print("Crypto Early Trend Scanner V4.2 Started")


telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
coingecko_api_key = os.getenv("COINGECKO_API_KEY")


# =========================================================
# V4.2 EXCLUSION FILTER
# =========================================================

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


# =========================================================
# COINGECKO MARKET DATA
# =========================================================

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

response.raise_for_status()

coins = response.json()

signals = []


# =========================================================
# MAIN SCANNER
# =========================================================

for coin in coins:

    symbol = coin["symbol"].upper()
    name = coin["name"]
    name_lower = name.lower()


    # -----------------------------------------------------
    # EXCLUSION FILTER
    # -----------------------------------------------------

    if symbol in excluded_symbols:
        continue


    if (
        "usd" in name_lower
        or "dollar" in name_lower
        or "stable" in name_lower
        or "gold" in name_lower
        or "tokenized stock" in name_lower
        or "bstocks" in name_lower
        or "stock" in name_lower
    ):
        continue


    # -----------------------------------------------------
    # MARKET DATA
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # DATA VALIDATION
    # -----------------------------------------------------

    if not price:
        continue

    if not market_cap:
        continue

    if not volume:
        continue

    if market_cap <= 0:
        continue


    # -----------------------------------------------------
    # VOLUME / MARKET CAP
    # -----------------------------------------------------

    volume_ratio = (
        volume / market_cap
    ) * 100


    # =====================================================
    # V4.2 SCORING ENGINE
    # =====================================================

    momentum = 0
    volume_quality = 0
    liquidity = 0
    early_trend = 0
    market_cap_score = 0
    volume_spike = 0
    late_move_penalty = 0


    # -----------------------------------------------------
    # MOMENTUM / 20
    # -----------------------------------------------------

    if 5 <= change <= 20:
        momentum = 20

    elif 20 < change <= 30:
        momentum = 12

    elif 30 < change <= 50:
        momentum = 5

    elif change > 50:
        momentum = 2


    # -----------------------------------------------------
    # VOLUME QUALITY / 20
    # -----------------------------------------------------

    if volume >= 200000000:
        volume_quality = 20

    elif volume >= 100000000:
        volume_quality = 16

    elif volume >= 50000000:
        volume_quality = 12

    elif volume >= 25000000:
        volume_quality = 6

    else:
        volume_quality = 2


    # -----------------------------------------------------
    # LIQUIDITY / 15
    # -----------------------------------------------------

    if 5 <= volume_ratio < 10:
        liquidity = 8

    elif 10 <= volume_ratio < 20:
        liquidity = 12

    elif 20 <= volume_ratio < 40:
        liquidity = 15

    elif volume_ratio >= 40:
        liquidity = 10


    # -----------------------------------------------------
    # EARLY TREND / 15
    # -----------------------------------------------------

    if 5 <= change <= 15:
        early_trend = 15

    elif 15 < change <= 25:
        early_trend = 12

    elif 25 < change <= 40:
        early_trend = 6

    elif change > 40:
        early_trend = 2


    # -----------------------------------------------------
    # MARKET CAP OPPORTUNITY / 10
    # -----------------------------------------------------

    if 50000000 <= market_cap <= 500000000:
        market_cap_score = 10

    elif 500000000 < market_cap <= 1000000000:
        market_cap_score = 7

    elif 1000000000 < market_cap <= 5000000000:
        market_cap_score = 5

    else:
        market_cap_score = 3


    # -----------------------------------------------------
    # VOLUME SPIKE / 10
    # -----------------------------------------------------

    if 10 <= volume_ratio < 20:
        volume_spike = 10

    elif 20 <= volume_ratio < 40:
        volume_spike = 8

    elif volume_ratio >= 40:
        volume_spike = 5

    elif 5 <= volume_ratio < 10:
        volume_spike = 6


    # -----------------------------------------------------
    # LATE MOVE PENALTY / 10
    # -----------------------------------------------------

    if 20 < change <= 50:
        late_move_penalty = 3

    elif 50 < change <= 100:
        late_move_penalty = 6

    elif change > 100:
        late_move_penalty = 10


    # -----------------------------------------------------
    # CONFIDENCE / 100
    # -----------------------------------------------------

    confidence = (
        momentum
        + volume_quality
        + liquidity
        + early_trend
        + market_cap_score
        + volume_spike
        - late_move_penalty
    )


    if confidence < 0:
        confidence = 0

    if confidence > 100:
        confidence = 100# ============================================================
# PART 2 — REPORT + TELEGRAM
# ============================================================

signals.sort(
    key=lambda x: x["confidence"],
    reverse=True
)


if signals:

    report = (
        "🚨 Crypto Early Trend Scanner V5\n\n"
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
        "🚨 Crypto Early Trend Scanner V5\n\n"
        "No early signals found."
    )


print(report)


# ============================================================
# TELEGRAM
# ============================================================

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
