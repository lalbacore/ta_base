from __future__ import annotations
from typing import Callable, Dict, List, Any
from collections import defaultdict
import uuid

class InMemoryBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> str:
        token = str(uuid.uuid4())
        # wrap to allow unsubscribe by token if you extend
        self._subs[topic].append(handler)
        return token

    def publish(self, topic: str, message: Dict[str, Any]) -> None:
        for handler in list(self._subs.get(topic, [])):
            try:
                handler(message)
            except Exception:
                continue