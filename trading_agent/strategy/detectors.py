from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd


@dataclass
class SignalResult:
    signal: bool
    score: float
    notes: str
    plot: dict[str, Any]


@dataclass
class Candle:
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float


WINDOW_DEFAULT = 50


def _to_series(candles: Iterable[Candle]) -> pd.DataFrame:
    df = pd.DataFrame([c.__dict__ for c in candles])
    if df.empty:
        raise ValueError("No candles provided")
    return df


def detect_order_blocks(candles: Iterable[Candle], lookback: int = WINDOW_DEFAULT) -> SignalResult:
    df = _to_series(candles).tail(lookback)
    recent = df.iloc[-5:]
    bullish_blocks = recent[(recent["close"] > recent["open"]) & (recent["low"] == recent["low"].rolling(3).min())]
    bearish_blocks = recent[(recent["close"] < recent["open"]) & (recent["high"] == recent["high"].rolling(3).max())]
    signal = not bullish_blocks.empty or not bearish_blocks.empty
    score = float(min(1.0, (len(bullish_blocks) + len(bearish_blocks)) / 3))
    notes = "Bullish OB" if len(bullish_blocks) >= len(bearish_blocks) else "Bearish OB"
    plot = {
        "bullish": bullish_blocks[["low", "high", "timestamp"]].to_dict(orient="records"),
        "bearish": bearish_blocks[["low", "high", "timestamp"]].to_dict(orient="records"),
    }
    return SignalResult(signal=signal, score=score, notes=notes, plot=plot)


def detect_fvg_ifvg(candles: Iterable[Candle], lookback: int = WINDOW_DEFAULT) -> SignalResult:
    df = _to_series(candles).tail(lookback)
    gaps = []
    for i in range(2, len(df)):
        prev_high = df.iloc[i - 2]["high"]
        prev_low = df.iloc[i - 2]["low"]
        curr_low = df.iloc[i]["low"]
        curr_high = df.iloc[i]["high"]
        if curr_low > prev_high:
            gaps.append({"type": "bullish", "start": prev_high, "end": curr_low, "timestamp": df.iloc[i]["timestamp"]})
        if curr_high < prev_low:
            gaps.append({"type": "bearish", "start": curr_high, "end": prev_low, "timestamp": df.iloc[i]["timestamp"]})
    signal = len(gaps) > 0
    score = float(min(1.0, len(gaps) / 5))
    return SignalResult(signal=signal, score=score, notes="FVG/IFVG detected" if signal else "", plot={"gaps": gaps})


def detect_liquidity_zones(candles: Iterable[Candle], lookback: int = WINDOW_DEFAULT) -> SignalResult:
    df = _to_series(candles).tail(lookback)
    highs = df["high"].rolling(5).max()
    lows = df["low"].rolling(5).min()
    equal_highs = df[np.isclose(df["high"], highs.shift(1))]
    equal_lows = df[np.isclose(df["low"], lows.shift(1))]
    signal = not equal_highs.empty or not equal_lows.empty
    plot = {
        "equal_highs": equal_highs[["high", "timestamp"]].to_dict(orient="records"),
        "equal_lows": equal_lows[["low", "timestamp"]].to_dict(orient="records"),
    }
    notes = "Liquidity pools near highs" if len(equal_highs) > len(equal_lows) else "Liquidity pools near lows"
    score = float(min(1.0, (len(equal_highs) + len(equal_lows)) / 5))
    return SignalResult(signal=signal, score=score, notes=notes, plot=plot)


def detect_rsi_divergence(candles: Iterable[Candle], period: int = 14) -> SignalResult:
    df = _to_series(candles)
    close = df["close"].astype(float)
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    price_highs = df["high"].rolling(5).max()
    price_lows = df["low"].rolling(5).min()
    bearish_div = price_highs.diff() > 0
    bullish_div = price_lows.diff() < 0
    rsi_bear = rsi.diff() < 0
    rsi_bull = rsi.diff() > 0
    signal = bool((bearish_div & rsi_bear).iloc[-1] or (bullish_div & rsi_bull).iloc[-1])
    notes = "RSI divergence" if signal else ""
    plot = {"rsi": rsi.tail(period * 2).tolist()}
    score = float(rsi.iloc[-1] / 100)
    return SignalResult(signal=signal, score=score, notes=notes, plot=plot)


def detect_structure_bos_choch(candles: Iterable[Candle], lookback: int = WINDOW_DEFAULT) -> SignalResult:
    df = _to_series(candles).tail(lookback)
    highs = df["high"]
    lows = df["low"]
    higher_highs = highs.diff() > 0
    higher_lows = lows.diff() > 0
    bos = bool(higher_highs.iloc[-1] and higher_lows.iloc[-1])
    choch = bool((not higher_highs.iloc[-1]) and higher_lows.iloc[-1])
    notes = "BOS" if bos else "CHOCH" if choch else "Range"
    score = 0.7 if bos else 0.5 if choch else 0.2
    plot = {
        "swing_highs": highs.tail(10).tolist(),
        "swing_lows": lows.tail(10).tolist(),
    }
    return SignalResult(signal=bos or choch, score=score, notes=notes, plot=plot)


def detect_turtle_soup(candles: Iterable[Candle]) -> SignalResult:
    df = _to_series(candles)
    recent_low = df["low"].iloc[-2]
    current_low = df["low"].iloc[-1]
    recent_high = df["high"].iloc[-2]
    current_high = df["high"].iloc[-1]
    long_signal = current_low < recent_low and df["close"].iloc[-1] > df["open"].iloc[-1]
    short_signal = current_high > recent_high and df["close"].iloc[-1] < df["open"].iloc[-1]
    signal = bool(long_signal or short_signal)
    notes = "Turtle Soup long" if long_signal else "Turtle Soup short" if short_signal else ""
    score = 0.6 if signal else 0.0
    plot = {
        "break_level": recent_low if long_signal else recent_high if short_signal else None,
        "direction": "long" if long_signal else "short" if short_signal else None,
    }
    return SignalResult(signal=signal, score=score, notes=notes, plot=plot)


def detect_trendline_break(candles: Iterable[Candle], lookback: int = WINDOW_DEFAULT) -> SignalResult:
    df = _to_series(candles).tail(lookback)
    highs = df["high"]
    lows = df["low"]
    x = np.arange(len(df))
    coef_high = np.polyfit(x, highs, 1)
    coef_low = np.polyfit(x, lows, 1)
    trend_high = coef_high[0] * x + coef_high[1]
    trend_low = coef_low[0] * x + coef_low[1]
    last_close = df["close"].iloc[-1]
    broke_down = last_close < trend_low[-1]
    broke_up = last_close > trend_high[-1]
    signal = bool(broke_down or broke_up)
    notes = "Trendline break up" if broke_up else "Trendline break down" if broke_down else ""
    score = 0.5 if signal else 0.0
    plot = {"trend_high": trend_high.tolist(), "trend_low": trend_low.tolist()}
    return SignalResult(signal=signal, score=score, notes=notes, plot=plot)


def compute_fibonacci_targets(candles: Iterable[Candle]) -> SignalResult:
    df = _to_series(candles).tail(20)
    swing_high = df["high"].max()
    swing_low = df["low"].min()
    levels = {
        "0.382": swing_high - (swing_high - swing_low) * 0.382,
        "0.5": (swing_high + swing_low) / 2,
        "0.618": swing_high - (swing_high - swing_low) * 0.618,
        "1.618": swing_high + (swing_high - swing_low) * 0.618,
    }
    return SignalResult(signal=True, score=0.3, notes="Fib levels", plot={"levels": levels})


def moving_average_confirmation(candles: Iterable[Candle], period: int = 20) -> SignalResult:
    df = _to_series(candles)
    close = df["close"].astype(float)
    ma = close.rolling(period).mean()
    if len(ma) < period:
        return SignalResult(signal=False, score=0.0, notes="Not enough data", plot={})
    direction_up = close.iloc[-1] > ma.iloc[-1]
    signal = bool(direction_up or close.iloc[-1] < ma.iloc[-1])
    score = 0.4
    notes = "MA bullish" if direction_up else "MA bearish"
    plot = {"ma": ma.tail(10).tolist()}
    return SignalResult(signal=signal, score=score, notes=notes, plot=plot)
