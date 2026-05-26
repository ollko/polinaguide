import os
import hashlib
import hmac
import json
from aiohttp import web
from aiogram import Bot

import data.data as data
from models import ActionType

TRIBUTE_API_TOKEN = os.getenv("TRIBUTE_API_TOKEN")

PAYLOAD_KEY_ORDER = [
    "product_id", "amount", "currency", "user_id", "trb_user_id",
    "telegram_user_id", "telegram_username", "purchase_id",
    "purchase_created_at", "product_name", "transaction_id"
]


async def get_amount_str(
    amount: int,
    currency: str
):
    price = amount / 100
    return f"{price:.2f} {currency}."


async def get_quide_text(
    product_name,
    product_url,
    amount_str,
):
    text = f'''💳 Оплата {amount_str} успешно получена через Трибьют!\n
🎉 Спасибо за покупку «{product_name}»!\n'''

    if product_url:
        return text + f'📍 <a href="{product_url}">Скачать гайд</a>'
    else:
        return text + "🎉 Мы скоро пришлем ваш гайд."


async def tribute_webhook_handler(request: web.Request) -> web.Response:
    bot: Bot = request.app['bot']

    signature_header = request.headers.get("trbt-signature")

    if not signature_header:
        print("Ошибка: Заголовок trbt-signature отсутствует")
        return web.Response(text="No signature header", status=200)

    # 1. Читаем измененный JSON
    try:
        wrong_json = await request.json()
    except Exception:
        return web.Response(text="Invalid JSON structure", status=400)

    # 2. Пересобираем payload строго в том порядке, в котором его подписал Tribute
    original_payload = wrong_json.get("payload", {})
    ordered_payload = {k: original_payload[k]
                       for k in PAYLOAD_KEY_ORDER if k in original_payload}

    # 3. Собираем финальный JSON-объект
    correct_dict = {
        "created_at": wrong_json.get("created_at"),
        "name": wrong_json.get("name"),
        "payload": ordered_payload,
        "sent_at": wrong_json.get("sent_at")
    }

    # 4. Превращаем в строку без лишних пробелов и с нормальной кириллицей (как в вашем тесте)
    correct_body_str = json.dumps(
        correct_dict, ensure_ascii=False, separators=(',', ':'))
    body_bytes = correct_body_str.encode("utf-8")

    # 5. Проверяем подпись
    computed_signature = hmac.new(
        key=TRIBUTE_API_TOKEN.encode("utf-8"),
        msg=body_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature_header, computed_signature):
        print("Подпись ВСЕ ЕЩЕ НЕ совпадает!")
        print(f'{computed_signature=}')
        return web.Response(text="Invalid signature", status=403)

    print("Успех! Подпись совпала после пересборки JSON.")

    event = correct_dict.get("name")
    payload = correct_dict.get("payload")

    if event == "new_digital_product" and payload:
        telegram_user_id = payload.get("telegram_user_id")
        product_name = payload.get("product_name")
        amount = payload.get("amount")
        currency = payload.get("currency").upper()
        amount_str = await get_amount_str(amount, currency)
        try:

            await data.create_tribute_payment(payload)
        except Exception as e:
            print(f'Ошибка при сохранении в таблицу tribute_payment: {e}')

        try:
            await data.create_action(
                tg_id=telegram_user_id,
                action_type=ActionType.PURCHASE,
                details=f'Покупка товара {product_name} на сумму {amount_str} через TRIBUTE'
            )
        except Exception as e:
            print(f'Ошибка при сохранении в таблицу action: {e}')

        product_url: str | None = await data.get_product_url(product_name)
        quide_text = await get_quide_text(
            product_name,
            product_url,
            amount_str,
        )
        try:
            await bot.send_message(
                chat_id=telegram_user_id,
                text=quide_text,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f'Ошибка при отправке файла: {e}')

        return web.Response(text="OK", status=200)
    else:
        print(f'Получен {event=} от tribute')
    return web.Response(text='DEFAULT', status=200)
