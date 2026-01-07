from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from trading_agent.api.schemas import Decision
from .broker import BrokerInterface


@dataclass
class PositionManager:
    broker: BrokerInterface

    async def execute_decision(self, decision: Decision) -> Dict:
        if decision.action != "enter" or decision.side == "flat":
            return {"status": "skipped", "reason": "No entry"}
        order = await self.broker.place_order(decision)
        return {"status": "filled", "order_id": order.id, "narrative": decision.narrative}
