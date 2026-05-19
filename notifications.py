import asyncio
import os

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from aiogram import Bot

from data.data import Session
from sqlalchemy import text


BOT_TOKEN = os.getenv("BOT_TOKEN")
NOTIFICATIONS_TIMEZONE = os.getenv("TIMEZONE", 'Europe/Moscow')
NOTIFICATION_CRON_HOUR = os.getenv("NOTIFICATION_CRON_HOUR")
NOTIFICATION_CRON_MINUTE = os.getenv("NOTIFICATION_CRON_MINUTE")


async def get_users_who_did_not_buy_raw():
    async with Session() as session:
        stmt = """
        SELECT 
            a.tg_id, 
            n.notification
        FROM action a
        JOIN notification n ON n.product_id = a.product_id
        WHERE a.action_type = 'START'
        -- Вычисляем разницу в днях (текущая дата минус дата создания экшена)
        AND CAST(JULIANDAY('now') - JULIANDAY(a.created_at) AS INTEGER) = n.day_delta
        -- Исключаем тех, кто в итоге купил этот гайд
        AND NOT EXISTS (
            SELECT 1 
            FROM action ap
            WHERE ap.tg_id = a.tg_id
                AND ap.product_id = n.product_id
                AND ap.action_type = 'PURCHASE'
        );
        """
        result = await session.execute(text(stmt))
        return result.all()


async def notificator():
    bot = Bot(token=BOT_TOKEN)

    users_to_notify = await get_users_who_did_not_buy_raw()

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


def my_listener(event):
    if event.exception:
        print(f"Задание {event.job_id} упало с ошибкой:")
        print(f"  Тип: {type(event.exception).__name__}")
        print(f"  Сообщение: {event.exception}")
        print(f"  Трейсбек:\n{event.traceback}")
    else:
        print(f"✅ Задача {event.job_id} завершилась.")


async def main():
    msk_tz = timezone(NOTIFICATIONS_TIMEZONE)

    scheduler = AsyncIOScheduler(timezone=msk_tz)

    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.add_job(
        notificator,
        "cron",
        hour=NOTIFICATION_CRON_HOUR,
        minute=NOTIFICATION_CRON_MINUTE,
        id='rssparse_job',
        timezone=msk_tz
    )

    scheduler.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Процесс планировщика остановлен.")
