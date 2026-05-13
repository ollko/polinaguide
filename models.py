from datetime import datetime
import enum
from os import getenv
from typing import List, Optional

from sqlalchemy import (
    Integer, BigInteger, String, ForeignKey, DateTime, Text, func, Enum, Boolean,
)
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

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now())

    status: Mapped[str] = mapped_column(
        String, default="active", server_default="active")  # active / blocked

    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False)

    yookassa_payments: Mapped[List["YookassaPayment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    tribute_payments: Mapped[List["TributePayment"]] = relationship(
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


class YookassaPayment(Base):
    __tablename__ = 'yookassa_payment'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.tg_id', ondelete='SET NULL'))
    currency: Mapped[str] = mapped_column(String(3))

    total_amount: Mapped[int] = mapped_column(Integer)
    invoice_payload: Mapped[str] = mapped_column(String(50))
    telegram_payment_charge_id:  Mapped[str] = mapped_column(String(32))
    provider_payment_charge_id: Mapped[str] = mapped_column(String(40))

    user: Mapped["User"] = relationship(back_populates="yookassa_payments")


class TributePayment(Base):
    __tablename__ = 'tribute_payment'

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))

    product_id: Mapped[int] = mapped_column(Integer)
    product_name: Mapped[str] = mapped_column(String(50))
    purchase_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True))
    purchase_id: Mapped[int] = mapped_column(Integer)
    telegram_user_id: Mapped[int] = mapped_column(
        ForeignKey('user.tg_id', ondelete='SET NULL'))
    telegram_username: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    transaction_id: Mapped[int] = mapped_column(Integer)
    trb_user_id: Mapped[str] = mapped_column(String(10))
    user_id: Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="tribute_payments")


class Action(Base):
    __tablename__ = 'action'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(
        ForeignKey('user.tg_id', ondelete='CASCADE'))

    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    details: Mapped[str] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="actions")


class SupportTicket(Base):
    __tablename__ = 'support_ticket'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(
        ForeignKey('user.tg_id', ondelete='SET NULL'))
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
