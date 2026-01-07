from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal


class TurtleSoupDetector(StrategyDetector):
    name = "turtle_soup"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < 20:
            return signals
        recent = data.iloc[-20:]
        swing_high = recent["high"].max()
        swing_low = recent["low"].min()
        last = data.iloc[-1]
        if last["high"] > swing_high and last["close"] < swing_high:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="turtle_soup_sell",
                    confidence=0.6,
                    metadata={"sweep_level": float(swing_high)},
                )
            )
        if last["low"] < swing_low and last["close"] > swing_low:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="turtle_soup_buy",
                    confidence=0.6,
                    metadata={"sweep_level": float(swing_low)},
                )
            )
        return signals
