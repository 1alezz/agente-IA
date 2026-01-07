from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TradingMode(str, Enum):
    PAPER = "paper"
    TESTNET = "testnet"
    LIVE = "live"


JSONType = JSON().with_variant(JSONB(), "postgresql")


class Config(Base):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    raw: Mapped[dict[str, Any]] = mapped_column(JSONType)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10))
    side: Mapped[str] = mapped_column(String(4))
    entry: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)
    size: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="open")
    pnl: Mapped[float | None] = mapped_column(Float)
    r_multiple: Mapped[float | None] = mapped_column(Float)
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)
    narrative: Mapped[str] = mapped_column(Text)
    metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONType)


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10))
    side: Mapped[str] = mapped_column(String(4))
    size: Mapped[float] = mapped_column(Float)
    entry: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SignalLog(Base):
    __tablename__ = "signal_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10))
    signal_type: Mapped[str] = mapped_column(String(50))
    score: Mapped[float] = mapped_column(Float)
    details: Mapped[dict[str, Any]] = mapped_column(JSONType)


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10))
    sharpe: Mapped[float] = mapped_column(Float)
    max_drawdown: Mapped[float] = mapped_column(Float)
    winrate: Mapped[float] = mapped_column(Float)
    expectancy: Mapped[float] = mapped_column(Float)
    profit_factor: Mapped[float] = mapped_column(Float)
    period_start: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    period_end: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModelState(Base):
    __tablename__ = "model_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10))
    algorithm: Mapped[str] = mapped_column(String(50))
    blob: Mapped[dict[str, Any]] = mapped_column(JSONType)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
