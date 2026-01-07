from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import gymnasium as gym
import numpy as np


@dataclass
class TradingState:
    observation: np.ndarray
    equity: float
    position: int


class TradingEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, observation_size: int = 20) -> None:
        super().__init__()
        self.observation_size = observation_size
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(observation_size,), dtype=np.float32)
        self.state = TradingState(observation=np.zeros(observation_size, dtype=np.float32), equity=1.0, position=0)

    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        self.state = TradingState(observation=np.zeros(self.observation_size, dtype=np.float32), equity=1.0, position=0)
        return self.state.observation, {}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        reward = 0.0
        terminated = False
        truncated = False
        info: Dict[str, Any] = {}
        return self.state.observation, reward, terminated, truncated, info
