from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import ccxt

from trading_agent.api.schemas import Decision
from trading_agent.execution.broker import BrokerInterface, Order


@dataclass
class BinanceCredentials:
    api_key: str
    api_secret: str

    @classmethod
    def from_config(cls, api_key: str | None, api_secret: str | None) -> "BinanceCredentials":
        if not api_key or not api_secret:
            raise ValueError("Credenciais Binance ausentes: informe api_key e api_secret")
        return cls(api_key=api_key, api_secret=api_secret)


class BinanceBroker(BrokerInterface):
    """Broker para Binance Futures que pode operar em sandbox (testnet) ou live via ccxt."""

    def __init__(self, creds: BinanceCredentials, sandbox: bool = True) -> None:
        self.exchange = ccxt.binanceusdm(
            {
                "apiKey": creds.api_key,
                "secret": creds.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "future"},
            }
        )
        self.exchange.set_sandbox_mode(sandbox)

    async def _run(self, fn, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

    async def place_order(self, decision: Decision) -> Order:
        order_type = decision.signals.get("order_type") if isinstance(decision.signals, dict) else None
        side = decision.side.upper()
        symbol = decision.symbol or (decision.signals.get("symbol") if isinstance(decision.signals, dict) else None)
        if not symbol:
            raise ValueError("Decision precisa conter symbol para Binance")

        amount = decision.size or 0.0
        price = decision.entry
        ccxt_type = "market" if order_type == "market" or price is None else "limit"
        params: Dict[str, Any] = {}
        if decision.stop_loss:
            params["stopPrice"] = decision.stop_loss

        def _create():
            return self.exchange.create_order(
                symbol=symbol, type=ccxt_type, side=side, amount=amount, price=price, params=params
            )

        created = await self._run(_create)
        return Order(
            id=str(created.get("id")),
            symbol=symbol,
            side=decision.side,
            price=float(created.get("price") or price or 0.0),
            size=float(created.get("amount") or amount),
            status=created.get("status", "open"),
            created_at=datetime.utcnow(),
            metadata={"info": created, "narrative": decision.narrative},
        )

    async def cancel_order(self, order_id: str) -> None:
        await self._run(self.exchange.cancel_order, order_id)

    async def get_positions(self) -> List[Dict[str, Any]]:
        try:
            positions = await self._run(self.exchange.fetch_positions)
            return positions or []
        except Exception:
            return []

    async def get_balance(self) -> Dict[str, Any]:
        try:
            bal = await self._run(self.exchange.fetch_balance)
            return bal
        except Exception:
            return {}

    async def get_fills(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            trades = await self._run(self.exchange.fetch_my_trades, symbol)
            return trades or []
        except Exception:
            return []
