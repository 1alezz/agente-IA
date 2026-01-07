from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator, Callable, Dict, Set

from fastapi import WebSocket


class StreamManager:
    def __init__(self) -> None:
        self.connections: Set[WebSocket] = set()
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    async def publish(self, message: Dict[str, Any]) -> None:
        await self.queue.put(message)

    async def broadcaster(self) -> None:
        while True:
            message = await self.queue.get()
            for ws in list(self.connections):
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    self.disconnect(ws)

    async def stream(self, websocket: WebSocket) -> None:
        await self.connect(websocket)
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            self.disconnect(websocket)


stream_manager = StreamManager()
