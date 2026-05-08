import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from handlers.start import start_router
from handlers.free_guide import free_quide_router
from handlers.road_trip_guide import road_trip_quide_router
from handlers.payments import payments_router
from handlers.question_before_purchase import question_before_purchase_router
from middlewares import DbSessionMiddleware
from handlers.tribute import tribute_webhook_handler

TOKEN = os.getenv("BOT_TOKEN")

WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = os.getenv("WEB_SERVER_PORT")

BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
TRIBUTE_API_TOKEN = os.getenv("TRIBUTE_API_TOKEN")
DB_URL = os.getenv("DB_URL")

router = Router()


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET,
    )


def main() -> None:
    dp = Dispatcher()

    dp.include_routers(
        start_router,
        free_quide_router,
        road_trip_quide_router,
        payments_router,
        question_before_purchase_router,
    )

    engine = create_async_engine(DB_URL, echo=True)
    session_pool = async_sessionmaker(engine, expire_on_commit=False)

    dp.update.middleware(DbSessionMiddleware(session_pool=session_pool))

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    bot = Bot(
        token=TOKEN,
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
    web.run_app(app, host="0.0.0.0", port=8080,)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
