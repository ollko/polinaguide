import logging
import sys
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from handlers.start import start_router
from handlers.free_guide import free_quide_router
from handlers.road_trip_guide import road_trip_quide_router
from handlers.payments import payments_router
from handlers.question_before_purchase import question_before_purchase_router
from handlers.question_payment_method import question_payment_method_router
from middlewares import DbSessionMiddleware

TOKEN = getenv("BOT_TOKEN")

WEB_SERVER_HOST = getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = getenv("WEB_SERVER_PORT")

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET")
BASE_WEBHOOK_URL = getenv("BASE_WEBHOOK_URL")
print(f'{BASE_WEBHOOK_URL=}')


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
        question_payment_method_router,
    )
    engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3", echo=True)
    session_pool = async_sessionmaker(engine, expire_on_commit=False)

    dp.update.middleware(DbSessionMiddleware(session_pool=session_pool))
    aiohttpsession = AiohttpSession(proxy='socks5://127.0.0.1:10808')
    bot = Bot(
        token=TOKEN,
        session=aiohttpsession,
    )

    app = web.Application()

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

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host="127.0.0.1",
                port=8080,)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
