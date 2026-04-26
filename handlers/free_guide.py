from os import environ

from aiogram import Bot, Router, types, F
from aiogram.types import LinkPreviewOptions
from aiogram.enums import ChatMemberStatus

from texts import (
    I_WANT_A_FREE_GUIDE,
    WHATS_INSIDE_FREE_GUIDE,
    SUITABLE_FOR_WHOM_FREE_GUIDE,
)
from inline_markups import *

free_quide_router = Router()

CHANNEL_ID = environ.get("TEST_CHANNEL_ID")
CHANNEL_URL = environ.get("CHANNEL_URL")

FREE_GUIDE_LINK = environ.get("FREE_GUIDE_LINK")


@free_quide_router.callback_query(F.data == "free_guide")
async def free_guide(callback: types.CallbackQuery):
    await callback.message.answer(
        I_WANT_A_FREE_GUIDE,
        reply_markup=whats_inside_free_guide_markup,
    )
    await callback.answer()


@free_quide_router.callback_query(F.data == "whats_inside_free_guide")
async def whats_inside_free_guide(callback: types.CallbackQuery):
    await callback.message.answer(
        WHATS_INSIDE_FREE_GUIDE,
        reply_markup=suitable_for_whom_free_guide_markup,
    )
    await callback.answer()


@free_quide_router.callback_query(F.data == "suitable_for_whom_free_guide")
async def suitable_for_whom_free_guide(callback: types.CallbackQuery):
    await callback.message.answer(
        SUITABLE_FOR_WHOM_FREE_GUIDE,
        reply_markup=free_guide_markup,
    )
    await callback.answer()


async def check_sub(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


@free_quide_router.callback_query(F.data == "get_free_guide")
async def free_guide(callback: types.CallbackQuery):
    await callback.message.answer(
        "Чтобы получить подарок, нужно быть частью нашего сообщества!"
        "Давай проверим, подписан ли ты на мой канал 👇",
        reply_markup=free_guide_markup,
    )
    await callback.answer()


@free_quide_router.callback_query(F.data == "Check_membership_and_get_gift")
async def handle_gift_request(callback: types.CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    is_subscribed = await check_sub(bot, user_id)

    if is_subscribed:
        # СЦЕНАРИЙ 1: Пользователь подписан — отдаем подарок
        # 1. Удаляем сообщение с кнопкой проверки
        await callback.message.delete()
        await callback.message.edit_text(
            f"✅ Спасибо за подписку! Ваш подарок готов.\n\n"
            f"📥 <a href='{FREE_GUIDE_LINK}'>Нажмите здесь, чтобы скачать гайд</a>",
            # Это позволит ссылке выглядеть как текст
            parse_mode="HTML",
            # Отключаем превью, чтобы не было лишних картинок под текстом
            link_preview_options=LinkPreviewOptions(is_disabled=True)

        )
        await callback.answer()
    else:
        # Если НЕ подписан — показываем всплывающее окно (alert)
        await callback.answer(
            "😪 Пойми, мы долго работали над этим гайдом, поэтому отдаём его только за подписку...",
            # "Чтобы получить подарок, нужно сначала подписаться на канал! 👆",
            show_alert=True
        )
