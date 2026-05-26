from async_lru import alru_cache
from datetime import datetime
from collections.abc import Sequence
import os
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text, Row
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import (
    async_session,
    User,
    Action,
    SupportTicket,
    YookassaPayment,
    TributePayment,
    ActionType,
    Product
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


async def save_question(tg_id: int, question_text: str) -> int:
    async with Session() as session:
        user = await session.get(User, tg_id)
        print(f'{user=}')

        new_ticket = SupportTicket(
            tg_id=user.tg_id,
            question=question_text
        )
        session.add(new_ticket)
        # Используем flush вместо commit, чтобы получить id нового тикета,
        # не закрывая транзакцию (commit будет позже в хэндлере или здесь)
        await session.flush()
        new_ticket_id = new_ticket.id
        await session.commit()
        return new_ticket_id  # Возвращаем ID, чтобы потом найти этот тикет для ответа


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

        # 3. НАХОДИМ ВНУТРЕННИЙ prod_id ИЗ ТАБЛИЦЫ PRODUCT
        stmt_prod = select(Product.id).where(
            Product.product_name == product_name)
        prod_id = await session.scalar(stmt_prod)

        if not prod_id:
            print(
                f"⚠️ Предупреждение: Товар с именем '{product_name}' не найден в таблице product. Поле prod_id будет NULL.")
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
            prod_id=prod_id,
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


@alru_cache(maxsize=1)
async def get_products(ids: tuple[int] | None = None) -> Sequence[Product]:
    async with async_session() as session:
        stmt = select(Product)
        if ids:
            stmt = stmt.where(Product.id.in_(ids))
        result = await session.scalars(stmt)
        return result.all()


@alru_cache(maxsize=8)
async def get_product(id: int):
    async with async_session() as session:
        # Возвращает объект или None, если запись не найдена
        return await session.get(Product, id)


@alru_cache(maxsize=8)
async def get_product_url(product_name: str) -> str | None:
    async with async_session() as session:
        stmt = (
            select(Product.product_url)
            .where(Product.product_name == product_name)
        )
        # Возвращает первый элемент первой строки результата
        # или  None если ничего не найдено
        result = await session.scalar(stmt)
        print(f'{result=}')
        return await session.scalar(stmt)


async def get_purchased_products(user_id: int) -> Sequence[Row[Any]]:
    async with async_session() as session:
        stmt = text("""
            SELECT p.product_name, p.product_url
            FROM product p
            INNER JOIN yookassa_payment y ON p.id = y.prod_id
            WHERE y.user_id = :user_id
            
            UNION
            
            SELECT p.product_name, p.product_url
            FROM product p
            INNER JOIN tribute_payment t ON p.id = t.prod_id
            WHERE t.telegram_user_id = :user_id
        """)

        result = await session.execute(stmt, {"user_id": user_id})

        # Возвращаем список словарей или generic-объектов
        return result.all()


@alru_cache(maxsize=8)
async def get_free_products() -> Sequence[Row[Any]]:
    async with async_session() as session:
        stmt = (
            select(Product.product_name, Product.product_url)
            .where(Product.free == True)
        )
        result = await session.execute(stmt)
        return result.all()


async def get_users_who_did_not_buy_product(today_date_str: str):
    async with Session() as session:
        stmt = """
        SELECT 
            u.tg_id, 
            n.notification,
            n.product_id
        FROM user u
        CROSS JOIN notification n

        -- Вычисляем разницу в днях (текущая дата минус дата создания экшена)
        WHERE CAST(JULIANDAY(:today_date) - JULIANDAY(DATE(u.registered_at)) AS INTEGER) = n.day_delta

        -- Исключаем тех, кто в итоге купил этот гайд
        AND NOT EXISTS (
            SELECT 1 
            FROM action ap
            WHERE ap.tg_id = u.tg_id
                AND ap.product_id = n.product_id
                AND ap.action_type = 'PURCHASE'
        );
        """
        result = await session.execute(text(stmt), {"today_date": today_date_str})
        rows = result.all()
        print(f'{rows=}')
        return rows
