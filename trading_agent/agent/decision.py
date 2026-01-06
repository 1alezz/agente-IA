from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from trading_agent.api.schemas import Decision, SignalMetadata
from trading_agent.strategy import detectors


@dataclass
class DecisionContext:
    symbol: str
    timeframe: str
    candles: Iterable[detectors.Candle]
    risk_config: dict
    strategy_params: dict


class RuleBasedDecisionEngine:
    def __init__(self, setups: list[str] | None = None) -> None:
        self.setups = setups or ["ob_fvg_liquidity", "turtle_rsi_structure"]

    def evaluate(self, context: DecisionContext) -> Decision:
        candles_df = pd.DataFrame([c.__dict__ for c in context.candles])
        if candles_df.empty:
            return Decision(action="wait", narrative="Sem dados suficientes")

        signals: dict[str, detectors.SignalResult] = {
            "order_block": detectors.detect_order_blocks(context.candles),
            "fvg": detectors.detect_fvg_ifvg(context.candles),
            "liquidity": detectors.detect_liquidity_zones(context.candles),
            "rsi_div": detectors.detect_rsi_divergence(context.candles),
            "structure": detectors.detect_structure_bos_choch(context.candles),
            "turtle": detectors.detect_turtle_soup(context.candles),
            "trendline": detectors.detect_trendline_break(context.candles),
            "fib": detectors.compute_fibonacci_targets(context.candles),
        }

        confluence_score = float(np.mean([s.score for s in signals.values()]))
        bullish_bias = signals["structure"].notes == "BOS" and signals["order_block"].notes.startswith("Bullish")
        bearish_bias = signals["structure"].notes != "BOS" and signals["order_block"].notes.startswith("Bearish")

        narrative = [
            f"Confluência média {confluence_score:.2f}",
            f"OB: {signals['order_block'].notes}",
            f"FVG: {len(signals['fvg'].plot.get('gaps', []))} gaps",
            f"Liquidez: {signals['liquidity'].notes}",
            f"RSI: {signals['rsi_div'].notes}",
            f"Estrutura: {signals['structure'].notes}",
            f"TurtleSoup: {signals['turtle'].notes}",
            f"Trendline: {signals['trendline'].notes}",
        ]

        action = "enter" if confluence_score > 0.35 else "wait"
        side = "long" if bullish_bias else "short" if bearish_bias else "flat"
        last_close = float(candles_df.iloc[-1]["close"])
        atr = float(candles_df["high"].rolling(14).max().iloc[-1] - candles_df["low"].rolling(14).min().iloc[-1])
        stop_loss = last_close - atr * 0.5 if side == "long" else last_close + atr * 0.5
        take_profit = last_close + atr if side == "long" else last_close - atr

        signal_metadata = {
            name: SignalMetadata(signal=s.signal, score=s.score, notes=s.notes, plot=s.plot)
            for name, s in signals.items()
        }

        return Decision(
            action=action,
            side=side,
            symbol=context.symbol,
            timeframe=context.timeframe,
            entry=last_close,
            stop_loss=stop_loss,
            take_profits=[take_profit],
            size=context.risk_config.get("risk_per_trade", 1.0),
            narrative=" | ".join(narrative),
            confluence=confluence_score,
            signals=signal_metadata,
        )
