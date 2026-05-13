import os
import hashlib
import hmac
from aiohttp import web
from aiogram import Bot

import data
from models import ActionType
from products import PRODUCTS

API_KEY = os.getenv("TRIBUTE_API_TOKEN")


async def get_amount_str(
    amount: int,
    currency: str
):
    price = amount / 100
    return f"{price:.2f} {currency}."


async def send_guide(
        bot,
        user_id,
        product_name,
        amount_str,
):
    product = PRODUCTS.get(product_name)

    if product and product.link:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"💳 Оплата успешно получена через Трибьют!\n"
                f"Сумма: {amount_str}\n\n"
                f"🎉 Спасибо за покупку путеводителя «{product_name}»!\n\n"
                f"📍 Скачать гайд по ссылке:\n{product.link}"
            )
        except Exception as e:
            print(f"Ошибка при отправке файла: {e}")
    else:
        await bot.send_message(
            chat_id=user_id,
            text="🎉 Спасибо за оплату! Мы скоро пришлем ваш гайд."
        )


async def tribute_webhook_handler(request: web.Request) -> web.Response:
    bot: Bot = request.app['bot']
    # 1. Извлечение заголовка подписи
    signature_header = request.headers.get("trbt-signature")
    if not signature_header:
        print("Ошибка: Заголовок trbt-signature отсутствует")
        return web.Response(text="No signature header", status=200)

    # 2. Получение RAW body (для генерации идентичного HMAC)
    body_bytes = await request.read()
    # ---отладка
    raw_body = body_bytes.decode('utf-8')
    print(f"--- НОВЫЙ ЗАПРОС ---")
    print(f"Заголовки: {dict(request.headers)}")
    print(f"Тело запроса: {raw_body}")
    print(f"--------------------")
    # ---отладка
    # 3. Верификация подписи
    computed_signature = hmac.new(
        key=API_KEY.encode("utf-8"), msg=body_bytes, digestmod=hashlib.sha256
    ).hexdigest()

    # Сравнение за константное время для защиты от timing-атак
    if not hmac.compare_digest(computed_signature, signature_header):
        print("Ошибка безопасности: Неверная подпись!")
        return web.Response(text="Invalid signature", status=200)

    # 4. Безопасный парсинг JSON после валидации
    try:
        r = await request.json()

    except Exception:
        return web.Response(text="Invalid JSON", status=200)

    event = r.get("name")
    if event == "new_digital_product":
        payload = r.get("payload", {})
        result = await data.create_tribute_payment(payload)
        # 6. Tribute требует строгий возврат 200 OK
        if (
            result.get("status") == 200
            and "product_name" in result
            and "amount" in result
            and "currency" in result
        ):
            user_id = result["user_id"]
            product_name = result["product_name"]
            amount = int(result["amount"])
            currency = str(result["currency"]).upper()
            try:
                amount_str = await get_amount_str(amount, currency)
            except Exception as e:
                print('Ошибка при сохранении в таблицу tribute_payment: {e}')
            await send_guide(
                bot,
                user_id,
                product_name,
                amount_str,
            )
            try:
                await data.create_action(
                    tg_id=user_id,
                    action_type=ActionType.PURCHASE,
                    details=f'Покупка товара {product_name} на сумму {amount_str} через TRIBUTE'
                )
            except Exception as e:
                print('Ошибка при сохранении в таблицу action: {e}')
        return web.Response(text="OK", status=200)
