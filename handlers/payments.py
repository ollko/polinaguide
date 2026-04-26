from os import getenv

from aiogram import Router, types, F

from inline_markups import buy_a_guide_markup
payments_router = Router()

YOOKASSA_TOKEN = getenv("YOOKASSA_TOKEN")


@payments_router.callback_query(F.data == "buy_a_guide")
async def select_payment_method(callback: types.CallbackQuery):
    await callback.message.answer(
        "Выберите удобный способ оплаты:",
        reply_markup=buy_a_guide_markup
    )
    await callback.answer()


@payments_router.callback_query(F.data == "pay_stars")
async def buy_a_guide(callback: types.CallbackQuery):
    await callback.message.answer_invoice(
        title="Гайд по Западной Сербии",
        description="Полный маршрут: локации, отели и советы.",
        payload="road_trip_guide",  # Внутренняя пометка для бота
        currency="XTR",         # XTR — это Звезды (Stars)
        prices=[types.LabeledPrice(label="Гайд", amount=1)]  # Цена в звездах
    )
    await callback.answer()


@payments_router.callback_query(F.data == "pay_yookassa")
async def buy_via_yookassa(callback: types.CallbackQuery):
    print(f'{YOOKASSA_TOKEN=}')
    await callback.message.answer_invoice(
        title="Гайд по Западной Сербии",
        description="Оплата через ЮKassa банковской картой.",
        payload="road_trip_guide",
        provider_token=YOOKASSA_TOKEN,  # ОБЯЗАТЕЛЬНО для ЮKassa
        currency="RUB",                # Фиатная валюта
        # Сумма в копейках (500.00 руб)
        prices=[types.LabeledPrice(label="Гайд", amount=10000)],
        start_parameter="guide_payment"
    )
    await callback.answer()


@payments_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@payments_router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    # Проверяем, за какой именно товар заплатили (из payload в invoice)

    payment = message.successful_payment
    # Определяем, как именно оплатил пользователь для красивого сообщения
    # Проверяем, какой товар был оплачен через payload
    if payment.invoice_payload == "road_trip_guide":
        # Логика выдачи гайда

        if payment.currency == "XTR":
            method_name = "Telegram Stars"
            amount_str = f"{payment.total_amount} ⭐️"
        else:
            method_name = "ЮКасса"
            # перевод из копеек
            amount_str = f"{payment.total_amount / 100} руб."

        await message.answer(
            f"Оплата успешно получена через {method_name}!\n"
            f"Сумма: {amount_str}\n\n"
            f"📍 Лови твой гайд по Западной Сербии: [ССЫЛКА_ИЛИ_ФАЙЛ]"
        )
