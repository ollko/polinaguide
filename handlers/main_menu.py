from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

import data
from products import PRODUCTS

main_menu_router = Router()


@main_menu_router.message(Command("my_guides"))
async def show_my_guides(message: Message):
    user_id = message.from_user.id
    print(f'{user_id=}')
    guides = await data.get_purchased_products(user_id)
    await message.answer(guides)
