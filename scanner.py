import os
import requests

print("Crypto Weekly Scanner Started")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

if telegram_token and telegram_chat_id:
    print("Telegram settings loaded successfully")

    message = "Crypto Weekly Scanner is running ✅"

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    payload = {
        "chat_id": telegram_chat_id,
        "text": message
    }

    response = requests.post(url, data=payload, timeout=10)

    print(response.text)

    if response.ok:
        print("Telegram message sent successfully")
    else:
        print("Telegram message failed")

else:
    print("Telegram settings are missing")
