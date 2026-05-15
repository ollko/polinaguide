from aiogram import Router, types, F, InlineKeyboardMarkup

from texts import (
    I_WANT_TO_GO_ON_A_ROAD_TRIP_TEXT,
    WHATS_INSIDE,
    SUITABLE_FOR_WHOM,
    WHO_IS_NOT_SUITABLE,
)
from inline_markups import *
from data import data

quide_router = Router()

btns = {
    'suitable': 'Кому подойдет',
    'not_suitable': 'Кому подойдет',
    'what_inside': 'Что вынутри',
}


@quide_router.callback_query(F.data == "quide:")
async def road_trip_guide(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]
    if product_id:
        product = await data.get_product_new(int(product_id))
        if product:
            product_btns = []
            product_btns.append(
                [types.InlineKeyboardButton(
                    text='Купить гайд',
                    callback_data=f'buy:{product.id}'
                )]
            )
            if product.suitable:
                product_btns.append(
                    [types.InlineKeyboardButton(
                        text='Кому подойдет',
                        callback_data=f'suitable:{product.id}'
                    )]
                )
            if product.not_suitable:
                product_btns.append(
                    [types.InlineKeyboardButton(
                        text='Кому не подойдет',
                        callback_data=f'not_suitable:{product.id}'
                    )]
                )
            if product.what_inside:
                product_btns.append(
                    [types.InlineKeyboardButton(
                        text='Что вынутри',
                        callback_data=f'what_inside:{product.id}'
                    )]
                )
            product_btns.append([question_before_purchase_btn])
            product_btns.append([question_before_purchase_btn])

            await callback.message.edit_text(
                text=product.text,
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=product_btns
                ),
            )
        await callback.answer()
