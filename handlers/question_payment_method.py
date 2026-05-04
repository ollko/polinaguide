import os

from aiogram import Bot, Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from sqlalchemy.ext.asyncio import AsyncSession

from data import save_answer, save_question
from handlers.question_before_purchase import ReplyCallback
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

question_payment_method_router = Router()


class TechSupportStates(StatesGroup):
    waiting_for_tech_question = State()
    # Состояние ответа админа можно используем из SupportStates
# 1. Начало диалога (другой callback_data)


@question_payment_method_router.callback_query(F.data == "ask_payment_method_start")
async def tech_question_start(callback: CallbackQuery, state: FSMContext):
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="❌ Отмена", callback_data="cancel_ask_payment_method")]
    ])
    await callback.message.answer(
        'Напишите мне "Другой способ" и я пришлю вам ответ',
        reply_markup=cancel_kb
    )
    await state.set_state(TechSupportStates.waiting_for_tech_question)
    await callback.answer()

# 2. Прием вопроса


@question_payment_method_router.message(TechSupportStates.waiting_for_tech_question)
async def forward_tech_to_admin(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    # Используем вашу функцию сохранения, если таблица та же
    ticket_id = await save_question(session, message.from_user.id, message.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Ответить другой способ оплаты",
            callback_data=ReplyCallback(
                user_id=message.from_user.id,
                username=message.from_user.username or f"id{message.from_user.id}",
                ticket_id=ticket_id,
            ).pack()
        )]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"🛠 **ТЕХ. ПОДДЕРЖКА (ID: {ticket_id})**\nОт: @{message.from_user.username}\n\n{message.text}",
        reply_markup=kb
    )
    await message.answer("Ваш запрос отправлен!")
    await state.clear()

# 3. Отмена для этого контекста


@question_payment_method_router.callback_query(F.data == "cancel_ask_payment_method")
async def cancel_tech(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Запрос в техподдержку отменен.")
    await callback.answer()
