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

from inline_markups import GREATING_TEXT, get_all_products_markup
import data.data as data

ADMIN_ID = int(os.environ.get("ADMIN_ID"))

question_before_purchase_router = Router()


class SupportStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()  # Для админа


class ReplyCallback(CallbackData, prefix="rep"):
    user_id: int
    username: str
    ticket_id: int  # Добавили это поле


@question_before_purchase_router.callback_query(F.data == "ask_question_start")
async def ask_question_start(
    callback: CallbackQuery,
    state: FSMContext
):
    '''Обрабатывает кнопку << задать вопрос перед покупкой >>
    Добавляет состояние ожидание вопроса ( state.waiting_for_question )
    '''
    # Создаем кнопку отмены
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="❌ Отмена", callback_data="cancel_question")]
    ])
    await callback.message.edit_text(
        "Напишите ваш вопрос, и я отвечу Вам в ближайшее время:",
        reply_markup=cancel_kb
    )
    await state.set_state(SupportStates.waiting_for_question)
    await callback.answer()


@question_before_purchase_router.callback_query(F.data == "cancel_question")
async def cancel_question(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await callback.message.edit_text(
        "Отправка вопроса отменена.",
        reply_markup=None
    )
    await callback.message.edit_text(
        text=GREATING_TEXT,
        reply_markup=await get_all_products_markup(),
    )
    await callback.answer()


@question_before_purchase_router.message(SupportStates.waiting_for_question)
async def forward_question_to_admin(
    message: Message,
    state: FSMContext,
    bot: Bot, session:
    AsyncSession,
):
    '''
    '''
    ticket_id = await data.save_question(message.from_user.id, message.text)

    # Отправляем админу
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Ответить",
            callback_data=ReplyCallback(
                user_id=message.from_user.id,
                username=message.from_user.username or "id" +
                str(message.from_user.id),
                ticket_id=ticket_id,
            ).pack()
        )]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"📩 **Новый вопрос! (ID: {ticket_id})**\nОт: @{message.from_user.username}\n\nТекст: {message.text}",
        reply_markup=kb
    )
    # Отправляем пользователю
    await message.answer("Ваш вопрос отправлен! Ожидайте ответа.")
    await state.clear()


@question_before_purchase_router.callback_query(ReplyCallback.filter())
async def setup_answer(
    callback: CallbackQuery,
    callback_data: ReplyCallback,
    state: FSMContext
):
    await state.update_data(
        reply_to_id=callback_data.user_id,
        ticket_id=callback_data.ticket_id,
    )
    await callback.message.answer(f"Введите ответ для @{callback_data.username}:")
    await state.set_state(SupportStates.waiting_for_answer)
    print(f'{state=}')
    await callback.answer()


@question_before_purchase_router.message(SupportStates.waiting_for_answer)
async def send_answer_to_user(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    state_data = await state.get_data()
    user_id = state_data.get("reply_to_id")
    ticket_id = state_data.get("ticket_id")

    try:
        await bot.send_message(user_id, f"🔔 **Ответ от Полины:**\n\n{message.text}")
    except Exception as e:
        await message.answer(f"Ошибка при отправке: {e}")

    await message.answer("Ответ успешно отправлен пользователю.")
    await data.save_answer(ticket_id, message.text)

    await state.clear()
