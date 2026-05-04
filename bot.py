import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from handlers.start import start_router
from handlers.free_guide import free_quide_router
from handlers.road_trip_guide import road_trip_quide_router
from handlers.payments import payments_router
from handlers.question_before_purchase import question_before_purchase_router
from handlers.question_payment_method import question_payment_method_router
# Bot token can be obtained via https://t.me/BotFather
from middlewares import DbSessionMiddleware

TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)


async def main() -> None:
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
        # default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await dp.start_polling(bot)
    finally:
        # Корректное закрытие сессий при остановке
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
