#!/usr/bin/env python3
"""
Dynamic Telegram Name Updater
ویژگی‌ها:
- آپدیت خودکار اسم تلگرام با ساعت تهران
- نمایش ساعت HH:MM کنار اسم
- تغییر فونت اسم + ساعت هر دقیقه
- کار با Session String
- آماده اجرا روی Render یا هر سرور مشابه
"""
import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from dotenv import load_dotenv

# بارگذاری متغیرها از فایل .env
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not all([API_ID, API_HASH, SESSION_STRING]):
    raise SystemExit("❌ لطفاً API_ID, API_HASH و SESSION_STRING را در .env وارد کنید.")

# منطقه زمانی تهران
TEHRAN_TZ = pytz.timezone("Asia/Tehran")

# اسم کاربری اصلی
USERNAME = "YASIN"

# لیست فونت‌ها (تغییر حروف با یونیکد و حالت‌های مختلف)
FONTS = [
    lambda t: t,  # عادی
    lambda t: ''.join(['𝐀' if c.isupper() else c for c in t]),  # بولد
    lambda t: ''.join(['𝒜' if c.isupper() else c for c in t]),  # ایتالیک
    lambda t: ''.join(['𝓨' if c.isupper() else c for c in t]),  # فانتزی یونیکد
    lambda t: ''.join(['𝓎' if c.islower() else c for c in t]),  # حروف خمیده
]

async def update_name():
    """آپدیت اسم تلگرام با ساعت و تغییر فونت هر دقیقه"""
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
    await client.start()
    print("✅ Client connected. Starting dynamic name updates...")
    font_index = 0  # برای تغییر متوالی فونت‌ها

    while True:
        try:
            # گرفتن ساعت دقیق تهران
            now = datetime.now(TEHRAN_TZ)
            time_str = now.strftime("%H:%M")  # ساعت به صورت HH:MM

            # انتخاب فونت متوالی
            font_func = FONTS[font_index % len(FONTS)]
            new_name = font_func(USERNAME) + " | " + font_func(time_str)
            font_index += 1

            # آپدیت اسم
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
            print(f"✅ Updated name: {new_name}")

        except Exception as e:
            print("⚠️ Error updating name:", e)

        await asyncio.sleep(60)  # هر دقیقه آپدیت می‌شود

if __name__ == "__main__":
    asyncio.run(update_name())
