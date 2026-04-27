from aiogram import Router, types, F
from aiogram.filters.command import CommandStart
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated

from sqlalchemy.ext.asyncio import AsyncSession

from data import (
    create_or_update_user,
    update_user_status,
)
from texts import (
    GREATING_TEXT,
)
from inline_markups import greating_markup
start_router = Router()


@start_router.message(CommandStart())
async def start(message: types.Message, session: AsyncSession):
    """Return 'Start' button"""
    await create_or_update_user(
        session=session,
        tg_id=message.from_user.id,
        username=message.from_user.username
    )
    await message.answer(
        text=GREATING_TEXT,
        reply_markup=greating_markup,
    )


@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def on_user_blocked(event: ChatMemberUpdated, session: AsyncSession):
    '''Handler will be triggered when the status changes to 'kicked' (the user has blocked the bot)'''
    await update_user_status(session, event.from_user.id, "blocked")


@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def on_user_unblocked(event: ChatMemberUpdated, session: AsyncSession):
    '''The handler will be triggered when the user has unblocked the bot back.'''
    await update_user_status(session, event.from_user.id, "active")
