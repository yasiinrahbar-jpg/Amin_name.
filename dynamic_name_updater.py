#!/usr/bin/env python3
"""
Dynamic Telegram Name Updater + Flask for Render
ویژگی‌ها:
- آپدیت خودکار اسم تلگرام با ساعت تهران
- تغییر فونت اسم + ساعت هر دقیقه
- کار با Session String
- سرور Flask برای Render (لایو بودن)
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

# فونت‌ها برای تغییر اسم + ساعت
FONTS = [
    lambda t: t,  # عادی
    lambda t: ''.join(['𝐀' if c.isupper() else c for c in t]),  # بولد
    lambda t: ''.join(['𝒜' if c.isupper() else c for c in t]),  # ایتالیک
    lambda t: ''.join(['𝓨' if c.isupper() else c for c in t]),  # فانتزی یونیکد
    lambda t: ''.join(['𝓎' if c.islower() else c for c in t]),  # حروف خمیده
]

# ======== Task آپدیت اسم تلگرام ========
async def update_name():
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
    await client.start()
    print("✅ Client connected. Starting dynamic name updates...")
    font_index = 0
    while True:
        try:
            now = datetime.now(TEHRAN_TZ)
            time_str = now.strftime("%H:%M")  # ساعت تهران
            font_func = FONTS[font_index % len(FONTS)]
            new_name = font_func(USERNAME) + " | " + font_func(time_str)
            font_index += 1
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
            print(f"✅ Updated name: {new_name}")
        except Exception as e:
            print("⚠️ Error updating name:", e)
        await asyncio.sleep(60)  # آپدیت هر دقیقه

# ======== سرور Flask برای Render ========
app = Flask("NameUpdater")

@app.route("/")
def index():
    return "🚀 Bot is live!"

# ======== اجرای همزمان Flask و آپدیت اسم ========
async def main():
    loop = asyncio.get_event_loop()
    # اجرای Task تلگرام در بک‌گراند
    loop.create_task(update_name())
    # اجرای Flask به صورت blocking
    port = int(os.environ.get("PORT", 10000))
    from threading import Thread
    def run_flask():
        app.run(host="0.0.0.0", port=port)
    Thread(target=run_flask).start()
    # نگه داشتن main alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
