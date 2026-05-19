import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from handlers.main_menu import main_menu_router
from handlers.start import start_router
from handlers.guide import guide_router
from handlers.yookassa_payments import yookassa_payments_router
from handlers.tribute_payments import tribute_webhook_handler
from handlers.question_before_purchase import question_before_purchase_router


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
        guide_router,
        main_menu_router,
        yookassa_payments_router,
        question_before_purchase_router,
    )

    dp.startup.register(on_startup)

    bot = Bot(
        token=TOKEN,
    )

    app = web.Application()
    app['bot'] = bot
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    app.add_routes([web.post("/webhook/tribute", tribute_webhook_handler)])

    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=8080,)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
