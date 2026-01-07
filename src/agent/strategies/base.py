from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class StrategySignal:
    name: str
    signal: str
    confidence: float
    metadata: Dict[str, float | str]


class StrategyDetector:
    name: str = "base"

    def detect(self, data: pd.DataFrame) -> list[StrategySignal]:
        raise NotImplementedError
