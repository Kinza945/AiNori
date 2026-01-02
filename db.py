from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import BigInteger, DateTime, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import settings
from crypto import decrypt, encrypt


class Base(DeclarativeBase):
    pass


class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


engine = create_async_engine(settings.database_url, echo=False, future=True)
AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def _decrypt_field(value: str | None) -> str | None:
    if value is None:
        return None
    return decrypt(value)


def _encrypt_field(value: str | None) -> str | None:
    if value is None:
        return None
    return encrypt(value)


async def _get_by_telegram_id(session: AsyncSession, telegram_id: int) -> UserToken | None:
    stmt = select(UserToken).where(UserToken.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def save_tokens(
    telegram_id: int,
    access_token: str,
    refresh_token: str,
    expires_at: dt.datetime,
    scope: str | None = None,
) -> None:
    async with AsyncSessionMaker() as session:
        async with session.begin():
            existing = await _get_by_telegram_id(session, telegram_id)
            if existing is None:
                existing = UserToken(telegram_id=telegram_id)
                session.add(existing)
            existing.access_token = _encrypt_field(access_token)
            existing.refresh_token = _encrypt_field(refresh_token)
            existing.expires_at = expires_at
            existing.scope = scope


async def get_tokens(telegram_id: int) -> UserToken | None:
    async with AsyncSessionMaker() as session:
        result = await _get_by_telegram_id(session, telegram_id)
        if result is None:
            return None
        result.access_token = _decrypt_field(result.access_token) or ""
        result.refresh_token = _decrypt_field(result.refresh_token) or ""
        return result
