from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal


class OrderBlockDetector(StrategyDetector):
    name = "order_blocks"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < 5:
            return signals
        last = data.iloc[-1]
        prev = data.iloc[-2]
        if prev["high"] < last["close"] and last["close"] > last["open"]:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bullish_order_block",
                    confidence=0.55,
                    metadata={"level": float(prev["high"])},
                )
            )
        if prev["low"] > last["close"] and last["close"] < last["open"]:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bearish_order_block",
                    confidence=0.55,
                    metadata={"level": float(prev["low"])},
                )
            )
        return signals
