from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import User, Action, SupportTicket


async def create_or_update_user(session: AsyncSession, tg_id: int, username: str = None):
    query = select(User).where(User.tg_id == tg_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        new_user = User(
            tg_id=tg_id,
            username=username
        )
        session.add(new_user)
        await session.commit()
        return True
    if user.username != username:
        user.username = username
        await session.commit()

    return False


async def update_user_status(session: AsyncSession, tg_id: int, new_status: str):
    """
    Обновляет статус пользователя (active / blocked)
    """
    stmt = update(User).where(User.tg_id == tg_id).values(status=new_status)
    await session.execute(stmt)
    await session.commit()


async def save_question(session: AsyncSession, tg_id: int, question_text: str) -> int:
    user_query = select(User.id).where(User.tg_id == tg_id)
    result = await session.execute(user_query)
    user_id = result.scalar_one()

    new_ticket = SupportTicket(
        user_id=user_id,
        question=question_text
    )
    session.add(new_ticket)
    # Используем flush вместо commit, чтобы получить id нового тикета,
    # не закрывая транзакцию (commit будет позже в хэндлере или здесь)
    await session.flush()
    await session.commit()
    return new_ticket.id  # Возвращаем ID, чтобы потом найти этот тикет для ответа


async def save_answer(session: AsyncSession, ticket_id: int, answer_text: str):
    stmt = (
        update(SupportTicket)
        .where(SupportTicket.id == ticket_id)
        .values(answer=answer_text)
    )
    await session.execute(stmt)
    await session.commit()


async def log_action(
        session: AsyncSession,
        tg_id: int,
        action_type: str,
        currency: str,
        price: int,
):
    """
    Записывает действие пользователя (например, 'buy_guide') в таблицу Action
    """
    print('in log_action ...')
    print(f'{tg_id=}')
    user_query = select(User.id).where(User.tg_id == tg_id)
    result = await session.execute(user_query)
    user_id = result.scalar_one()

    new_action = Action(
        user_id=user_id,
        action_type=action_type,
        currency=currency,
        price=price,
    )
    session.add(new_action)
    await session.commit()
