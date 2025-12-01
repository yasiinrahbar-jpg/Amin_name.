#!/usr/bin/env python3
"""
Telegram Name Updater with Dynamic Fonts and Clock
ویژگی‌ها:
- آپدیت اسم تلگرام با فونت‌های متغیر و ساعت تهران
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

# API اطلاعات و سشن
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not all([API_ID, API_HASH, SESSION_STRING]):
    raise SystemExit("❌ لطفاً API_ID, API_HASH و SESSION_STRING را در .env وارد کنید.")

# اسم اصلی از متغیر محیطی
BASE_NAME = os.getenv("BASE_NAME", "YourName")
TEHRAN_TZ = pytz.timezone("Asia/Tehran")

# لیست فونت‌ها
FONTS = [
    "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩",
    "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙",
    "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ",
    "𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝐽𝐾𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵",
]

def stylize_name(name, font):
    # تبدیل حروف اسم به فونت انتخابی
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

def fancy_numbers(text: str) -> str:
    # تبدیل اعداد به فونت فانتزی
    nums = str.maketrans("0123456789", "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿")
    return text.translate(nums)

# ======== Task آپدیت اسم تلگرام ========
async def update_name():
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
    await client.start()
    print("✅ Client connected. Starting name updates...")
    font_index = 0
    while True:
        try:
            # انتخاب فونت و استایل‌دهی به نام
            current_font = FONTS[font_index % len(FONTS)]
            styled_name = stylize_name(BASE_NAME, current_font)

            # دریافت و فرمت‌دهی ساعت تهران
            now = datetime.now(TEHRAN_TZ)
            time_str = now.strftime("%H:%M")
            fancy_time = fancy_numbers(time_str)

            # ترکیب نهایی نام و آپدیت پروفایل
            new_name = f"{styled_name} | {fancy_time}"
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
            print(f"✅ Updated name: {new_name}")

            font_index += 1
        except Exception as e:
            print(f"⚠️ Error updating name: {e}")

        # محاسبه تأخیر تا دقیقه بعدی برای زمان‌بندی دقیق
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
    Thread(target=run_flask, daemon=True).start()
    print(f"🚀 Flask server started on port {port}")
    # حلقه اصلی برای زنده نگه داشتن برنامه
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
