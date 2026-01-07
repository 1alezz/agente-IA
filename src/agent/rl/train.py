from __future__ import annotations

from stable_baselines3 import PPO

from .env import TradingEnv


def train_ppo(total_timesteps: int = 10_000) -> PPO:
    env = TradingEnv()
    model = PPO("MlpPolicy", env, verbose=0)
    model.learn(total_timesteps=total_timesteps)
    return model
