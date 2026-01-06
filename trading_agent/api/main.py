from __future__ import annotations

import asyncio
from typing import Any

from fastapi import Depends, FastAPI, WebSocket

from trading_agent.agent.adaptive import AdaptivePolicy
from trading_agent.agent.decision import DecisionContext, RuleBasedDecisionEngine
from trading_agent.api.schemas import AppConfig, Decision, PerformanceDTO, TradeDTO
from trading_agent.data import database
from trading_agent.execution.broker import PaperBroker
from trading_agent.execution.position_manager import PositionManager
from trading_agent.services.stream import stream_manager
from trading_agent.strategy.detectors import Candle

app = FastAPI(title="Agente IA Trading")
adaptive_policy = AdaptivePolicy()
rule_engine = RuleBasedDecisionEngine()
broker = PaperBroker()
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
    return {"message": "config fetch placeholder"}


@app.put("/config")
async def update_config(config: AppConfig) -> dict[str, Any]:
    return {"message": "config updated", "assets": [a.symbol for a in config.assets]}


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
