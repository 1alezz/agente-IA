import pandas as pd

from trading_agent.strategy import detectors


def sample_candles(n: int = 60):
    candles = []
    for i in range(n):
        candles.append(
            detectors.Candle(
                timestamp=pd.Timestamp.utcnow() + pd.Timedelta(minutes=i),
                open=100 + i * 0.1,
                high=100 + i * 0.1 + 1,
                low=100 + i * 0.1 - 1,
                close=100 + i * 0.1 + 0.5,
                volume=10_000,
            )
        )
    return candles


def test_order_block_signal():
    result = detectors.detect_order_blocks(sample_candles())
    assert isinstance(result.signal, bool)


def test_fvg_signal():
    result = detectors.detect_fvg_ifvg(sample_candles())
    assert result.score >= 0


def test_rsi_divergence_signal():
    result = detectors.detect_rsi_divergence(sample_candles())
    assert 0 <= result.score <= 1
