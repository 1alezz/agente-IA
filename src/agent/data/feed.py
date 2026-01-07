from __future__ import annotations

from typing import List

import pandas as pd


def klines_to_dataframe(klines: List[List[float]]) -> pd.DataFrame:
    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore",
    ]
    frame = pd.DataFrame(klines, columns=columns)
    for col in ["open", "high", "low", "close", "volume"]:
        frame[col] = frame[col].astype(float)
    return frame
