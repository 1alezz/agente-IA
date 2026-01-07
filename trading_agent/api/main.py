from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from trading_agent.agent.adaptive import AdaptivePolicy
from trading_agent.agent.decision import DecisionContext, RuleBasedDecisionEngine
from trading_agent.api.schemas import AppConfig, AssetConfig, Decision, ExecutionConfig, PerformanceDTO, RiskConfig, TradeDTO
from trading_agent.backtest.runner import Backtester
from trading_agent.data import database
from trading_agent.execution.binance import BinanceBroker, BinanceCredentials
from trading_agent.execution.broker import BrokerInterface, PaperBroker
from trading_agent.execution.position_manager import PositionManager
from trading_agent.services.stream import stream_manager
from trading_agent.strategy.detectors import Candle

app = FastAPI(title="Agente IA Trading")
adaptive_policy = AdaptivePolicy()
rule_engine = RuleBasedDecisionEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dashboard_dist = Path(__file__).resolve().parents[2] / "dashboard" / "dist"
if dashboard_dist.exists():
    app.mount("/assets", StaticFiles(directory=dashboard_dist / "assets"), name="assets")


def _default_config() -> AppConfig:
    return AppConfig(
        assets=[AssetConfig(symbol="BTCUSDT", enabled=True, timeframes=["1m", "5m", "15m"])],
        risk=RiskConfig(),
        execution=ExecutionConfig(),
    )


current_config: AppConfig = _default_config()
backtest_status: dict[str, Any] = {"running": False, "last_run": None}
backtest_task: asyncio.Task | None = None
performance_cache: list[PerformanceDTO] = []


def build_broker(exec_config: ExecutionConfig) -> BrokerInterface:
    if exec_config.broker.startswith("binance") or exec_config.mode in {"testnet", "live"}:
        creds = BinanceCredentials.from_config(exec_config.api_key, exec_config.api_secret)
        sandbox = exec_config.broker == "binance_testnet" or exec_config.mode == "testnet"
        return BinanceBroker(creds, sandbox=sandbox)
    return PaperBroker()


broker: BrokerInterface = build_broker(current_config.execution)
position_manager = PositionManager(broker=broker)


@app.on_event("startup")
async def startup() -> None:
    asyncio.create_task(stream_manager.broadcaster())
    await database.init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def dashboard_index() -> FileResponse:
    if dashboard_dist.exists():
        return FileResponse(dashboard_dist / "index.html")
    return FileResponse(Path(__file__).resolve().parents[2] / "README.md")


@app.get("/config")
async def get_config() -> dict[str, Any]:
    return current_config.model_dump()


@app.put("/config")
async def update_config(config: AppConfig) -> dict[str, Any]:
    global current_config, broker, position_manager
    current_config = config
    broker = build_broker(config.execution)
    position_manager = PositionManager(broker=broker)
    return {"message": "config updated", "assets": [a.symbol for a in config.assets], "broker": config.execution.broker}


@app.post("/agent/start")
async def start_agent() -> dict[str, str]:
    return {"status": "started"}


@app.post("/agent/stop")
async def stop_agent() -> dict[str, str]:
    return {"status": "stopped"}


@app.get("/symbols")
async def get_symbols() -> list[str]:
    return ["BTCUSDT", "ETHUSDT", "EURUSD"]


@app.get("/state")
async def get_state() -> dict[str, Any]:
    positions = await broker.get_positions()
    balance = await broker.get_balance()
    return {"positions": positions, "balance": balance}


@app.get("/trades")
async def get_trades() -> list[TradeDTO]:
    return []


@app.get("/performance")
async def get_performance() -> list[PerformanceDTO]:
    return performance_cache


def _generate_candles(count: int, start_price: float = 100.0) -> list[Candle]:
    candles: list[Candle] = []
    price = start_price
    now = datetime.utcnow()
    for i in range(count):
        drift = random.uniform(-0.5, 0.5)
        open_price = price
        close_price = max(1.0, price + drift)
        high = max(open_price, close_price) + random.uniform(0.1, 0.6)
        low = max(0.1, min(open_price, close_price) - random.uniform(0.1, 0.6))
        candles.append(
            Candle(
                timestamp=now + timedelta(minutes=i),
                open=open_price,
                high=high,
                low=low,
                close=close_price,
                volume=random.uniform(100, 500),
            )
        )
        price = close_price
    return candles


async def _run_backtest() -> None:
    global performance_cache, backtest_status
    backtest_status = {"running": True, "last_run": datetime.utcnow().isoformat()}
    duration = current_config.execution.backtest_duration_minutes or 120
    backtester = Backtester()
    metrics: list[PerformanceDTO] = []
    for asset in current_config.assets:
        if not asset.enabled:
            continue
        for timeframe in asset.timeframes:
            candles = _generate_candles(duration)
            result = backtester.run(asset.symbol, timeframe, candles)
            metrics.append(
                PerformanceDTO(
                    symbol=asset.symbol,
                    timeframe=timeframe,
                    sharpe=result.sharpe,
                    max_drawdown=0.0,
                    winrate=0.0,
                    expectancy=0.0,
                    profit_factor=0.0,
                )
            )
    performance_cache = metrics
    backtest_status["running"] = False


@app.post("/backtest/start")
async def start_backtest() -> dict[str, Any]:
    global backtest_task
    if backtest_task and not backtest_task.done():
        return {"status": "already_running"}
    backtest_task = asyncio.create_task(_run_backtest())
    return {"status": "started", "duration_minutes": current_config.execution.backtest_duration_minutes}


@app.post("/backtest/pause")
async def pause_backtest() -> dict[str, Any]:
    global backtest_task
    if backtest_task and not backtest_task.done():
        backtest_task.cancel()
        backtest_status["running"] = False
        return {"status": "paused"}
    return {"status": "not_running"}


@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await stream_manager.stream(websocket)


@app.post("/decide")
async def decide(payload: dict[str, Any]) -> Decision:
    candles = [Candle(**c) for c in payload["candles"]]
    context = DecisionContext(
        symbol=payload["symbol"],
        timeframe=payload["timeframe"],
        candles=candles,
        risk_config=payload.get("risk_config", {}),
        strategy_params=payload.get("strategy_params", {}),
    )
    mode = payload.get("mode", "rule")
    if mode == "adaptive":
        decision = adaptive_policy.decide(context)
    else:
        decision = rule_engine.evaluate(context)
    await stream_manager.publish({"channel": "signals", "payload": decision.model_dump()})
    return decision


@app.post("/execute")
async def execute(decision: Decision) -> dict[str, Any]:
    result = await position_manager.execute_decision(decision)
    await stream_manager.publish({"channel": "positions", "payload": result})
    return result
