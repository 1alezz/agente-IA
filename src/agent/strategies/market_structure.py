from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal


class MarketStructureDetector(StrategyDetector):
    name = "market_structure"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < 6:
            return signals
        highs = data["high"].iloc[-6:]
        lows = data["low"].iloc[-6:]
        if highs.iloc[-1] > highs.iloc[-3] and lows.iloc[-1] > lows.iloc[-3]:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bullish_structure",
                    confidence=0.55,
                    metadata={"trend": "up"},
                )
            )
        if highs.iloc[-1] < highs.iloc[-3] and lows.iloc[-1] < lows.iloc[-3]:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bearish_structure",
                    confidence=0.55,
                    metadata={"trend": "down"},
                )
            )
        return signals
