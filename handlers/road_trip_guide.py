from aiogram import Router, types, F

from texts import (
    I_WANT_TO_GO_ON_A_ROAD_TRIP_TEXT,
    WHATS_INSIDE,
    SUITABLE_FOR_WHOM,
    WHO_IS_NOT_SUITABLE,
)
from inline_markups import *

road_trip_quide_router = Router()


@road_trip_quide_router.callback_query(F.data == "road_trip_guide")
async def road_trip_guide(callback: types.CallbackQuery):
    # Отправляем ответ пользователю (всплывающее уведомление или сообщение)
    text_to_send = I_WANT_TO_GO_ON_A_ROAD_TRIP_TEXT
    await callback.message.edit_text(
        text=text_to_send,
        reply_markup=whats_in_depth_markup,
    )
    await callback.answer()


@road_trip_quide_router.callback_query(F.data == "whats_inside")
async def whats_inside(callback: types.CallbackQuery):
    text_to_send = WHATS_INSIDE
    await callback.message.edit_text(
        text=text_to_send,
        reply_markup=for_whom__markup,
    )


@road_trip_quide_router.callback_query(F.data == "suitable_for_whom")
async def suitable_for_whom(callback: types.CallbackQuery):
    # Отправляем ответ пользователю (всплывающее уведомление или сообщение)
    text_to_send = SUITABLE_FOR_WHOM
    await callback.message.edit_text(
        text=text_to_send,
        reply_markup=by_or_ask_a_question_markup,
    )
    await callback.answer()


@road_trip_quide_router.callback_query(F.data == "who_is_not_suitable")
async def who_is_not_suitable(callback: types.CallbackQuery):
    # Отправляем ответ пользователю (всплывающее уведомление или сообщение)
    await callback.message.edit_text(
        WHO_IS_NOT_SUITABLE,
        reply_markup=by_or_ask_a_question_markup,
    )
    await callback.answer()
