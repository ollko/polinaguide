import os
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import (
    async_session,
    User,
    Action,
    SupportTicket,
    YookassaPayment,
    TributePayment,
    ActionType
)


engine = create_async_engine(os.environ['DB_URL'], echo=False)
Session = async_sessionmaker(engine)


async def create_or_update_user(tg_id: int, username: str = None) -> bool:
    async with Session() as session:

        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            print(f'Create new tg user {tg_id=} {username=}')
            new_user = User(
                tg_id=tg_id,
                username=username,
            )
            session.add(new_user)
            await session.commit()
            return True
        if username and username != user.username:
            print(
                f'Change username of {tg_id=} old username={user.username} new {username=}')
            user.username = username
            await session.commit()

        return False


async def update_user_status(tg_id: int, new_status: str):
    """
    Обновляет статус пользователя (active / blocked)
    """
    async with Session() as session:
        stmt = update(User).where(
            User.tg_id == tg_id).values(status=new_status)
        await session.execute(stmt)
        await session.commit()


async def save_question(session: AsyncSession, tg_id: int, question_text: str) -> int:
    async with Session() as session:
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


async def save_answer(ticket_id: int, answer_text: str):
    async with Session() as session:
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


async def create_tribute_payment(
        payload,
):
    transaction_id = str(payload.get("transaction_id"))
    async with async_session() as session:
        # 1. Идемпотентность: проверяем, нет ли уже такого платежа
        stmt = select(TributePayment).where(
            TributePayment.transaction_id == transaction_id)
        existing_payment = await session.scalar(stmt)

        if existing_payment:
            print(f"Платеж {transaction_id} уже обработан.")
            return dict(text="OK", status=200)

        telegram_user_id = payload.get("telegram_user_id")
        user = await session.get(User, telegram_user_id)

        if not user:
            print(f"Ошибка: Пользователь {telegram_user_id=} не найден в БД!")
            # Можно создать пользователя "на лету", если нужно
            return dict(text="User not found", status=200)

        product_name = payload.get("product_name")
        amount = payload.get("amount")
        currency = payload.get("currency")
        purchase_created_at = payload.get("purchase_created_at")
        new_payment = TributePayment(
            amount=amount,
            currency=currency,
            product_id=payload.get("product_id"),
            product_name=product_name,
            purchase_created_at=datetime.fromisoformat(purchase_created_at),
            purchase_id=payload.get("purchase_id"),
            telegram_user_id=telegram_user_id,
            telegram_username=payload.get("telegram_username"),
            transaction_id=transaction_id,
            trb_user_id=payload.get("trb_user_id"),
            user_id=payload.get("user_id"),
        )
        session.add(new_payment)
        await session.commit()

        return dict(
            text="OK",
            status=200,
            product_name=product_name,
            user_id=telegram_user_id,
            amount=amount,
            currency=currency,
        )

#             new_action = Action(
#                 user_id=user.id,
#                 action_type=ActionType.PURCHASE,
#                 payment_id=new_payment.id,
#                 details=f"Куплен товар: {new_payment.product_name}"
#             )
#             session.add(new_action)

#             await session.commit()
#             return dict(
#                 text="OK",
#                 status=200,
#                 product_id=product_id,
#                 user_id=tg_id,
#             )
#             # 6. ВЫДАЧА ТОВАРА (через бота)
#             # await bot.send_document(tg_id, ...)

#         except Exception as e:
#             await session.rollback()
#             print(f"Ошибка при сохранении в БД: {e}")
#             return dict(text="DB Error", status=200)


async def create_yookassa_payment(
        tg_id: int | str,
        payment,
):

    async with async_session() as session:
        new_payment = YookassaPayment(
            # Предполагаем, что id в таблице User равен tg_id
            user_id=int(tg_id),
            currency=payment.currency,
            total_amount=payment.total_amount,  # в копейках
            invoice_payload=payment.invoice_payload,
            telegram_payment_charge_id=payment.telegram_payment_charge_id,
            provider_payment_charge_id=payment.provider_payment_charge_id,
        )
        session.add(new_payment)
        await session.flush()
        new_payment_id = new_payment.id
        await session.commit()
        return new_payment_id


async def create_action(
    tg_id: int | str,
    action_type: ActionType,
    details: str,
):
    async with async_session() as session:
        new_action = Action(
            tg_id=int(tg_id),
            action_type=action_type,
            details=details
        )
        session.add(new_action)
        await session.flush()
        new_action_id = new_action.id
        await session.commit()
        return new_action_id


async def get_user_ids_for_notify():
    async with async_session() as session:
        stmt = '''
        SELECT tg_id, created_at
        FROM action
        WHERE 
            action_type='start'
            AND datetime(created_at, 'utc') > datetime('now', '-10 days')
            AND tg_id NOT IN (
                SELECT tg_id FROM action WHERE action_type='purchase'
            )
        '''
        result = await session.execute(text(stmt))
        return result.all()
