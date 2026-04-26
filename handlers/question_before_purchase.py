import os

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

ADMIN_ID = int(os.environ.get("ADMIN_ID"))

question_before_purchase_router = Router()


class SupportStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()  # Для админа


@question_before_purchase_router.callback_query(F.data == "ask_question_start")
async def ask_question_start(
    callback: CallbackQuery,
    state: FSMContext
):
    # Создаем кнопку отмены
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="❌ Отмена", callback_data="cancel_question")]
    ])
    await callback.message.answer(
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
    await callback.message.edit_text("Отправка вопроса отменена.")
    await callback.answer()


@question_before_purchase_router.message(SupportStates.waiting_for_question)
async def forward_question_to_admin(message: Message, state: FSMContext, bot: Bot):
    # Отправляем админу
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Ответить", callback_data=f"reply_{message.from_user.id}")]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"📩 **Новый вопрос!**\nОт: @{message.from_user.username} ({message.from_user.id})\n\nТекст: {message.text}",
        reply_markup=kb
    )
    # Отправляем пользователю
    await message.answer("Ваш вопрос отправлен! Ожидайте ответа.")
    await state.clear()


@question_before_purchase_router.callback_query(F.data.startswith("reply_"))
async def setup_answer(
    callback: CallbackQuery,
    state: FSMContext
):
    target_user_id = callback.data.split("_")[1]
    await state.update_data(reply_to_id=target_user_id)

    await callback.message.answer(f"Введите ответ для пользователя @{callback.message.from_user.username}:")
    await state.set_state(SupportStates.waiting_for_answer)
    await callback.answer()


@question_before_purchase_router.message(SupportStates.waiting_for_answer)
async def send_answer_to_user(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()
    print(f'{data=}')
    user_id = data.get("reply_to_id")

    try:
        await bot.send_message(user_id, f"🔔 **Ответ от Полины:**\n\n{message.text}")
        await message.answer("Ответ успешно отправлен пользователю.")
    except Exception as e:
        await message.answer(f"Ошибка при отправке: {e}")

    await state.clear()
