from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI, WebSocket

from trading_agent.agent.adaptive import AdaptivePolicy
from trading_agent.agent.decision import DecisionContext, RuleBasedDecisionEngine
from trading_agent.api.schemas import AppConfig, AssetConfig, Decision, ExecutionConfig, PerformanceDTO, RiskConfig, TradeDTO
from trading_agent.data import database
from trading_agent.execution.binance import BinanceBroker, BinanceCredentials
from trading_agent.execution.broker import BrokerInterface, PaperBroker
from trading_agent.execution.position_manager import PositionManager
from trading_agent.services.stream import stream_manager
from trading_agent.strategy.detectors import Candle

app = FastAPI(title="Agente IA Trading")
adaptive_policy = AdaptivePolicy()
rule_engine = RuleBasedDecisionEngine()


def _default_config() -> AppConfig:
    return AppConfig(
        assets=[AssetConfig(symbol="BTCUSDT", enabled=True, timeframes=["1m", "5m", "15m"])],
        risk=RiskConfig(),
        execution=ExecutionConfig(),
    )


current_config: AppConfig = _default_config()


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
    return []


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
