# A2A Protocol API

API reference for Agent-to-Agent communication protocol.

---

## Overview

The A2A Protocol provides secure, PKI-based messaging between agents.

**Module**: `swarms.team_agent.a2a.protocol`

---

## A2AClient

Client for sending requests to other agents.

```python
from swarms.team_agent.a2a import A2AClient

client = A2AClient(
    agent_id: str,
    signer: Signer,
    verifier: Verifier,
    trust_tracker: Optional[AgentReputationTracker] = None,
    registry: Optional[CapabilityRegistry] = None
)
```

### send_request()

Send a request to another agent.

```python
request = await client.send_request(
    target_id: str,
    operation: str,
    parameters: Dict[str, Any],
    capability_id: Optional[str] = None,
    timeout: float = 300.0
) -> A2ARequest
```

### invoke_capability()

Invoke a registered capability.

```python
result = await client.invoke_capability(
    capability_id: str,
    parameters: Dict[str, Any],
    timeout: float = 300.0
) -> Any
```

---

## A2AServer

Server for handling incoming agent requests.

```python
from swarms.team_agent.a2a import A2AServer

server = A2AServer(
    agent_id: str,
    signer: Signer,
    verifier: Verifier,
    trust_tracker: Optional[AgentReputationTracker] = None,
    registry: Optional[CapabilityRegistry] = None,
    min_trust_score: float = 50.0
)
```

### register_handler()

Register operation handler.

```python
async def my_handler(params: Dict[str, Any]) -> Any:
    # Process request
    return result

server.register_handler("operation_name", my_handler)
```

### handle_message()

Process incoming message.

```python
response = await server.handle_message(
    message: A2AMessage
) -> Optional[A2AMessage]
```

---

## Message Types

```python
class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    CAPABILITY_INVOKE = "capability_invoke"
    CAPABILITY_RESPONSE = "capability_response"
    HANDSHAKE = "handshake"
    HEARTBEAT = "heartbeat"
```

---

## Complete Reference

For complete implementation details, see:
- Source: `swarms/team_agent/a2a/protocol.py`
- Tests: `utils/tests/test_a2a_system.py`
- Examples: [A2A Examples](../getting-started/examples.md#a2a-examples)
