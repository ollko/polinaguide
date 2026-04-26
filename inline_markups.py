from os import environ

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

i_want_to_go_on_a_road_trip_btn = InlineKeyboardButton(
    text='🚗 Авторский Гайд “Автопутешествие по Западной Сербии”',
    callback_data='road_trip_guide'
)

for_free_with_a_subscription_btn = InlineKeyboardButton(
    text='🎁 Бесплатно за подписку:\n"50 топовых природных мест Сербии"',
    callback_data='free_guide'
)
whats_inside_btn = InlineKeyboardButton(
    text='Что внутри',
    callback_data='whats_inside'
)
suitable_for_whom_btn = InlineKeyboardButton(
    text='Кому подойдёт',
    callback_data='suitable_for_whom'
)
who_is_not_suitable_btn = InlineKeyboardButton(
    text='Кому не подойдет',
    callback_data='who_is_not_suitable'
)
question_before_purchase_btn = InlineKeyboardButton(
    text='Задать свой вопрос перед покупкой',
    callback_data='ask_question_start'
)
buy_a_guide_btn = InlineKeyboardButton(
    text='Купить гайд',
    callback_data='buy_a_guide'
)
pay_stars_btn = InlineKeyboardButton(
    text='Оплатить Звездами (XTR)',
    callback_data='pay_stars'
)
pay_yookassa_btn = InlineKeyboardButton(
    text='Оплатить картой (ЮKassa)',
    callback_data='pay_yookassa'
)

greating_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [i_want_to_go_on_a_road_trip_btn],
        [for_free_with_a_subscription_btn],
    ]
)
whats_inside_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [whats_inside_btn,],
        [buy_a_guide_btn,],
    ]
)
for_whom__markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [suitable_for_whom_btn],
        [who_is_not_suitable_btn],
        [question_before_purchase_btn,],
    ]
)
by_or_ask_a_question_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [buy_a_guide_btn],
    ]
)
buy_a_guide_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [pay_stars_btn],
        [pay_yookassa_btn],
    ]
)

# free_guide
CHANNEL_URL = environ.get("CHANNEL_URL")
whats_inside_free_guide_btn = InlineKeyboardButton(
    text='Что внутри',
    callback_data='whats_inside_free_guide'
)
suitable_for_whom_free_guide_btn = InlineKeyboardButton(
    text='Кому подойдёт',
    callback_data='suitable_for_whom_free_guide'
)
free_guide_btn = InlineKeyboardButton(
    text='Забрать гайд бесплатно 🎁',
    callback_data='get_free_guide'
)
subscribe_btn = InlineKeyboardButton(
    text='🔗 Подписаться на мой канал',
    url=CHANNEL_URL
)
check_membership_btn = InlineKeyboardButton(
    text='Я подписался, проверяй',
    callback_data='Check_membership_and_get_gift'
)

whats_inside_free_guide_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [whats_inside_free_guide_btn,],
        [suitable_for_whom_free_guide_btn,],
        [free_guide_btn,],
    ]
)
suitable_for_whom_free_guide_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [suitable_for_whom_free_guide_btn,],
        [free_guide_btn,],
    ]
)
free_guide_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [subscribe_btn,],
        [check_membership_btn,],
    ]
)
