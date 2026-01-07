from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.config import AgentConfig, AssetConfig, BinanceSettings, RiskSettings, StrategyToggles
from agent.logging.logger import DashboardLogger

app = FastAPI(title="Agente IA Trading Dashboard")
logger = DashboardLogger("dashboard")
logger.configure("INFO")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AssetConfigModel(BaseModel):
    symbol: str
    timeframes: List[str]
    enabled: bool = True


class StrategyTogglesModel(BaseModel):
    order_blocks: bool = True
    fvg: bool = True
    liquidity_sweeps: bool = True
    rsi_divergence: bool = True
    market_structure: bool = True
    turtle_soup: bool = True
    moving_averages: bool = True
    fibonacci_targets: bool = True


class RiskSettingsModel(BaseModel):
    risk_per_trade: float = 0.02
    max_drawdown_daily: float = 0.05
    max_consecutive_losses: int = 3
    leverage: int = 1
    max_position_pct: float = 0.1


class BinanceSettingsModel(BaseModel):
    api_key: str = ""
    api_secret: str = ""
    testnet: bool = True


class AgentConfigModel(BaseModel):
    assets: List[AssetConfigModel] = []
    strategy_toggles: StrategyTogglesModel = StrategyTogglesModel()
    risk: RiskSettingsModel = RiskSettingsModel()
    binance: BinanceSettingsModel = BinanceSettingsModel()
    log_level: str = "INFO"
    initial_equity: float = 10_000.0


state_config = AgentConfig()


@app.get("/")
def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/config", response_model=AgentConfigModel)
def get_config() -> AgentConfigModel:
    return AgentConfigModel(
        assets=[AssetConfigModel(**asset.__dict__) for asset in state_config.assets],
        strategy_toggles=StrategyTogglesModel(**state_config.strategy_toggles.__dict__),
        risk=RiskSettingsModel(**state_config.risk.__dict__),
        binance=BinanceSettingsModel(**state_config.binance.__dict__),
        log_level=state_config.log_level,
        initial_equity=state_config.initial_equity,
    )


@app.post("/config", response_model=AgentConfigModel)
def update_config(config: AgentConfigModel) -> AgentConfigModel:
    global state_config
    state_config = AgentConfig(
        assets=[AssetConfig(**asset.dict()) for asset in config.assets],
        strategy_toggles=StrategyToggles(**config.strategy_toggles.dict()),
        risk=RiskSettings(**config.risk.dict()),
        binance=BinanceSettings(**config.binance.dict()),
        log_level=config.log_level,
        initial_equity=config.initial_equity,
    )
    logger.configure(state_config.log_level)
    logger.log("info", "Configurações atualizadas via dashboard.")
    return get_config()


@app.get("/logs")
def get_logs() -> list:
    return [event.__dict__ for event in logger.buffer.list_events()]


@app.post("/test-connection")
def test_connection() -> dict:
    if not state_config.binance.api_key or not state_config.binance.api_secret:
        raise HTTPException(status_code=400, detail="API key/secret não informadas")
    logger.log("info", "Teste de conexão solicitado.")
    return {"status": "pending", "detail": "Teste de conexão agendado."}


@app.get("/api/config", response_model=AgentConfigModel)
def api_get_config() -> AgentConfigModel:
    return get_config()


@app.post("/api/config", response_model=AgentConfigModel)
def api_update_config(config: AgentConfigModel) -> AgentConfigModel:
    return update_config(config)


@app.get("/api/logs")
def api_get_logs() -> list:
    return get_logs()


@app.post("/api/test-connection")
def api_test_connection() -> dict:
    return test_connection()
