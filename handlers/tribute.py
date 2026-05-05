import os
import hashlib
import hmac
from aiohttp import web
from aiogram import Bot
from data import create_payment_and_action
# Константы
API_KEY = os.getenv("TRIBUTE_API_TOKEN")
HOST = "0.0.0.0"
PORT = 3000


async def send_guide(bot, user_id, product_id):
    files = {
        "pvmW": "link_OF_GUIDE_1",
        "guide_2": "FILE_ID_OF_GUIDE_2"
    }

    link_to_send = files.get(product_id)

    if link_to_send:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"🎉 Спасибо за покупку! Это ссылка на ваш гайд: {link_to_send}"
            )
        except Exception as e:
            print(f"Ошибка при отправке файла: {e}")
    else:
        # Если ID товара не в словаре, можно отправить админу алерт
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
        data = await request.json()
    except Exception:
        return web.Response(text="Invalid JSON", status=200)
    event = data.get("name")
    if event == "new_digital_product":
        payload = data.get("payload", {})
        result = await create_payment_and_action(payload)
        # 6. Tribute требует строгий возврат 200 OK
        if result.get("status") == 200 and "product_id" in result:
            user_id = result["user_id"]
            product_id = result["product_id"]
            await send_guide(bot, user_id, product_id)

        return web.Response(text="OK", status=200)
