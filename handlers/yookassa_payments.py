from os import getenv

from aiogram import Router, types, F

import data
from inline_markups import *
from models import ActionType
from products import PRODUCTS

payments_router = Router()

YOOKASSA_TOKEN = getenv("YOOKASSA_TOKEN")


@payments_router.callback_query(F.data == "buy_a_guide")
async def select_payment_method(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите удобный способ оплаты:",
        reply_markup=buy_a_guide_markup
    )
    await callback.answer()


@payments_router.callback_query(F.data.startswith("pay_yookassa:"))
async def buy_via_yookassa(
    callback: types.CallbackQuery,
):
    product_key = callback.data.split(":")[1]
    print(f'{product_key=}')

    if product_key not in PRODUCTS:
        await callback.answer("Товар не найден!", show_alert=True)
        return

    product = PRODUCTS[product_key]

    if product.amount <= 0:
        await callback.answer("Этот материал бесплатный, его можно скачать сразу!", show_alert=True)
        # Здесь можно сразу выдать ссылку: await callback.message.answer(product.link)
        return
    else:
        await callback.message.answer_invoice(
            title=product.products_name,
            description="Оплата через ЮKassa банковской картой.",
            payload=product.yookassa_products_id,
            provider_token=YOOKASSA_TOKEN,  # ОБЯЗАТЕЛЬНО для ЮKassa
            currency="RUB",                # Фиатная валюта
            prices=[types.LabeledPrice(
                label="Путеводитель",
                amount=product.amount
            )
            ],
            start_parameter=f"pay_{product_key}"
        )
        await callback.message.delete()
        await callback.answer()


@payments_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@payments_router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    # Проверяем, за какой именно товар заплатили (из payload в invoice)
    tg_id = message.from_user.id
    payment = message.successful_payment

    yookassa_payment_id = await data.create_yookassa_payment(
        tg_id=tg_id,
        payment=payment,
    )
    product_key = payment.invoice_payload
    product = PRODUCTS.get(product_key)
    db_product_name = product.products_name if product else f"Неизвестный товар ({product_key})"

    price = payment.total_amount / 100
    amount_str = f"{price:.2f} руб."

    user_action_id = await data.create_action(
        tg_id=tg_id,
        action_type=ActionType.PURCHASE,
        details=f'Покупка товара {db_product_name} на сумму {amount_str} через ЮКАССА'
    )

    if not product:
        await message.answer(
            "Оплата прошла успешно, но возникла ошибка при определении товара. "
            "Пожалуйста, свяжитесь с поддержкой."
        )
        return

    await message.answer(
        f"💳 Оплата успешно получена через ЮKassa!\n"
        f"Сумма: {amount_str}\n\n"
        f"🎉 Спасибо за покупку путеводителя «{product.products_name}»!\n\n"
        f"📍 Скачать гайд можно по ссылке:\n{product.link}",
        # Актуальный способ включить превью ссылки в aiogram 3.x
        link_preview_options=types.LinkPreviewOptions(is_disabled=False)
    )
