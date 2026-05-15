from os import environ

from aiogram import Bot, Router, types, F
from aiogram.types import LinkPreviewOptions
from aiogram.enums import ChatMemberStatus
from sqlalchemy.ext.asyncio import AsyncSession

import data.data as data
from inline_markups import *
from models import ActionType
from data.data import PRODUCTS
from texts import (
    I_WANT_A_FREE_GUIDE,
    WHATS_INSIDE_FREE_GUIDE,
    SUITABLE_FOR_WHOM_FREE_GUIDE,
)

free_quide_router = Router()


channel_id = environ.get("CHANNEL_ID")


@free_quide_router.callback_query(F.data == "free_guide")
async def free_guide_in_depth(callback: types.CallbackQuery):
    text_to_send = I_WANT_A_FREE_GUIDE
    await callback.message.edit_text(
        text=text_to_send,
        reply_markup=free_guide_in_depth_markup,
    )
    await callback.answer()


@free_quide_router.callback_query(F.data == "whats_inside_free_guide")
async def whats_inside_free_guide(callback: types.CallbackQuery):
    text_to_send = WHATS_INSIDE_FREE_GUIDE
    await callback.message.edit_text(
        text=text_to_send,
        reply_markup=back_to_free_guide_in_depth_markup,
    )
    await callback.answer()


@free_quide_router.callback_query(F.data == "suitable_for_whom_free_guide")
async def suitable_for_whom_free_guide(callback: types.CallbackQuery):
    text_to_send = SUITABLE_FOR_WHOM_FREE_GUIDE
    await callback.message.edit_text(
        text=text_to_send,
        reply_markup=back_to_free_guide_in_depth_markup,
    )
    await callback.answer()


async def check_channel_subscription(bot: Bot, user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


@free_quide_router.callback_query(F.data == "get_free_guide")
async def free_guide(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Чтобы получить подарок, нужно быть частью нашего сообщества! "
        "Давай проверим, подписан ли ты на мой канал 👇",
        reply_markup=free_guide_markup,
    )
    await callback.answer()


@free_quide_router.callback_query(F.data == "check_membership_and_get_gift")
async def handle_gift_request(callback: types.CallbackQuery, bot: Bot, session: AsyncSession):
    print('in handle_gift_request ...')
    user_id = callback.from_user.id
    print(f'{callback.from_user.id=}')
    channel_id = channel_id
    is_subscribed = await check_channel_subscription(bot, user_id, channel_id)

    if is_subscribed:
        # СЦЕНАРИЙ 1: Пользователь подписан — отдаем подарок
        # 1. Удаляем сообщение с кнопкой проверки
        # await callback.message.delete()
        print('deleted ...')
        # print(f'{callback.message=}')
        await callback.message.edit_text(
            f"✅ Спасибо за подписку!\n\n"
            f"📥 <a href='{PRODUCTS['Настоящая Сербия'].link}'>Нажмите здесь, чтобы скачать гайд</a>",
            # Это позволит ссылке выглядеть как текст
            parse_mode="HTML",
            # Отключаем превью, чтобы не было лишних картинок под текстом
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            reply_markup=back_main_menu_markup,
        )
        await data.create_action(
            tg_id=user_id,
            action_type=ActionType.FREE_GUIDE,
            details='Настоящая Сербия'
        )

        await callback.answer()
    else:
        # Если НЕ подписан — показываем всплывающее окно (alert)
        await callback.answer(
            "😪 Пойми, мы долго работали над этим гайдом, поэтому отдаём его только за подписку...",
            # "Чтобы получить подарок, нужно сначала подписаться на канал! 👆",
            show_alert=True
        )
