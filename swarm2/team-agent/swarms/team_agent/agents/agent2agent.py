from __future__ import annotations
from typing import Any, Dict, Optional
from .bus import InMemoryBus

class Agent:
    def __init__(self, name: str, bus: InMemoryBus):
        self.name = name
        self.bus = bus

    def on_message(self, message: Dict[str, Any]) -> None:
        # override in subclasses
        pass

    def send(self, topic: str, payload: Dict[str, Any], correlation_id: Optional[str] = None) -> None:
        msg = {
            "from": self.name,
            "payload": payload,
            "correlation_id": correlation_id,
        }
        self.bus.publish(topic, msg)

    def listen(self, topic: str) -> None:
        self.bus.subscribe(topic, self.on_message)