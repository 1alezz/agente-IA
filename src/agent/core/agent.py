from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from agent.config import AgentConfig
from agent.logging.logger import DashboardLogger
from agent.strategies import (
    FibonacciTargetDetector,
    FVGDetector,
    LiquiditySweepDetector,
    MarketStructureDetector,
    MovingAverageFilter,
    OrderBlockDetector,
    RSIDivergenceDetector,
    TurtleSoupDetector,
)
from agent.strategies.base import StrategySignal


@dataclass
class TradeDecision:
    action: str
    confidence: float
    reasons: List[str]
    metadata: Dict[str, float | str]


class TradingAgent:
    def __init__(self, config: AgentConfig, logger: DashboardLogger) -> None:
        self.config = config
        self.logger = logger
        self.detectors = self._build_detectors()

    def _build_detectors(self) -> List:
        toggles = self.config.strategy_toggles
        detectors = []
        if toggles.order_blocks:
            detectors.append(OrderBlockDetector())
        if toggles.fvg:
            detectors.append(FVGDetector())
        if toggles.liquidity_sweeps:
            detectors.append(LiquiditySweepDetector())
        if toggles.rsi_divergence:
            detectors.append(RSIDivergenceDetector())
        if toggles.market_structure:
            detectors.append(MarketStructureDetector())
        if toggles.turtle_soup:
            detectors.append(TurtleSoupDetector())
        if toggles.moving_averages:
            detectors.append(MovingAverageFilter())
        if toggles.fibonacci_targets:
            detectors.append(FibonacciTargetDetector())
        return detectors

    def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> TradeDecision:
        signals: List[StrategySignal] = []
        for detector in self.detectors:
            signals.extend(detector.detect(data))
        bullish = [s for s in signals if "bullish" in s.signal or "buy" in s.signal or "trend_up" in s.signal]
        bearish = [s for s in signals if "bearish" in s.signal or "sell" in s.signal or "trend_down" in s.signal]
        if len(bullish) > len(bearish):
            action = "buy"
            confidence = min(0.9, 0.5 + 0.05 * len(bullish))
            reasons = [s.signal for s in bullish]
        elif len(bearish) > len(bullish):
            action = "sell"
            confidence = min(0.9, 0.5 + 0.05 * len(bearish))
            reasons = [s.signal for s in bearish]
        else:
            action = "hold"
            confidence = 0.4
            reasons = [s.signal for s in signals]
        self.logger.log(
            "info",
            f"{symbol} [{timeframe}]: decisão {action} com {len(signals)} sinais.",
            symbol=symbol,
            timeframe=timeframe,
        )
        return TradeDecision(action=action, confidence=confidence, reasons=reasons, metadata={})
