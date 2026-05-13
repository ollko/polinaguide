from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_main_menu(bot: Bot):
    # Формируем список команд для меню
    main_menu_commands = [
        BotCommand(command='/start', description='Начать работу с ботом'),
        BotCommand(command='/my_guides', description='Мои гайды'),
    ]

    # Регистрируем команды в Telegram
    await bot.set_my_commands(
        commands=main_menu_commands,
        scope=BotCommandScopeDefault()
    )
