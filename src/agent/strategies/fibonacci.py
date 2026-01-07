from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal


class FibonacciTargetDetector(StrategyDetector):
    name = "fibonacci_targets"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < 20:
            return signals
        recent = data.iloc[-20:]
        swing_high = recent["high"].max()
        swing_low = recent["low"].min()
        diff = swing_high - swing_low
        if diff == 0:
            return signals
        level_618 = swing_high - diff * 0.618
        signals.append(
            StrategySignal(
                name=self.name,
                signal="fib_levels",
                confidence=0.5,
                metadata={"level_618": float(level_618)},
            )
        )
        return signals
