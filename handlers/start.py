from typing import Union

from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated, Message, CallbackQuery

import data.data as data

from inline_markups import get_all_products_markup
start_router = Router()


GREATING_TEXT = '''Привет! 👋

Если ты когда-нибудь пытался спланировать маршрут по Сербии и понял, сколько это занимает времени — этот бот сильно упростит тебе жизнь😊

Мы уже проделали за тебя десятки часов планирования и собрали маршруты так, как сделали бы это для себя: с продуманной логикой, проверенными локациями и без лишней суеты. Мы знаем регион изнутри, поэтому в гайдах — не случайные точки, а места, отобранные по реальному опыту, а не по туристическим спискам.

✨️Выбирай, с чего начать — и погнали исследовать Балканы:
'''


@start_router.callback_query(F.data == "start_menu")
@start_router.message(CommandStart())
async def start(event: Union[Message, CallbackQuery]):
    user = event.from_user
    text_to_send = GREATING_TEXT
    all_products_markup = await get_all_products_markup()
    await data.create_or_update_user(
        tg_id=user.id,
        username=user.username
    )

    if isinstance(event, Message):
        print(f'{all_products_markup=}')
        await event.answer(
            text=text_to_send,
            reply_markup=all_products_markup,
        )

    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text_to_send,
            reply_markup=all_products_markup,
        )
        await event.answer()


@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def on_user_blocked(event: ChatMemberUpdated):
    '''Handler will be triggered when the status changes to 'kicked' (the user has blocked the bot)'''
    await data.update_user_status(event.from_user.id, "blocked")


@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def on_user_unblocked(event: ChatMemberUpdated):
    '''The handler will be triggered when the user has unblocked the bot back.'''
    await data.update_user_status(event.from_user.id, "active")
