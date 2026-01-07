from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, List


@dataclass
class LogEvent:
    timestamp: str
    level: str
    message: str
    symbol: str | None = None
    timeframe: str | None = None


class LogBuffer:
    def __init__(self, maxlen: int = 500) -> None:
        self._events: Deque[LogEvent] = deque(maxlen=maxlen)

    def add(self, event: LogEvent) -> None:
        self._events.append(event)

    def list_events(self) -> List[LogEvent]:
        return list(self._events)


class DashboardLogger:
    def __init__(self, name: str = "agent") -> None:
        self.logger = logging.getLogger(name)
        self.buffer = LogBuffer()

    def configure(self, level: str = "INFO") -> None:
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format="%(asctime)s %(levelname)s %(message)s",
        )
        self.logger.setLevel(level.upper())

    def log(self, level: str, message: str, symbol: str | None = None, timeframe: str | None = None) -> None:
        timestamp = datetime.utcnow().isoformat()
        event = LogEvent(timestamp=timestamp, level=level, message=message, symbol=symbol, timeframe=timeframe)
        self.buffer.add(event)
        log_fn = getattr(self.logger, level.lower(), self.logger.info)
        log_fn(message)
