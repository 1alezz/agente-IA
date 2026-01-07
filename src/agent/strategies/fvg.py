from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal


class FVGDetector(StrategyDetector):
    name = "fvg"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < 3:
            return signals
        c1, c2, c3 = data.iloc[-3], data.iloc[-2], data.iloc[-1]
        if c1["high"] < c3["low"]:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bullish_fvg",
                    confidence=0.6,
                    metadata={"gap_low": float(c1["high"]), "gap_high": float(c3["low"])},
                )
            )
        if c1["low"] > c3["high"]:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bearish_fvg",
                    confidence=0.6,
                    metadata={"gap_high": float(c1["low"]), "gap_low": float(c3["high"])},
                )
            )
        return signals
