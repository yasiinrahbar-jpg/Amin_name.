#!/usr/bin/env python3
"""
Telegram Name Updater + Fixed Bold Font
ویژگی‌ها:
- آپدیت اسم تلگرام با ساعت تهران
- فونت ثابت بولد
- کار با Session String
- سرور Flask برای Render
"""
import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not all([API_ID, API_HASH, SESSION_STRING]):
    raise SystemExit("❌ لطفاً API_ID, API_HASH و SESSION_STRING را در .env وارد کنید.")

TEHRAN_TZ = pytz.timezone("Asia/Tehran")
USERNAME = "YASIN"

# فونت ثابت بولد (با یونیکد)
def bold_font(text: str) -> str:
    bold_map = {c: chr(ord(c) + 0x1D400 - ord('A')) if 'A' <= c <= 'Z' else chr(ord(c) + 0x1D41A - ord('a')) if 'a' <= c <= 'z' else c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'}
    return ''.join(bold_map.get(c, c) for c in text)

# تابع جدید برای فونت فانتزی اعداد
def fancy_numbers(text: str) -> str:
    nums = str.maketrans("0123456789", "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿")
    return text.translate(nums)

# ======== Task آپدیت اسم تلگرام ========
async def update_name():
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
    await client.start()
    print("✅ Client connected. Starting name updates...")
    while True:
        try:
            now = datetime.now(TEHRAN_TZ)
            time_str = now.strftime("%H:%M")  # ساعت تهران
            fancy_time = fancy_numbers(time_str)
            new_name = bold_font(USERNAME) + " | " + fancy_time
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
            print(f"✅ Updated name: {new_name}")
        except Exception as e:
            print("⚠️ Error updating name:", e)

        # Calculate delay until the next minute for precise timing
        now_seconds = datetime.now(TEHRAN_TZ).second
        delay = 60 - now_seconds
        await asyncio.sleep(delay)

# ======== سرور Flask برای Render ========
app = Flask("NameUpdater")

@app.route("/")
def index():
    return "🚀 Bot is live!"

# ======== اجرای همزمان Flask و آپدیت اسم ========
async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(update_name())
    port = int(os.environ.get("PORT", 10000))
    from threading import Thread
    def run_flask():
        app.run(host="0.0.0.0", port=port)
    Thread(target=run_flask).start()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
