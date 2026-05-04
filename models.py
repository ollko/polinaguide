from datetime import datetime
from os import getenv
from typing import List

from sqlalchemy import Integer, BigInteger, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


DB_URL = getenv('DB_URL')

engine = create_async_engine(DB_URL, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now())
    status: Mapped[str] = mapped_column(
        String, default="active")  # active / blocked

    actions: Mapped[List["Action"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    support_tickets: Mapped[List["SupportTicket"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Action(Base):
    __tablename__ = 'action'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'))
    action_type: Mapped[str] = mapped_column(
        String)  # "free_guide", "buy_guide"
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=True)

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
    answer: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="support_tickets")
