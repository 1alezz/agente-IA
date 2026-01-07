from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StrategyToggles:
    order_blocks: bool = True
    fvg: bool = True
    liquidity_sweeps: bool = True
    rsi_divergence: bool = True
    market_structure: bool = True
    turtle_soup: bool = True
    moving_averages: bool = True
    fibonacci_targets: bool = True


@dataclass
class RiskSettings:
    risk_per_trade: float = 0.02
    max_drawdown_daily: float = 0.05
    max_consecutive_losses: int = 3
    leverage: int = 1
    max_position_pct: float = 0.1


@dataclass
class AssetConfig:
    symbol: str
    timeframes: List[str]
    enabled: bool = True


@dataclass
class BinanceSettings:
    api_key: str = ""
    api_secret: str = ""
    testnet: bool = True


@dataclass
class AgentConfig:
    assets: List[AssetConfig] = field(default_factory=list)
    strategy_toggles: StrategyToggles = field(default_factory=StrategyToggles)
    risk: RiskSettings = field(default_factory=RiskSettings)
    binance: BinanceSettings = field(default_factory=BinanceSettings)
    log_level: str = "INFO"
    initial_equity: float = 10_000.0

    def assets_by_symbol(self) -> Dict[str, AssetConfig]:
        return {asset.symbol: asset for asset in self.assets}
