import json
from typing import List, Dict, Any

class CryptoTape:
    """
    The 'Turing Tape'. A strict append-only data structure used by the Ledger 
    to record all state changes and signed message passing.
    """
    def __init__(self):
        self._tape: List[Dict[str, Any]] = []

    def append_record(self, record: Dict[str, Any]):
        """
        Appends a verified record to the tape.
        In a production system, this would write to an immutable distributed ledger.
        """
        self._tape.append(record)

    def read_all(self) -> List[Dict[str, Any]]:
        """Returns the full historical sequence of events."""
        return list(self._tape)

    def export_manifest(self) -> str:
        """Exports the entire tape as a cryptographic manifest string."""
        return json.dumps(self._tape, indent=2)
