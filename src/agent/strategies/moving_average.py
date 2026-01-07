from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal
from .indicators import ema


class MovingAverageFilter(StrategyDetector):
    name = "moving_averages"

    def __init__(self, fast: int = 50, slow: int = 200) -> None:
        self.fast = fast
        self.slow = slow

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < self.slow:
            return signals
        close = data["close"]
        fast_ma = ema(close, self.fast).iloc[-1]
        slow_ma = ema(close, self.slow).iloc[-1]
        if fast_ma > slow_ma:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="trend_up",
                    confidence=0.52,
                    metadata={"fast_ma": float(fast_ma), "slow_ma": float(slow_ma)},
                )
            )
        if fast_ma < slow_ma:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="trend_down",
                    confidence=0.52,
                    metadata={"fast_ma": float(fast_ma), "slow_ma": float(slow_ma)},
                )
            )
        return signals
