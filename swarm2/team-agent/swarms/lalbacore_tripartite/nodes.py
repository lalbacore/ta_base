import json
import hashlib
from typing import Dict, Any, Tuple
from .ledger import CryptoTape

# Minimal mock cryptography
def generate_mock_keypair(role: str) -> Tuple[str, str]:
    return f"PUB_{role}", f"PRIV_{role}"

def mock_sign(payload: dict, priv_key: str) -> str:
    payload_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(f"{payload_str}{priv_key}".encode()).hexdigest()

def mock_verify(payload: dict, signature: str, pub_key: str) -> bool:
    # Reconstruct the expected private key from the public key mapping (mock only)
    expected_priv = pub_key.replace("PUB_", "PRIV_")
    expected_sig = mock_sign(payload, expected_priv)
    return signature == expected_sig

# --- Node Implementations ---

class LedgerNode:
    def __init__(self, tape: CryptoTape, exec_pub: str, gov_pub: str):
        self.tape = tape
        self.exec_pub = exec_pub
        self.gov_pub = gov_pub

    def process_message(self, sender: str, payload: dict, signature: str) -> None:
        """Receives a message, verifies the signature, and appends to the tape."""
        pub_key = self.exec_pub if sender == "EXECUTION" else self.gov_pub
        
        if not mock_verify(payload, signature, pub_key):
            raise PermissionError(f"Ledger rejected invalid signature from {sender}")
            
        record = {
            "sender": sender,
            "payload": payload,
            "signature": signature
        }
        self.tape.append_record(record)
        print(f"[LEDGER] Appended verified message from {sender}")

class GovernanceNode:
    def __init__(self, pub_key: str, priv_key: str, ledger: LedgerNode):
        self.pub_key = pub_key
        self.priv_key = priv_key
        self.ledger = ledger

    def evaluate_proposal(self, proposal_payload: dict, env_policies: list = None) -> None:
        """Evaluates a proposal from Execution and signs an Approval if safe."""
        print(f"[GOVERNANCE] Evaluating proposed action: {proposal_payload.get('action')}")
        
        # Policy constraint
        if proposal_payload.get("params", {}).get("env") == "prod":
            decision = "DENIED"
            reason = "Direct deployment to prod violates core policy."
        else:
            decision = "APPROVED"
            reason = "Action meets safety constraints."
            
        decision_payload = {
            "type": "DECISION",
            "decision": decision,
            "reason": reason,
            "original_action": proposal_payload.get("action")
        }
        
        sig = mock_sign(decision_payload, self.priv_key)
        self.ledger.process_message("GOVERNANCE", decision_payload, sig)

class ExecutionNode:
    def __init__(self, pub_key: str, priv_key: str, ledger: LedgerNode):
        self.pub_key = pub_key
        self.priv_key = priv_key
        self.ledger = ledger

    def propose_action(self, action: str, params: dict) -> None:
        """Proposes an action to the ledger, waiting for Governance approval."""
        print(f"[EXECUTION] Proposing action: {action}")
        payload = {
            "type": "PROPOSAL",
            "action": action,
            "params": params
        }
        sig = mock_sign(payload, self.priv_key)
        self.ledger.process_message("EXECUTION", payload, sig)

    def execute_approved_action(self, action: str, gov_approval_payload: dict, gov_sig: str, gov_pub: str) -> str:
        """Executes the tool ONLY IF a valid governance signature is provided."""
        if not mock_verify(gov_approval_payload, gov_sig, gov_pub):
            raise PermissionError("[EXECUTION] Cannot execute: Governance signature is invalid!")
            
        if gov_approval_payload.get("decision") != "APPROVED" or gov_approval_payload.get("original_action") != action:
            raise PermissionError("[EXECUTION] Cannot execute: Action was not approved by Governance.")
            
        print(f"[EXECUTION] Validation passed. Executing '{action}' now.")
        
        result_payload = {
            "type": "RESULT",
            "action_executed": action,
            "status": "success",
        }
        sig = mock_sign(result_payload, self.priv_key)
        self.ledger.process_message("EXECUTION", result_payload, sig)
        
        return "ARTIFACT_GENERATED"
