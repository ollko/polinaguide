import os
from aiogram import Bot, Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession

from inline_markups import *
from models import ActionType
import data.data as data

channel_id = int(os.environ.get("CHANNEL_ID"))
channel_name = os.environ.get("CHANNEL_NAME")
channel_url = os.environ.get("CHANNEL_URL")

guide_router = Router()

btns = {
    'suitable': 'Кому подойдет',
    'not_suitable': 'Кому подойдет',
    'what_inside': 'Что вынутри',
}


@guide_router.callback_query(F.data.startswith("product:"))
async def guide(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]
    if product_id:
        product = await data.get_product(int(product_id))
        if product:
            product_btns = []
            if not product.free:
                product_btns.append(
                    [types.InlineKeyboardButton(
                        text='Купить гайд',
                        callback_data=f'buy:{product.id}'
                    )]
                )
            else:
                product_btns.append(
                    [types.InlineKeyboardButton(
                        text='Забрать гайд бесплатно 🎁',
                        callback_data=f'get_free_guide:{product_id}'
                    )]
                )

            if product.suitable and product.not_suitable:
                product_btns.append(
                    [
                        types.InlineKeyboardButton(
                            text='Кому подойдет',
                            callback_data=f'suitable:{product.id}'
                        ),
                        types.InlineKeyboardButton(
                            text='Кому не подойдет',
                            callback_data=f'not_suitable:{product.id}'
                        )
                    ]
                )
            elif product.suitable:
                product_btns.append(
                    [
                        types.InlineKeyboardButton(
                            text='Кому подойдет',
                            callback_data=f'suitable:{product.id}'
                        ),
                    ]
                )
            elif product.not_suitable:
                product_btns.append(
                    [
                        types.InlineKeyboardButton(
                            text='Кому не подойдет',
                            callback_data=f'not_suitable:{product.id}'
                        )
                    ]
                )
            if product.what_inside:
                product_btns.append(
                    [types.InlineKeyboardButton(
                        text='Что вынутри',
                        callback_data=f'what_inside:{product.id}'
                    )]
                )
            if not product.free:
                product_btns.append(
                    [
                        InlineKeyboardButton(
                            text='Задать свой вопрос перед покупкой',
                            callback_data='ask_question_start'
                        )
                    ]
                )

            product_btns.append([back_to_start_meny_btn])

            await callback.message.edit_text(
                text=product.text,
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=product_btns
                ),
            )

            await callback.answer()


@guide_router.callback_query(F.data.startswith("buy:"))
async def buy_product(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]
    if product_id:
        product = await data.get_product(int(product_id))
        await callback.message.edit_text(
            "Выберите удобный способ оплаты:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text='Оплатить через Телеграм',
                            url=product.pay_tribute_url
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text='Оплатить картой (ЮKassa)',
                            callback_data=f'pay_yookassa:{product_id}'
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
        )
        await callback.answer()


@guide_router.callback_query(F.data.startswith("suitable:"))
async def suitable(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]
    if product_id:
        product = await data.get_product(int(product_id))
        buy_product_markup = await get_buy_product_markup(product_id)
        await callback.message.edit_text(
            text=product.suitable,
            reply_markup=buy_product_markup,
        )


@guide_router.callback_query(F.data.startswith("not_suitable:"))
async def not_suitable(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]
    if product_id:
        product = await data.get_product(int(product_id))
        buy_product_markup = await get_buy_product_markup(product_id)
        await callback.message.edit_text(
            text=product.not_suitable,
            reply_markup=buy_product_markup,
        )


@guide_router.callback_query(F.data.startswith("what_inside:"))
async def what_inside(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]
    if product_id:
        product = await data.get_product(int(product_id))
        buy_product_markup = await get_buy_product_markup(product_id)
        await callback.message.edit_text(
            text=product.what_inside,
            reply_markup=buy_product_markup,
        )


async def check_channel_subscription(bot: Bot, user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


@guide_router.callback_query(F.data.startswith("get_free_guide:"))
async def free_guide(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]
    await callback.message.edit_text(
        "Чтобы получить подарок, нужно быть частью нашего сообщества! "
        "Давай проверим, подписан ли ты на мой канал 👇",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Я подписался, проверяй',
                    callback_data=f'check_membership_and_get_gift:{product_id}'
                )],
                [InlineKeyboardButton(
                    text=f'🔗 {channel_name}',
                    url=channel_url
                )],
            ]
        ),
    )
    await callback.answer()


@guide_router.callback_query(F.data.startswith("check_membership_and_get_gift:"))
async def handle_gift_request(callback: types.CallbackQuery, bot: Bot):
    print('in handle_gift_request ...')
    user_id = callback.from_user.id
    is_subscribed = await check_channel_subscription(bot, user_id, channel_id=channel_id)

    if is_subscribed:
        # СЦЕНАРИЙ 1: Пользователь подписан — отдаем подарок
        product_id = callback.data.split(":")[1]
        product = await data.get_product(int(product_id))
        await callback.message.edit_text(
            f"✅ Спасибо за подписку!\n\n"
            f"📥 <a href='{product.product_url}'>Нажмите здесь, чтобы скачать гайд</a>",
            # Это позволит ссылке выглядеть как текст
            parse_mode="HTML",
            # Отключаем превью, чтобы не было лишних картинок под текстом
            link_preview_options=types.LinkPreviewOptions(is_disabled=True),
            reply_markup=back_main_menu_markup,
        )
        await data.create_action(
            tg_id=user_id,
            action_type=ActionType.FREE_GUIDE,
            details='Настоящая Сербия'
        )

    else:
        # Если НЕ подписан — показываем всплывающее окно (alert)
        await callback.answer(
            "😪 Пойми, мы долго работали над этим гайдом, поэтому отдаём его только за подписку...",
            # "Чтобы получить подарок, нужно сначала подписаться на канал! 👆",
            show_alert=True
        )
    await callback.answer()
