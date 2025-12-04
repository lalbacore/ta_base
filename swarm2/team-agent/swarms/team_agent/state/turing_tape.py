from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer, Verifier
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None
    Verifier = None


class TuringTape:
    """
    Append-only JSONL tape for agent/workflow state with cryptographic signing.
    File layout: .team_agent/tape/{workflow_id}.jsonl
    Each line: {"ts": ISO8601, "agent": str, "workflow_id": str, "state": {...}, "event": str, "_signature": {...}}
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        workflow_id: str = "default",
        signer: Optional[Signer] = None
    ):
        self.workflow_id = workflow_id or "default"
        self.base_dir = base_dir or Path(".team_agent") / "tape"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.base_dir / f"{self.workflow_id}.jsonl"
        self.path.touch(exist_ok=True)
        self.signer = signer

    def append(self, agent: str, event: str, state: Dict[str, Any]) -> None:
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "agent": agent,
            "workflow_id": self.workflow_id,
            "event": event,
            "state": state,
        }

        # Sign the record if signer is available
        if self.signer and CRYPTO_AVAILABLE:
            record = self.signer.sign_dict(record)

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

    def verify_entry(self, entry: Dict[str, Any], verifier: Verifier) -> bool:
        """
        Verify cryptographic signature of an entry.

        Args:
            entry: Entry dict with _signature metadata
            verifier: Verifier instance with certificate chain

        Returns:
            True if signature is valid, False otherwise
        """
        if not CRYPTO_AVAILABLE:
            return False

        if "_signature" not in entry:
            return False

        return verifier.verify_dict(entry)

    def verify_all(self, verifier: Verifier) -> Dict[str, Any]:
        """
        Verify all entries in the tape.

        Args:
            verifier: Verifier instance with certificate chain

        Returns:
            Dict with verification statistics
        """
        if not CRYPTO_AVAILABLE:
            return {"error": "Crypto not available"}

        total = 0
        verified = 0
        failed = 0
        unsigned = 0

        for entry in self.read_all():
            total += 1
            if "_signature" not in entry:
                unsigned += 1
            elif self.verify_entry(entry, verifier):
                verified += 1
            else:
                failed += 1

        return {
            "total": total,
            "verified": verified,
            "failed": failed,
            "unsigned": unsigned,
        }