from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Iterable, List

from trading_agent.agent.decision import DecisionContext, RuleBasedDecisionEngine
from trading_agent.strategy.detectors import Candle


@dataclass
class BacktestResult:
    trades: List[float]
    equity_curve: List[float]
    sharpe: float


class Backtester:
    def __init__(self, engine: RuleBasedDecisionEngine | None = None) -> None:
        self.engine = engine or RuleBasedDecisionEngine()

    def run(self, symbol: str, timeframe: str, candles: Iterable[Candle]) -> BacktestResult:
        candles_list = list(candles)
        equity = [100000.0]
        trades: List[float] = []
        for i in range(50, len(candles_list)):
            window = candles_list[: i + 1]
            context = DecisionContext(symbol=symbol, timeframe=timeframe, candles=window, risk_config={}, strategy_params={})
            decision = self.engine.evaluate(context)
            if decision.action == "enter" and decision.side != "flat":
                pnl = (decision.take_profits[0] - decision.entry) if decision.side == "long" else (decision.entry - decision.take_profits[0])
                trades.append(pnl)
                equity.append(equity[-1] + pnl)
            else:
                equity.append(equity[-1])
        returns = []
        for i in range(1, len(equity)):
            if equity[i - 1] != 0:
                returns.append((equity[i] - equity[i - 1]) / equity[i - 1])
        if returns and pstdev(returns) != 0:
            sharpe = (mean(returns) / pstdev(returns)) * (252 ** 0.5)
        else:
            sharpe = 0.0
        return BacktestResult(trades=trades, equity_curve=equity, sharpe=float(sharpe))
