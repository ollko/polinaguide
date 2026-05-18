
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from data import data


back_to_start_meny_btn = InlineKeyboardButton(
    text='🏠 В начало',
    callback_data='start_menu'
)
back_main_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [back_to_start_meny_btn,],
    ]
)


async def get_all_products_markup():
    products = await data.get_products_new()

    product_btns = [
        InlineKeyboardButton(
            text=f'🚗 {p.description}',
            callback_data=f"product:{p.id}")
        for p in products

    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn] for btn in product_btns
        ]
    )


async def get_buy_product_markup(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Купить гайд',
                    callback_data=f"bay:{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text='👈🏼 Вернуться',
                    callback_data=f"product:{product_id}"
                )
            ]
        ]
    )
