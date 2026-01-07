from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Sequence

from pydantic import BaseModel, Field


class StrategyParams(BaseModel):
    rsi_threshold: int | None = Field(default=30, ge=0, le=100)
    lookback: int = Field(default=50, gt=0)
    risk_per_trade: float = Field(default=1.0, gt=0)
    use_ma_confirmation: bool = False


class StrategyConfig(BaseModel):
    enabled: bool = True
    params: StrategyParams = Field(default_factory=StrategyParams)


class AssetConfig(BaseModel):
    symbol: str
    enabled: bool = True
    timeframes: list[str] = Field(default_factory=lambda: ["1m", "5m", "15m"])
    strategies: dict[str, StrategyConfig] = Field(default_factory=dict)


class RiskConfig(BaseModel):
    risk_per_trade: float = 1.0
    daily_risk_limit: float = 5.0
    max_trades_per_day: int = 10
    max_exposure_per_asset: float = 2.0
    max_position_size: float = 1000.0
    leverage: float | None = None
    order_size_mode: Literal["fixed", "risk", "atr"] = "risk"
    order_size_value: float | None = None


class ExecutionConfig(BaseModel):
    mode: Literal["paper", "testnet", "live"] = "paper"
    allow_live: bool = False
    slippage_bps: float = 5
    order_type: Literal["market", "limit"] = "market"
    spread_limit_bps: float = 10
    broker: Literal["paper", "binance_testnet", "binance_live"] = "paper"
    api_key: str | None = None
    api_secret: str | None = None
    backtest_duration_minutes: int | None = None


class AppConfig(BaseModel):
    assets: list[AssetConfig]
    risk: RiskConfig = Field(default_factory=RiskConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    sessions: list[str] = Field(default_factory=lambda: ["london", "newyork", "asia"])


class SignalMetadata(BaseModel):
    signal: bool
    score: float
    notes: str
    plot: dict[str, Any] = Field(default_factory=dict)


class Decision(BaseModel):
    action: Literal["enter", "wait"]
    side: Literal["long", "short", "flat"] = "flat"
    symbol: str | None = None
    timeframe: str | None = None
    entry: float | None = None
    stop_loss: float | None = None
    take_profits: list[float] = Field(default_factory=list)
    size: float | None = None
    narrative: str = ""
    confluence: float = 0.0
    signals: dict[str, SignalMetadata] = Field(default_factory=dict)


class TradeDTO(BaseModel):
    id: int | None = None
    symbol: str
    timeframe: str
    side: str
    entry: float
    stop_loss: float
    take_profit: float
    size: float
    status: str
    pnl: float | None
    r_multiple: float | None
    opened_at: datetime
    closed_at: datetime | None
    narrative: str
    metadata: dict[str, Any] | None


class PerformanceDTO(BaseModel):
    symbol: str
    timeframe: str
    sharpe: float
    max_drawdown: float
    winrate: float
    expectancy: float
    profit_factor: float


class StreamMessage(BaseModel):
    channel: Literal["candles", "signals", "positions", "logs", "performance"]
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
