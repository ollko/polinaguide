from aiogram import Router, types, F
from aiogram.filters.command import CommandStart

from texts import (
    GREATING_TEXT,

    FOR_FREE_WITH_A_SUBSCRIPTION_TEXT,
)
from inline_markups import greating_markup
start_router = Router()


@start_router.message(CommandStart())
async def start(message: types.Message):
    """Возвращает инлайн кнопку 'Start'"""
    await message.answer(
        text=GREATING_TEXT,
        reply_markup=greating_markup,
    )
