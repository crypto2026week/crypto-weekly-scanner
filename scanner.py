import os

print("Crypto Weekly Scanner Started")

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

if telegram_token and telegram_chat_id:
    print("Telegram settings loaded successfully")
else:
    print("Telegram settings are missing")
