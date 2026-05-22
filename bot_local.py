# Импорты для планировщика
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from pytz import timezone

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand, BotCommandScopeDefault
import logging
import os
import sys

from handlers.yookassa_payments import yookassa_payments_router
from handlers.guide import guide_router
from aiogram import Bot, Dispatcher
from handlers.tribute_payments import tribute_webhook_handler
from handlers.question_before_purchase import question_before_purchase_router

from handlers.start import start_router
from handlers.main_menu import main_menu_router
from notifications import notificator as notificator_job
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")

WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = os.getenv("WEB_SERVER_PORT")

BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
TRIBUTE_API_TOKEN = os.getenv("TRIBUTE_API_TOKEN")

NOTIFICATIONS_TIMEZONE = os.getenv("NOTIFICATIONS_TIMEZONE")
NOTIFICATION_CRON_HOUR = os.getenv("NOTIFICATION_CRON_HOUR")
NOTIFICATION_CRON_MINUTE = os.getenv("NOTIFICATION_CRON_MINUTE")

router = Router()


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='start', description='Начать работу с ботом'),
        BotCommand(command='my_guides', description='Мои гайды'),
        BotCommand(command='free_guides', description='Бесплатные гайды'),
    ]

    await bot.set_my_commands(
        commands=main_menu_commands,
        scope=BotCommandScopeDefault()
    )


def my_listener(event):
    if event.exception:
        print(f"Задание {event.job_id} упало с ошибкой:")
        print(f"  Тип: {type(event.exception).__name__}")
        print(f"  Сообщение: {event.exception}")
        print(f"  Трейсбек:\n{event.traceback}")
    else:
        print(f"✅ Задача {event.job_id} завершилась.")


async def on_startup(bot: Bot, dispatcher: Dispatcher) -> None:
    await bot.set_webhook(
        f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        allowed_updates=["message", "callback_query",
                         "edited_message", "channel_post"],
        drop_pending_updates=True,
    )
    await set_main_menu(bot)

    msk_tz = timezone(NOTIFICATIONS_TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=msk_tz)
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Передаем bot прямо в аргументы выполняемой задачи (kwargs)
    scheduler.add_job(
        notificator_job,
        "cron",
        hour=NOTIFICATION_CRON_HOUR,
        minute=NOTIFICATION_CRON_MINUTE,
        id='rssparse_job',
        timezone=msk_tz,
        kwargs={"bot": bot}
    )

    scheduler.start()
    print("⏰ Планировщик уведомлений успешно запущен.")

    # Сохраняем ссылку на планировщик в workflow_data диспетчера, чтобы остановить его при выключении
    dispatcher["scheduler"] = scheduler


def main() -> None:
    dp = Dispatcher()

    dp.include_routers(
        start_router,
        guide_router,
        main_menu_router,
        yookassa_payments_router,
        question_before_purchase_router,
    )

    dp.startup.register(on_startup)

    aiohttpsession = AiohttpSession(proxy='socks5://127.0.0.1:10808')
    bot = Bot(
        token=TOKEN,
        session=aiohttpsession,
    )
    app = web.Application()
    app['bot'] = bot
    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Add router for tribute
    app.add_routes([web.post("/webhook/tribute", tribute_webhook_handler)])

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host="127.0.0.1", port=8080,)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
