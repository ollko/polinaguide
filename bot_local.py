from handlers.yookassa_payments import yookassa_payments_router
from handlers.guide import guide_router
from aiogram import Bot, Dispatcher
from handlers.tribute_payments import tribute_webhook_handler
from middlewares import DbSessionMiddleware
from handlers.question_before_purchase import question_before_purchase_router
from handlers.yookassa_payments import payments_router
from handlers.road_trip_guide import road_trip_quide_router
from handlers.free_guide import free_quide_router
from handlers.start import start_router
from handlers.main_menu import main_menu_router
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand, BotCommandScopeDefault
import logging
import os
import sys

from aiohttp import web
<< << << < HEAD

== == == =

>>>>>> > new

TOKEN = os.getenv("BOT_TOKEN")

WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = os.getenv("WEB_SERVER_PORT")

BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
TRIBUTE_API_TOKEN = os.getenv("TRIBUTE_API_TOKEN")


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


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        allowed_updates=["message", "callback_query",
                         "edited_message", "channel_post"],
        drop_pending_updates=True
    )
    await set_main_menu(bot)


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
