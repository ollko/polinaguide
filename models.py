from datetime import datetime
import enum
from os import getenv
from typing import List, Optional

from sqlalchemy import Integer, BigInteger, String, ForeignKey, DateTime, Text, func, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


DB_URL = getenv('DB_URL')

engine = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(engine)


class ActionType(enum.Enum):
    START = "start"
    FREE_GUIDE = "free_guide"
    PURCHASE = "purchase"
    GROUP_JOIN = "group_join"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    trb_user_id: Mapped[Optional[str]] = mapped_column(
        String, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now())

    status: Mapped[str] = mapped_column(
        String, default="active", server_default="active")  # active / blocked

    payments: Mapped[List["Payment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    actions: Mapped[List["Action"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    support_tickets: Mapped[List["SupportTicket"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Payment(Base):
    __tablename__ = 'payment'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))

    external_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True)

    product_name: Mapped[str] = mapped_column(String(255))
    # Сохраняем ID для логики выдачи (проще сравнивать "guide_1", чем "Гайд по похудению v2.0")
    product_id: Mapped[str] = mapped_column(String(100), index=True)

    amount: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(10))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="payments")


class Action(Base):
    __tablename__ = 'action'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))

    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False),
        index=True,
    )

    # Ссылка на платеж (опционально)
    # Если действие — покупка, тут будет ID из таблицы Payment
    payment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('payment.id', ondelete='SET NULL'),
        nullable=True,
        default=None,
    )

    # Текстовое описание для истории (например, "Купил гайд через Tribute")
    details: Mapped[str] = mapped_column(
        String(255), nullable=True, default='')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="actions")


class SupportTicket(Base):
    __tablename__ = 'support_ticket'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    question_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    answer_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user: Mapped["User"] = relationship(back_populates="support_tickets")
