from os import environ

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


back_to_main_meny_btn = InlineKeyboardButton(
    text='👈🏼 Вернуться в начало',
    callback_data='main_menu'
)
back_to_road_trip_guide = InlineKeyboardButton(
    text='👈🏼 Вернуться',
    callback_data='road_trip_guide'
)
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
pay_tribute_btn = InlineKeyboardButton(
    text='Оплатить через Телеграм',
    url='https://t.me/tribute/app?startapp=pvzA'
)

pay_yookassa_btn = InlineKeyboardButton(
    text='Оплатить картой (ЮKassa)',
    callback_data='pay_yookassa:guide_1'
)

greating_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [i_want_to_go_on_a_road_trip_btn],
        [for_free_with_a_subscription_btn],
    ]
)
whats_in_depth_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [buy_a_guide_btn,],
        [suitable_for_whom_btn, who_is_not_suitable_btn],
        [whats_inside_btn,],
        [question_before_purchase_btn],
        [back_to_main_meny_btn],
    ]
)
whats_inside_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [buy_a_guide_btn],
        [back_to_road_trip_guide]
    ]
)
for_whom__markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [buy_a_guide_btn],
        [back_to_road_trip_guide]
    ]
)
by_or_ask_a_question_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [buy_a_guide_btn],
        [back_to_road_trip_guide]
    ]
)
buy_a_guide_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [pay_tribute_btn],
        [pay_yookassa_btn],
        [InlineKeyboardButton(
            text='👈🏼 Вернуться',
            callback_data='road_trip_guide'
        )]
    ]
)

# free_guide
CHANNEL_URL = environ.get("CHANNEL_URL")
get_free_guide_btn = InlineKeyboardButton(
    text='Забрать гайд бесплатно 🎁',
    callback_data='get_free_guide'
)
whats_inside_free_guide_btn = InlineKeyboardButton(
    text='Что внутри',
    callback_data='whats_inside_free_guide'
)
back_to_get_free_guide_btn = InlineKeyboardButton(
    text='👈🏼 Вернуться и забрать  🎁',
    callback_data='free_guide'
)


suitable_for_whom_free_guide_btn = InlineKeyboardButton(
    text='Кому подойдёт',
    callback_data='suitable_for_whom_free_guide'
)
subscribe_btn = InlineKeyboardButton(
    text='🔗 Подписаться на мой канал',
    url=CHANNEL_URL
)
check_membership_btn = InlineKeyboardButton(
    text='Я подписался, проверяй',
    callback_data='check_membership_and_get_gift'
)

free_guide_in_depth_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [get_free_guide_btn],
        [whats_inside_free_guide_btn],
        [suitable_for_whom_free_guide_btn],
        [back_to_main_meny_btn],
    ]
)
back_to_free_guide_in_depth_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [back_to_get_free_guide_btn,],
    ]
)
back_main_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [back_to_main_meny_btn,],
    ]
)
suitable_for_whom_free_guide_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [suitable_for_whom_free_guide_btn,],

    ]
)
free_guide_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [check_membership_btn,],
        [subscribe_btn,],
    ]
)
