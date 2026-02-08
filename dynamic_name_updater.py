#!/usr/bin/env python3
"""
Telegram Name Updater with Bold Name & Small Clock
ویژگی‌ها:
- آپدیت اسم تلگرام با فونت بولد و شیک + ساعت کوچیک تهران
- کار با Session String
- سرور Flask برای Render جهت اجرای ۲۴/۷
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

# ======= تنظیمات تلگرام از ENV =======
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BASE_NAME = os.getenv("BASE_NAME", "YASIN")  # اسم از env بخونه
PORT = int(os.environ.get("PORT", 10000))

if not all([API_ID, API_HASH, SESSION_STRING]):
    raise SystemExit("❌ لطفاً API_ID, API_HASH و SESSION_STRING را در .env وارد کنید.")

# ======= فونت اسم بولد و شیک =======
NAME_FONT = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
TEHRAN_TZ = pytz.timezone("Asia/Tehran")

# ======= تبدیل اسم به فونت ثابت =======
def stylize_name(name, font):
    styled = ""
    for c in name:
        if 'a' <= c.lower() <= 'z':
            index = ord(c.upper()) - ord('A')
            if index < len(font):
                styled += font[index]
            else:
                styled += c
        else:
            styled += c
    return styled

# ======= تبدیل ساعت به اعداد کوچیک (superscript) =======
def small_time(text: str) -> str:
    return (
        text.replace("0", "⁰")
            .replace("1", "¹")
            .replace("2", "²")
            .replace("3", "³")
            .replace("4", "⁴")
            .replace("5", "⁵")
            .replace("6", "⁶")
            .replace("7", "⁷")
            .replace("8", "⁸")
            .replace("9", "⁹")
            .replace(":", "ː")  # دو نقطه کوچیک
    )

# ======= آپدیت اسم تلگرام =======
async def update_name():
    print("ℹ️ Initializing Telegram client...")
    try:
        client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
        await client.start()
        print("✅ Client connected. Starting name updates...")
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        return

    styled_name = stylize_name(BASE_NAME, NAME_FONT)

    while True:
        try:
            # دریافت ساعت تهران و تبدیل به superscript
            now = datetime.now(TEHRAN_TZ)
            time_str = now.strftime("%H:%M")
            small_clock = small_time(time_str)

            # ترکیب اسم و ساعت (چسبیده)
            new_name = f"{styled_name}{small_clock}"
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
            print(f"✅ Updated name: {new_name}")

        except Exception as e:
            print(f"⚠️ Error updating name: {e}")

        # صبر تا دقیقه بعد برای آپدیت دقیق
        now_seconds = datetime.now(TEHRAN_TZ).second
        delay = 60 - now_seconds
        await asyncio.sleep(delay)

# ======= سرور Flask برای Render =======
app = Flask("NameUpdater")

@app.route("/")
def index():
    return "🚀 Bot is live!"

# ======= اجرای همزمان Flask و آپدیت اسم =======
async def main():
    print("ℹ️ Starting main function...")
    loop = asyncio.get_event_loop()
    loop.create_task(update_name())

    from threading import Thread
    def run_flask():
        app.run(host="0.0.0.0", port=PORT)
    Thread(target=run_flask, daemon=True).start()

    print(f"🚀 Flask server started on port {PORT}")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
