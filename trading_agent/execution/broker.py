from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from trading_agent.api.schemas import Decision


@dataclass
class Order:
    id: str
    symbol: str
    side: str
    price: float
    size: float
    status: str
    created_at: datetime
    metadata: Dict[str, Any]


class BrokerInterface(ABC):
    @abstractmethod
    async def place_order(self, decision: Decision) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_fills(self, symbol: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class PaperBroker(BrokerInterface):
    def __init__(self) -> None:
        self.orders: Dict[str, Order] = {}
        self.balance = {"equity": 100000.0, "available": 100000.0}
        self.positions: Dict[str, Dict[str, Any]] = {}

    async def place_order(self, decision: Decision) -> Order:
        order_id = f"paper-{len(self.orders) + 1}"
        order = Order(
            id=order_id,
            symbol=decision.signals.get("symbol", "unknown") if isinstance(decision.signals, dict) else "unknown",
            side=decision.side,
            price=decision.entry or 0.0,
            size=decision.size or 0.0,
            status="filled",
            created_at=datetime.utcnow(),
            metadata={"narrative": decision.narrative},
        )
        self.orders[order_id] = order
        self.positions[order.symbol] = {
            "symbol": order.symbol,
            "side": order.side,
            "entry": order.price,
            "size": order.size,
            "stop_loss": decision.stop_loss,
            "take_profit": decision.take_profits,
        }
        self.balance["available"] -= order.price * order.size * 0.01
        return order

    async def cancel_order(self, order_id: str) -> None:
        if order_id in self.orders:
            self.orders[order_id].status = "canceled"

    async def get_positions(self) -> List[Dict[str, Any]]:
        return list(self.positions.values())

    async def get_balance(self) -> Dict[str, Any]:
        return self.balance

    async def get_fills(self, symbol: str) -> List[Dict[str, Any]]:
        return [o.__dict__ for o in self.orders.values() if o.symbol == symbol]
