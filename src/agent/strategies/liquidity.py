from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal


class LiquiditySweepDetector(StrategyDetector):
    name = "liquidity_sweeps"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < 10:
            return signals
        recent = data.iloc[-10:]
        high_level = recent["high"].max()
        low_level = recent["low"].min()
        last = data.iloc[-1]
        if last["high"] > high_level and last["close"] < high_level:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="sell_sweep",
                    confidence=0.58,
                    metadata={"level": float(high_level)},
                )
            )
        if last["low"] < low_level and last["close"] > low_level:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="buy_sweep",
                    confidence=0.58,
                    metadata={"level": float(low_level)},
                )
            )
        return signals
