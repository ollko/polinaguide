from aiogram import Bot
import asyncio
import os
from pytz import timezone
from datetime import datetime

from data import data


BOT_TOKEN = os.getenv("BOT_TOKEN")
NOTIFICATIONS_TIMEZONE = os.getenv("TIMEZONE", 'Europe/Moscow')


async def notificator(bot: Bot):
    tz = timezone(NOTIFICATIONS_TIMEZONE)
    current_time = datetime.now(tz)
    today_date_str = current_time.strftime('%Y-%m-%d')  # Формат '2026-05-22'
    users_to_notify = await data.get_users_who_did_not_buy_raw(today_date_str)

    if not users_to_notify:
        print("💤 Нет пользователей для отправки уведомлений на сегодня.")
        return

    print(f"📢 Найдено пользователей для отправки: {len(users_to_notify)}")
    async with bot:
        for tg_id, text_message in users_to_notify:
            try:
                await bot.send_message(chat_id=tg_id, text=text_message)
                print(f"✅ Успешно отправлено пользователю {tg_id}")
                await asyncio.sleep(0.05)
            except Exception as e:
                print(
                    f"❌ Не удалось отправить сообщение пользователю {tg_id}: {e}")
