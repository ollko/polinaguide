from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import async_session, User, Action, SupportTicket, Payment, ActionType


async def create_or_update_user(session: AsyncSession, tg_id: int, username: str = None) -> bool:
    query = select(User).where(User.tg_id == tg_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    print(f'{type(tg_id)=} {username=}')
    if not user:
        new_user = User(
            tg_id=tg_id,
            username=username,
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


async def create_payment_and_action(
        payload: dict,
):

    tg_id = payload.get("telegram_user_id")
    trans_id = str(payload.get("transaction_id"))
    trb_user_id = payload.get("trb_user_id")
    async with async_session() as session:
        # 1. Идемпотентность: проверяем, нет ли уже такого платежа
        stmt = select(Payment).where(Payment.external_id == trans_id)
        existing_payment = await session.scalar(stmt)

        if existing_payment:
            print(f"Платеж {trans_id} уже обработан.")
            return dict(text="OK", status=200)

        stmt_user = select(User).where(User.tg_id == tg_id)
        user = await session.scalar(stmt_user)

        if not user:
            print(f"Ошибка: Пользователь {tg_id} не найден в БД!")
            # Можно создать пользователя "на лету", если нужно
            return dict(text="User not found", status=200)
        if user and not user.trb_user_id:
            user.trb_user_id = trb_user_id

        try:
            product_id = str(payload.get("product_id", "unknown"))
            new_payment = Payment(
                user_id=user.id,
                external_id=trans_id,
                product_name=payload.get("product_name", "Без названия"),
                product_id=product_id,
                amount=payload.get("amount"),
                currency=payload.get("currency")
            )
            session.add(new_payment)
            await session.flush()
            print('after session.flush')

            new_action = Action(
                user_id=user.id,
                action_type=ActionType.PURCHASE,
                payment_id=new_payment.id,
                details=f"Куплен товар: {new_payment.product_name}"
            )
            session.add(new_action)

            await session.commit()
            return dict(
                text="OK",
                status=200,
                product_id=product_id,
                user_id=tg_id,
            )
            # 6. ВЫДАЧА ТОВАРА (через бота)
            # await bot.send_document(tg_id, ...)

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при сохранении в БД: {e}")
            return dict(text="DB Error", status=200)


async def create_payment_and_action_yookassa(
        tg_id: int | str,
        external_id: str,
        product_name: str,
        product_id: str,
        amount: int,  # в копейках
        currency: str,
        details_str: str,

):

    async with async_session() as session:

        stmt_user = select(User).where(User.tg_id == tg_id)
        user = await session.scalar(stmt_user)

        if not user:
            print(f"Ошибка: Пользователь {tg_id} не найден в БД!")
            # Можно создать пользователя "на лету", если нужно
            return
        else:
            new_payment = Payment(
                user_id=user.id,  # Предполагаем, что id в таблице User равен tg_id
                external_id=external_id,
                product_name=product_name,
                product_id=product_id,
                amount=amount,  # в копейках
                currency=currency
            )

            session.add(new_payment)
            await session.flush()

            new_action = Action(
                user_id=user.id,
                action_type=ActionType.PURCHASE,  # Твой Enum элемент для покупок
                payment_id=new_payment.id,
                details=details_str
            )
            session.add(new_action)

            await session.commit()

            return dict(text="OK", status=200)
