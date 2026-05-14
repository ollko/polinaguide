import os

from aiogram import Router
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import Command

import data.data as data
from handlers.free_guide import check_channel_subscription

channel_id = os.getenv("CHANNEL_ID")
channel_name = os.getenv("CHANNEL_NAME")
channel_url = os.getenv("CHANNEL_URL")

main_menu_router = Router()


async def get_guides_list(guides: list[data.Product]) -> str:

    guides_list = "\n".join(
        [
            f"📍 {g.products_name}\n {g.link}"
            for g in guides
        ]
    )
    return f"📚 Список ваших гайдов:\n\n{guides_list}"


@main_menu_router.message(Command("my_guides"))
async def show_my_guides(message: Message):
    user_id = message.from_user.id
    guides = await data.get_purchased_products(user_id)
    text = await get_guides_list(guides)
    await message.answer(text)


@main_menu_router.message(Command("free_guides"))
async def show_free_guides(message: Message):
    user_id = message.from_user.id
    is_subscribed = await check_channel_subscription(message.bot, user_id, channel_id=channel_id)

    if is_subscribed:
        gree_guides = await data.get_free_products()
        text = await get_guides_list(gree_guides)
        await message.answer(text)
    else:
        await message.answer(
            text='Чтобы получить 🎁 , подпишись на мой канал 😳',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text=f'🔗 {channel_name}',
                        url=channel_url
                    )]]
            ),
        )
