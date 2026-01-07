from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./trading.db"

Base = declarative_base()

_engine: AsyncEngine | None = None
_SessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_engine(url: str = DATABASE_URL) -> AsyncEngine:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_async_engine(url, echo=False, future=True)
        _SessionLocal = async_sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    engine = get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session


async def init_db(url: str = DATABASE_URL) -> None:
    engine = get_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
