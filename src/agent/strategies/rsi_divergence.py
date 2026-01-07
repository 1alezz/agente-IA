from __future__ import annotations

import pandas as pd

from .base import StrategyDetector, StrategySignal
from .indicators import rsi


class RSIDivergenceDetector(StrategyDetector):
    name = "rsi_divergence"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        signals: list[StrategySignal] = []
        if len(data) < 20:
            return signals
        prices = data["close"]
        rsi_series = rsi(prices)
        if rsi_series.isna().all():
            return signals
        last_price = prices.iloc[-1]
        prev_price = prices.iloc[-5]
        last_rsi = rsi_series.iloc[-1]
        prev_rsi = rsi_series.iloc[-5]
        if last_price < prev_price and last_rsi > prev_rsi:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bullish_divergence",
                    confidence=0.57,
                    metadata={"rsi": float(last_rsi)},
                )
            )
        if last_price > prev_price and last_rsi < prev_rsi:
            signals.append(
                StrategySignal(
                    name=self.name,
                    signal="bearish_divergence",
                    confidence=0.57,
                    metadata={"rsi": float(last_rsi)},
                )
            )
        return signals
