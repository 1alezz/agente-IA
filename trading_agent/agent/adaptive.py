from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable

import numpy as np

from trading_agent.api.schemas import Decision
from trading_agent.strategy.detectors import Candle
from .decision import DecisionContext, RuleBasedDecisionEngine


@dataclass
class BanditArm:
    name: str
    alpha: float = 1.0
    beta: float = 1.0

    def sample(self) -> float:
        return np.random.beta(self.alpha, self.beta)

    def update(self, reward: float) -> None:
        self.alpha += reward
        self.beta += 1 - reward


@dataclass
class AdaptivePolicy:
    storage_dir: Path = Path("storage/models")
    arms: Dict[str, Dict[str, Dict[str, BanditArm]]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(dict)))
    rule_engine: RuleBasedDecisionEngine = field(default_factory=RuleBasedDecisionEngine)

    def __post_init__(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self, symbol: str, timeframe: str) -> None:
        path = self.storage_dir / f"bandit_{symbol}_{timeframe}.json"
        if path.exists():
            data = json.loads(path.read_text())
            arms = {
                name: BanditArm(name=name, alpha=values["alpha"], beta=values["beta"])
                for name, values in data.items()
            }
            self.arms[symbol][timeframe].update(arms)
        else:
            for setup in ["ob_fvg_liquidity", "turtle_rsi_structure"]:
                self.arms[symbol][timeframe][setup] = BanditArm(name=setup)

    def _save_state(self, symbol: str, timeframe: str) -> None:
        path = self.storage_dir / f"bandit_{symbol}_{timeframe}.json"
        payload = {
            name: {"alpha": arm.alpha, "beta": arm.beta}
            for name, arm in self.arms[symbol][timeframe].items()
        }
        path.write_text(json.dumps(payload, indent=2))

    def select_setup(self, symbol: str, timeframe: str) -> str:
        self._load_state(symbol, timeframe)
        arms = self.arms[symbol][timeframe]
        sampled = {name: arm.sample() for name, arm in arms.items()}
        return max(sampled, key=sampled.get)

    def update_reward(self, symbol: str, timeframe: str, setup: str, reward: float) -> None:
        self._load_state(symbol, timeframe)
        self.arms[symbol][timeframe][setup].update(reward)
        self._save_state(symbol, timeframe)

    def decide(self, context: DecisionContext) -> Decision:
        setup = self.select_setup(context.symbol, context.timeframe)
        decision = self.rule_engine.evaluate(context)
        decision.narrative += f" | Setup escolhido: {setup}"
        return decision
