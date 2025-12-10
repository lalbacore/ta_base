# Swarm Architecture: The Crypto-Mesh

**Version 1.2.0**

This document details the transition from a linear orchestration pipeline to a decentralized **Crypto-Mesh** architecture. The core innovation is the shift from direct method calls to cryptographically signed, message-based communication between independent nodes.

---

## 1. Core Concepts

### 1.1 SwarmNode
The fundamental building block of the new architecture. Every agent (Orchestrator, Architect, Specialist) is a `SwarmNode`.

**Capabilities:**
- **Identity:** Unique ID (`agent_{uuid}`) and Type (e.g., `architect`, `specialist`).
- **PKI Integration:** Built-in `Signer` and `Verifier` initialized from the standard 3-tier CA hierarchy.
- **Message Handling:** Standard `handle_message(message: AgentMessage)` interface.
- **Trust Domain:** Each node belongs to a domain (GOVERNMENT, EXECUTION, LOGGING) which dictates its certificate constraints.

### 1.2 AgentMessage
The universal protocol for inter-agent communication.

```python
@dataclass
class AgentMessage:
    msg_id: str             # Unique UUID
    sender_id: str          # Sender's Agent ID
    recipient_id: str       # Target Agent ID (or "broadcast")
    message_type: str       # "task_request", "review_request", "log_request", "response"
    payload: Dict[str, Any] # The actual data (mission, code, review)
    timestamp: float        # Unix timestamp
    signature: str          # Cryptographic signature of the payload
```

**Security:**
- Payloads are signed by the sender's private key.
- Recipients verify the signature against the sender's public key (retrieved from the CA/PKI manager) before processing.

---

## 2. Dynamic Orchestration (Hub-and-Spoke)

Instead of the Orchestrator manually instantiating and calling agents in a fixed order, it now acts as a **MsgBus Node**.

### 2.1 MessageDispatcher
An in-memory (currently) routing bus that:
1.  **Registers Nodes:** Agents register themselves with the dispatcher on startup.
2.  **Routes Messages:** Delivers `AgentMessage` objects to the correct recipient.
3.  **Discovery:** Allows finding nodes by role or capability (e.g., "Find me a Critic").

### 2.2 The Execution Flow

1.  **Submission:** User submits a mission to `Orchestrator`.
2.  **Dispatch:** Orchestrator wraps the mission in a `task_request` message and sends it to `Architect`.
3.  **Architect Execution:**
    - Verifies message signature (from Orchestrator).
    - Designs architecture.
    - Sends `response` message back to Orchestrator.
4.  **Builder Dispatch:** Orchestrator sends the architecture to `Builder`.
    - Builder may request `Specialist` agents via dynamic discovery.
5.  **Critique & Log:** Similar signed message exchanges occur for `Critic` and `Recorder`.

---

## 3. Specialist Integration

Specialists (AWS, Legal, etc.) are now first-class `SwarmNodes`.

- They inherit `SwarmNode`.
- They register with the `AgentManager`.
- They can be addressed directly via messages if their ID is known, or discovered via the Registry.

---

## 4. Security Model

The Crypto-Mesh ensures that **no action occurs without attribution**.

- **Non-Repudiation:** Every instruction and every result is signed. The `Recorder` logs these signed messages to the `TuringTape`.
- **Authorization:** Agents checks the `TrustDomain` of the sender. For example, a `Governance` agent might only accept policy updates from the `GOVERNMENT` domain.

---

## 5. Future Roadmap: Networked Mesh

Currently, `MessageDispatcher` is in-memory. The next phase involves:
- **P2P Transport:** Replacing the variable-passing dispatcher with HTTP/gRPC or a queue (Redis/RabbitMQ).
- **Remote Nodes:** Agents running on different servers/containers communicating over the network using the same `AgentMessage` protocol.
