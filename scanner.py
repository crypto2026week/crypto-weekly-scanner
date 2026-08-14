import os
import requests
import json
from pathlib import Path

print("Crypto Early Trend Scanner V4.3 Started")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
coingecko_api_key = os.getenv("COINGECKO_API_KEY")


# =========================================================
# V4.3 CONFIGURATION
# =========================================================

HISTORY_FILE = Path("scanner_history.json")

MIN_VOLUME_USD = 5_000_000
MIN_CONFIDENCE = 65
MAX_HISTORY = 12


# =========================================================
# EXCLUSION FILTER
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
# LOAD HISTORY
# =========================================================

if HISTORY_FILE.exists():

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            history = json.load(f)

        if not isinstance(history, dict):
            history = {}

    except Exception as error:

        print(
            "History load failed:",
            error
        )

        history = {}

else:

    history = {}


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

    headers["x-cg-demo-api-key"] = (
        coingecko_api_key
    )


response = requests.get(
    coins_url,
    headers=headers,
    timeout=15
)

response.raise_for_status()

coins = response.json()

signals = []


# =========================================================
# MAIN SCANNER
# =========================================================

for coin in coins:

    symbol = coin.get(
        "symbol",
        ""
    ).upper()

    name = coin.get(
        "name",
        ""
    )

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
    if change is None:
    continue

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

    if not volume:
        continue

    if not market_cap:
        continue

    if market_cap <= 0:
        continue

    if volume < MIN_VOLUME_USD:
        continue


    # -----------------------------------------------------
    # VOLUME / MARKET CAP
    # -----------------------------------------------------

    volume_ratio = (
        volume / market_cap
    ) * 100


    # =====================================================
    # V4.3 SCORE COMPONENTS
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

    if volume >= 200_000_000:

        volume_quality = 20

    elif volume >= 100_000_000:

        volume_quality = 16

    elif volume >= 50_000_000:

        volume_quality = 12

    elif volume >= 25_000_000:

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

    if 50_000_000 <= market_cap <= 500_000_000:

        market_cap_score = 10

    elif 500_000_000 < market_cap <= 1_000_000_000:

        market_cap_score = 7

    elif 1_000_000_000 < market_cap <= 5_000_000_000:

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


    # =====================================================
    # BASE SCORE
    # =====================================================

    base_score = (
        momentum
        + volume_quality
        + liquidity
        + early_trend
        + market_cap_score
        + volume_spike
        - late_move_penalty
    )


    if base_score < 0:
        base_score = 0

    if base_score > 100:
        base_score = 100


    # =====================================================
    # HISTORY TRACKING
    # =====================================================

    if symbol not in history:
        history[symbol] = []

    if not isinstance(
        history[symbol],
        list
    ):
        history[symbol] = []


    history[symbol].append(
        {
            "price": price,
            "change": change,
            "volume": volume,
            "market_cap": market_cap,
            "confidence": base_score
        }
    )


    history[symbol] = history[symbol][
        -MAX_HISTORY:
    ]


    previous_count = max(
        0,
        len(history[symbol]) - 1
    )


    # =====================================================
    # PERSISTENCE SCORE / 10
    # =====================================================

    persistence_score = 0

    if previous_count >= 1:
        persistence_score = 3

    if previous_count >= 2:
        persistence_score = 5

    if previous_count >= 4:
        persistence_score = 7

    if previous_count >= 6:
        persistence_score = 10


    # =====================================================
    # TREND CONTINUITY
    # =====================================================

    rising_observations = 0

    if len(history[symbol]) >= 2:

        recent = history[symbol][-5:]

        for i in range(
            1,
            len(recent)
        ):

            if (
                recent[i]["price"]
                > recent[i - 1]["price"]
            ):

                rising_observations += 1


    # =====================================================
    # CONTINUITY BONUS
    # =====================================================

    continuity_bonus = 0

    if rising_observations >= 2:
        continuity_bonus = 2

    if rising_observations >= 3:
        continuity_bonus = 4


    # =====================================================
    # V4.3 FINAL CONFIDENCE
    # =====================================================

    confidence = (
        base_score
        + persistence_score
        + continuity_bonus
    )


    if confidence > 100:
        confidence = 100


    # =====================================================
    # SIGNAL FILTER
    # =====================================================

    if confidence < MIN_CONFIDENCE:
        continue


    # =====================================================
    # STAGE DETECTION
    # =====================================================

    if change <= 15:

        stage = "🟢 EARLY"

    elif change <= 25:

        stage = "🟡 DEVELOPING"

    elif change <= 50:

        stage = "🟠 EXTENDED"

    else:

        stage = "🔴 LATE"


    # =====================================================
    # PERSISTENCE LABEL
    # =====================================================

    if previous_count >= 4:

        persistence_label = "🔥 Persistent"

    elif previous_count >= 2:

        persistence_label = "📌 Repeated"

    elif previous_count >= 1:

        persistence_label = "👀 Returning"

    else:

        persistence_label = "🆕 New"


    # =====================================================
    # FINAL OPPORTUNITY
    # =====================================================

    if (
        confidence >= 85
        and stage == "🟢 EARLY"
    ):

        opportunity = "🟢 STRONG EARLY"

    elif (
        confidence >= 80
        and stage in [
            "🟢 EARLY",
            "🟡 DEVELOPING"
        ]
    ):

        opportunity = "🟡 GOOD EARLY"

    elif (
        confidence >= 75
        and persistence_score >= 5
        and stage != "🔴 LATE"
    ):

        opportunity = "🔥 PERSISTENT TREND"

    else:

        opportunity = "🔴 WATCHLIST"


    # =====================================================
    # SAVE SIGNAL
    # =====================================================

    signals.append(
        {
            "symbol": symbol,
            "name": name,
            "confidence": confidence,
            "base_score": base_score,
            "opportunity": opportunity,
            "stage": stage,
            "persistence_label": persistence_label,
            "persistence_score": persistence_score,
            "continuity_bonus": continuity_bonus,
            "price": price,
            "change": change,
            "volume": volume,
            "market_cap": market_cap,
            "ratio": volume_ratio,
            "momentum": momentum,
            "volume_quality": volume_quality,
            "liquidity": liquidity,
            "early_trend": early_trend,
            "market_cap_score": market_cap_score,
            "volume_spike": volume_spike,
            "late_move_penalty": late_move_penalty
        }
    )


# =========================================================
# SAVE HISTORY
# =========================================================

try:

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=2
        )

except Exception as error:

    print(
        "History save failed:",
        error
    )


# =========================================================
# END OF PART 1
# =========================================================
# =========================================================
# PART 2 — REPORT + TELEGRAM
# =========================================================

signals.sort(
    key=lambda x: (
        x["confidence"],
        x["persistence_score"],
        x["change"]
    ),
    reverse=True
)


# =========================================================
# BUILD REPORT
# =========================================================

if signals:

    report = (
        "🚨 Crypto Early Trend Scanner V4.3\n\n"
    )

    rank = 1

    for item in signals[:5]:

        report += (
            f"🏆 {rank}. "
            f"{item['symbol']} - "
            f"{item['name']}\n"

            f"{item['opportunity']}\n"
            f"{item['stage']} | "
            f"{item['persistence_label']}\n\n"

            f"🎯 Confidence: "
            f"{item['confidence']}/100\n"

            f"🧠 Base Score: "
            f"{item['base_score']}/100\n\n"

            f"📈 Momentum: "
            f"{item['momentum']}/20\n"

            f"📊 Volume Quality: "
            f"{item['volume_quality']}/20\n"

            f"🔥 Volume Spike: "
            f"{item['volume_spike']}/10\n"

            f"💧 Liquidity: "
            f"{item['liquidity']}/15\n"

            f"🚀 Early Trend: "
            f"{item['early_trend']}/15\n"

            f"🏦 Market Cap: "
            f"{item['market_cap_score']}/10\n"

            f"⚠️ Late Move Penalty: "
            f"-{item['late_move_penalty']}/10\n\n"

            f"🔁 Persistence: "
            f"{item['persistence_score']}/10\n"

            f"📌 Continuity Bonus: "
            f"+{item['continuity_bonus']}\n\n"

            f"💰 Price: "
            f"${item['price']}\n"

            f"📈 7D: "
            f"{item['change']:.2f}%\n"

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
        "🚨 Crypto Early Trend Scanner V4.3\n\n"
        "No early signals found."
    )


# =========================================================
# PRINT REPORT
# =========================================================

print(report)


# =========================================================
# TELEGRAM
# =========================================================

if telegram_token and telegram_chat_id:

    telegram_url = (
        f"https://api.telegram.org/bot"
        f"{telegram_token}/sendMessage"
    )

    payload = {
        "chat_id": telegram_chat_id,
        "text": report[:4000]
    }

    try:

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

            print(
                result.text
            )

    except Exception as error:

        print(
            "Telegram request failed:",
            error
        )

else:

    print(
        "Telegram settings are missing"
    )
