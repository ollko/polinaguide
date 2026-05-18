from os import getenv

from aiogram import Router, types, F

import data.data as data
from inline_markups import *
from models import ActionType
from data.data import PRODUCTS

yookassa_payments_router = Router()

YOOKASSA_TOKEN = getenv("YOOKASSA_TOKEN")


@yookassa_payments_router.callback_query(F.data.startswith("pay_yookassa:"))
async def buy_via_yookassa(
    callback: types.CallbackQuery,
):
    product_id = callback.data.split(":")[1]
    product = await data.get_product_new(int(product_id))
    await callback.message.answer_invoice(
        title=product.product_name,
        description="Оплата через ЮKassa банковской картой.",
        payload=product.invoice_payload,
        provider_token=YOOKASSA_TOKEN,  # ОБЯЗАТЕЛЬНО для ЮKassa
        currency="RUB",                # Фиатная валюта
        prices=[types.LabeledPrice(
            label=product.product_name,
            amount=product.yookassa_total_amount
        )],
        start_parameter=f"pay_{product.invoice_payload}"
    )
    await callback.message.delete()
    await callback.answer()


@yookassa_payments_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@yookassa_payments_router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    # Проверяем, за какой именно товар заплатили (из payload в invoice)
    tg_id = message.from_user.id
    payment = message.successful_payment

    await data.create_yookassa_payment(
        tg_id=tg_id,
        payment=payment,
    )
    product_id = payment.invoice_payload.split('_')[1]
    product = await data.get_product_new(int(product_id))

    price = payment.total_amount / 100
    amount_str = f"{price:.2f} руб."

    await data.create_action(
        tg_id=tg_id,
        action_type=ActionType.PURCHASE,
        details=f'Покупка товара {product.product_name} на сумму {amount_str} через ЮКАССА'
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
        f"🎉 Спасибо за покупку путеводителя «{product.product_name}»!\n\n"
        f"📍 Скачать гайд можно по ссылке:\n{product.product_url}",
        # Актуальный способ включить превью ссылки в aiogram 3.x
        link_preview_options=types.LinkPreviewOptions(is_disabled=False)
    )
