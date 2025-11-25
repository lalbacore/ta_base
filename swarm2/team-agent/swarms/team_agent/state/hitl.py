from __future__ import annotations
from typing import Any, Optional
from .turing_tape import TuringTape

class HumanApprovalGate:
    """
    Simple human-in-the-loop gate using TuringTape.
    - request/check approvals per checkpoint_id
    - approval is recorded as an 'approved' event on the tape
    """

    def __init__(self, tape: TuringTape):
        self.tape = tape

    def is_approved(self, checkpoint_id: str) -> bool:
        # Scan from end; first relevant event decides
        last = None
        for rec in self.tape.read_all():
            if rec.get("event") in ("approval_requested", "approved", "rejected"):
                st = rec.get("state", {})
                if st.get("checkpoint_id") == checkpoint_id:
                    last = rec
        return bool(last and last.get("event") == "approved")

    def request_if_needed(self, checkpoint_id: str, context: Optional[dict] = None) -> bool:
        """
        Returns True if already approved; otherwise logs request and returns False.
        """
        if self.is_approved(checkpoint_id):
            return True
        # Log that we need approval (idempotent enough; can be requested multiple times)
        self.tape.append(agent="hitl", event="approval_requested", state={
            "checkpoint_id": checkpoint_id,
            "context": context or {}
        })
        return False

    def approve(self, checkpoint_id: str, approver: str = "human") -> None:
        self.tape.append(agent=approver, event="approved", state={"checkpoint_id": checkpoint_id})

    def reject(self, checkpoint_id: str, approver: str = "human", reason: str = "") -> None:
        self.tape.append(agent=approver, event="rejected", state={"checkpoint_id": checkpoint_id, "reason": reason})