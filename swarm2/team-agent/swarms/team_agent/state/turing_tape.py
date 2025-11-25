from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

class TuringTape:
    """
    Append-only JSONL tape for agent/workflow state.
    File layout: .team_agent/tape/{workflow_id}.jsonl
    Each line: {"ts": ISO8601, "agent": str, "workflow_id": str, "state": {...}, "event": str}
    """

    def __init__(self, base_dir: Optional[Path] = None, workflow_id: str = "default"):
        self.workflow_id = workflow_id or "default"
        self.base_dir = base_dir or Path(".team_agent") / "tape"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.base_dir / f"{self.workflow_id}.jsonl"
        self.path.touch(exist_ok=True)

    def append(self, agent: str, event: str, state: Dict[str, Any]) -> None:
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "agent": agent,
            "workflow_id": self.workflow_id,
            "event": event,
            "state": state,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read_all(self) -> Iterable[Dict[str, Any]]:
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue

    def last_state(self, agent: Optional[str] = None) -> Optional[Dict[str, Any]]:
        last = None
        for rec in self.read_all():
            if agent and rec.get("agent") != agent:
                continue
            last = rec
        return last