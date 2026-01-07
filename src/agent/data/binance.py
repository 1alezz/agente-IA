from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from binance.client import Client


@dataclass
class BinanceOrderResult:
    order_id: str
    status: str
    raw: Dict[str, Any]


class BinanceDataClient:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True) -> None:
        self.client = Client(api_key=api_key, api_secret=api_secret, testnet=testnet)

    def ping(self) -> bool:
        self.client.ping()
        return True

    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List[Any]]:
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def create_order(self, **kwargs: Any) -> BinanceOrderResult:
        response = self.client.create_order(**kwargs)
        return BinanceOrderResult(order_id=str(response.get("orderId")), status=response.get("status"), raw=response)

    def get_account(self) -> Dict[str, Any]:
        return self.client.get_account()
