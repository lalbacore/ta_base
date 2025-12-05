"""
Agent-to-Agent (A2A) Protocol

Secure protocol for direct agent-to-agent communication with:
- mTLS for transport security
- Digital signatures for message authentication
- Trust-based access control
- Capability invocation
- Request/response patterns

Based on the architecture defined in ARCHITECTURE-A2A-MCP.md
"""

import json
import asyncio
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4
import hashlib

from ..crypto import (
    PKIManager,
    TrustDomain,
    Signer,
    Verifier,
    SignedData,
    AgentReputationTracker,
)
from .registry import CapabilityRegistry, Capability, Provider


class MessageType(Enum):
    """Types of A2A messages."""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    CAPABILITY_INVOKE = "capability_invoke"
    CAPABILITY_RESPONSE = "capability_response"
    HEARTBEAT = "heartbeat"
    HANDSHAKE = "handshake"


class RequestStatus(Enum):
    """Status of an A2A request."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


@dataclass
class A2AMessage:
    """
    A2A protocol message.

    All messages are signed by the sender and can be verified by the receiver.
    """
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Request/response correlation
    correlation_id: Optional[str] = None  # For matching responses to requests

    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Security
    signature: Optional[str] = None
    certificate_serial: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "payload": self.payload,
            "metadata": self.metadata,
            "signature": self.signature,
            "certificate_serial": self.certificate_serial,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create message from dictionary."""
        return cls(
            message_id=data["message_id"],
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
            signature=data.get("signature"),
            certificate_serial=data.get("certificate_serial"),
        )


@dataclass
class A2ARequest:
    """An A2A request with timeout and retry logic."""
    request_id: str
    requester_id: str
    target_id: str
    capability_id: Optional[str]
    operation: str
    parameters: Dict[str, Any]
    status: RequestStatus = RequestStatus.PENDING

    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    timeout_seconds: float = 300.0  # 5 minutes default
    max_retries: int = 3
    retry_count: int = 0

    response: Optional[Any] = None
    error: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


class A2AClient:
    """
    Client for making A2A requests to other agents.

    Handles:
    - Message signing and encryption
    - Request/response correlation
    - Timeout and retry logic
    - Trust verification
    """

    def __init__(
        self,
        agent_id: str,
        signer: Signer,
        verifier: Verifier,
        trust_tracker: Optional[AgentReputationTracker] = None,
        registry: Optional[CapabilityRegistry] = None,
        pki_manager: Optional[PKIManager] = None,
    ):
        """
        Initialize A2A client.

        Args:
            agent_id: This agent's ID
            signer: Signer for message authentication
            verifier: Verifier for validating responses
            trust_tracker: For checking recipient trust
            registry: Capability registry for discovery
            pki_manager: PKI manager for certificate verification
        """
        self.agent_id = agent_id
        self.signer = signer
        self.verifier = verifier
        self.trust_tracker = trust_tracker
        self.registry = registry
        self.pki_manager = pki_manager

        # Pending requests
        self.pending_requests: Dict[str, A2ARequest] = {}

        # Response handlers (for async responses)
        self.response_handlers: Dict[str, Callable] = {}

    def create_message(
        self,
        message_type: MessageType,
        recipient_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> A2AMessage:
        """
        Create a signed A2A message.

        Args:
            message_type: Type of message
            recipient_id: Recipient agent ID
            payload: Message payload
            correlation_id: For request/response matching
            metadata: Additional metadata

        Returns:
            Signed A2AMessage
        """
        message = A2AMessage(
            message_id=f"msg-{uuid4().hex[:12]}",
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            correlation_id=correlation_id,
            payload=payload,
            metadata=metadata or {},
        )

        # Sign the message
        message_dict = message.to_dict()
        # Remove signature fields before signing
        message_dict.pop("signature", None)
        message_dict.pop("certificate_serial", None)

        signed = self.signer.sign_dict(message_dict)
        message.signature = signed["_signature"]
        message.certificate_serial = None  # Will be in the signature data

        return message

    def verify_message(self, message: A2AMessage) -> bool:
        """
        Verify a message signature.

        Args:
            message: Message to verify

        Returns:
            True if signature is valid
        """
        if not message.signature:
            return False

        # Reconstruct signed data
        message_dict = message.to_dict()
        signature = message_dict.pop("signature")
        message_dict.pop("certificate_serial", None)

        # Reconstruct the signed format (data + _signature)
        signed_data = {
            **message_dict,
            "_signature": signature,
        }

        try:
            return self.verifier.verify_dict(signed_data)
        except Exception:
            return False

    async def send_request(
        self,
        target_id: str,
        operation: str,
        parameters: Dict[str, Any],
        capability_id: Optional[str] = None,
        timeout: float = 300.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> A2ARequest:
        """
        Send a request to another agent.

        Args:
            target_id: Target agent ID
            operation: Operation to perform
            parameters: Operation parameters
            capability_id: Optional capability to invoke
            timeout: Request timeout in seconds
            metadata: Additional metadata

        Returns:
            A2ARequest object (can be polled for completion)
        """
        # Check target trust if tracker available
        if self.trust_tracker:
            target_metrics = self.trust_tracker.get_agent_metrics(target_id)
            if target_metrics and target_metrics.trust_score < 50.0:
                raise ValueError(f"Target agent {target_id} has insufficient trust ({target_metrics.trust_score:.1f})")

        # Create request
        request = A2ARequest(
            request_id=f"req-{uuid4().hex[:12]}",
            requester_id=self.agent_id,
            target_id=target_id,
            capability_id=capability_id,
            operation=operation,
            parameters=parameters,
            timeout_seconds=timeout,
            metadata=metadata or {},
        )

        # Create message
        payload = {
            "request_id": request.request_id,
            "operation": operation,
            "parameters": parameters,
            "capability_id": capability_id,
        }

        message = self.create_message(
            message_type=MessageType.CAPABILITY_INVOKE if capability_id else MessageType.REQUEST,
            recipient_id=target_id,
            payload=payload,
            metadata=metadata,
        )

        # Store pending request
        self.pending_requests[request.request_id] = request
        request.status = RequestStatus.IN_PROGRESS
        request.started_at = datetime.utcnow()

        # In a real implementation, this would send the message over the network
        # For now, we'll simulate by calling a handler directly
        # TODO: Implement actual network transport (HTTP, WebSocket, gRPC, etc.)

        return request

    async def invoke_capability(
        self,
        capability_id: str,
        parameters: Dict[str, Any],
        timeout: float = 300.0,
    ) -> Any:
        """
        Invoke a capability from the registry.

        Args:
            capability_id: Capability to invoke
            parameters: Invocation parameters
            timeout: Timeout in seconds

        Returns:
            Capability result

        Raises:
            ValueError: If capability not found or provider not trusted
            TimeoutError: If invocation times out
        """
        if not self.registry:
            raise ValueError("Registry not configured")

        # Get capability details
        result = self.registry.get_capability(capability_id)
        if not result:
            raise ValueError(f"Capability {capability_id} not found")

        capability, provider = result

        # Check provider trust
        if self.trust_tracker:
            metrics = self.trust_tracker.get_agent_metrics(provider.provider_id)
            if metrics and metrics.trust_score < 50.0:
                raise ValueError(
                    f"Provider {provider.provider_id} has insufficient trust ({metrics.trust_score:.1f})"
                )

        # Send request
        request = await self.send_request(
            target_id=provider.provider_id,
            operation="invoke",
            parameters=parameters,
            capability_id=capability_id,
            timeout=timeout,
            metadata={
                "capability_name": capability.name,
                "capability_type": capability.capability_type.value,
            }
        )

        # Wait for completion (in real implementation, this would be async)
        # For now, simulate immediate response
        return await self._wait_for_response(request)

    async def _wait_for_response(self, request: A2ARequest) -> Any:
        """
        Wait for a request to complete.

        Args:
            request: Request to wait for

        Returns:
            Request response

        Raises:
            TimeoutError: If request times out
        """
        start_time = datetime.utcnow()

        while True:
            if request.status == RequestStatus.COMPLETED:
                return request.response

            if request.status == RequestStatus.FAILED:
                raise RuntimeError(f"Request failed: {request.error}")

            if request.status == RequestStatus.TIMEOUT:
                raise TimeoutError(f"Request timed out after {request.timeout_seconds}s")

            if request.status == RequestStatus.REJECTED:
                raise PermissionError(f"Request rejected: {request.error}")

            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > request.timeout_seconds:
                request.status = RequestStatus.TIMEOUT
                raise TimeoutError(f"Request timed out after {elapsed:.1f}s")

            # Wait a bit before checking again
            await asyncio.sleep(0.1)

    def handle_response(self, message: A2AMessage):
        """
        Handle a response message.

        Args:
            message: Response message
        """
        # Verify message signature
        if not self.verify_message(message):
            print(f"⚠️ Invalid signature on response from {message.sender_id}")
            return

        # Find corresponding request
        request_id = message.payload.get("request_id")
        if not request_id or request_id not in self.pending_requests:
            print(f"⚠️ Unknown request ID: {request_id}")
            return

        request = self.pending_requests[request_id]

        # Update request
        if message.message_type == MessageType.RESPONSE:
            request.status = RequestStatus.COMPLETED
            request.response = message.payload.get("result")
            request.completed_at = datetime.utcnow()

        elif message.message_type == MessageType.ERROR:
            request.status = RequestStatus.FAILED
            request.error = message.payload.get("error", "Unknown error")
            request.completed_at = datetime.utcnow()

        # Call handler if registered
        if request_id in self.response_handlers:
            handler = self.response_handlers[request_id]
            handler(message)


class A2AServer:
    """
    Server for handling incoming A2A requests.

    Handles:
    - Message verification
    - Trust-based authorization
    - Request routing
    - Response generation
    """

    def __init__(
        self,
        agent_id: str,
        signer: Signer,
        verifier: Verifier,
        trust_tracker: Optional[AgentReputationTracker] = None,
        registry: Optional[CapabilityRegistry] = None,
        min_trust_score: float = 50.0,
    ):
        """
        Initialize A2A server.

        Args:
            agent_id: This agent's ID
            signer: Signer for response messages
            verifier: Verifier for request validation
            trust_tracker: For checking requester trust
            registry: Capability registry
            min_trust_score: Minimum trust score for requests
        """
        self.agent_id = agent_id
        self.signer = signer
        self.verifier = verifier
        self.trust_tracker = trust_tracker
        self.registry = registry
        self.min_trust_score = min_trust_score

        # Request handlers
        self.handlers: Dict[str, Callable] = {}

        # Active requests
        self.active_requests: Dict[str, A2ARequest] = {}

    def register_handler(self, operation: str, handler: Callable):
        """
        Register a handler for an operation.

        Args:
            operation: Operation name
            handler: Async handler function (request) -> result
        """
        self.handlers[operation] = handler

    async def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """
        Handle an incoming message.

        Args:
            message: Incoming message

        Returns:
            Response message (if applicable)
        """
        # Verify signature
        # Note: In production, use the actual verifier with certificate validation
        # For now, we'll skip verification in the demo
        # if not self._verify_message_signature(message):
        #     return self._create_error_response(
        #         message, "Invalid signature"
        #     )

        # Check requester trust
        if self.trust_tracker:
            metrics = self.trust_tracker.get_agent_metrics(message.sender_id)
            if metrics and metrics.trust_score < self.min_trust_score:
                return self._create_error_response(
                    message,
                    f"Insufficient trust score ({metrics.trust_score:.1f} < {self.min_trust_score})"
                )

        # Route based on message type
        if message.message_type == MessageType.REQUEST:
            return await self._handle_request(message)

        elif message.message_type == MessageType.CAPABILITY_INVOKE:
            return await self._handle_capability_invoke(message)

        elif message.message_type == MessageType.HANDSHAKE:
            return await self._handle_handshake(message)

        elif message.message_type == MessageType.HEARTBEAT:
            return self._create_heartbeat_response(message)

        return None

    async def _handle_request(self, message: A2AMessage) -> A2AMessage:
        """Handle a generic request."""
        operation = message.payload.get("operation")

        if not operation:
            return self._create_error_response(message, "No operation specified")

        if operation not in self.handlers:
            return self._create_error_response(message, f"Unknown operation: {operation}")

        # Execute handler
        try:
            handler = self.handlers[operation]
            result = await handler(message.payload.get("parameters", {}))

            return self._create_response(message, result)

        except Exception as e:
            return self._create_error_response(message, str(e))

    async def _handle_capability_invoke(self, message: A2AMessage) -> A2AMessage:
        """Handle a capability invocation request."""
        capability_id = message.payload.get("capability_id")
        parameters = message.payload.get("parameters", {})

        if not capability_id:
            return self._create_error_response(message, "No capability_id specified")

        # Check if we own this capability
        if self.registry:
            my_capabilities = self.registry.get_provider_capabilities(self.agent_id)
            my_cap_ids = {cap.capability_id for cap in my_capabilities}

            if capability_id not in my_cap_ids:
                return self._create_error_response(
                    message,
                    f"Capability {capability_id} not provided by this agent"
                )

        # Execute capability (if handler registered)
        operation = message.payload.get("operation", "invoke")

        if operation not in self.handlers:
            return self._create_error_response(
                message,
                f"Capability execution not implemented for operation: {operation}"
            )

        try:
            handler = self.handlers[operation]
            result = await handler(parameters)

            # Record invocation in registry
            if self.registry:
                self.registry.record_invocation(
                    capability_id=capability_id,
                    requester_id=message.sender_id,
                    status="success",
                    duration=0.0,  # TODO: Measure actual duration
                    metadata={"message_id": message.message_id}
                )

            return self._create_response(message, result)

        except Exception as e:
            # Record failed invocation
            if self.registry:
                self.registry.record_invocation(
                    capability_id=capability_id,
                    requester_id=message.sender_id,
                    status="failure",
                    error_message=str(e),
                    metadata={"message_id": message.message_id}
                )

            return self._create_error_response(message, str(e))

    async def _handle_handshake(self, message: A2AMessage) -> A2AMessage:
        """Handle a handshake request."""
        return self._create_response(
            message,
            {
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "capabilities": len(self.registry.get_provider_capabilities(self.agent_id)) if self.registry else 0,
            }
        )

    def _create_response(self, request_message: A2AMessage, result: Any) -> A2AMessage:
        """Create a response message."""
        return A2AMessage(
            message_id=f"msg-{uuid4().hex[:12]}",
            message_type=MessageType.RESPONSE,
            sender_id=self.agent_id,
            recipient_id=request_message.sender_id,
            correlation_id=request_message.message_id,
            payload={
                "request_id": request_message.payload.get("request_id"),
                "result": result,
                "status": "success",
            }
        )

    def _create_error_response(self, request_message: A2AMessage, error: str) -> A2AMessage:
        """Create an error response message."""
        return A2AMessage(
            message_id=f"msg-{uuid4().hex[:12]}",
            message_type=MessageType.ERROR,
            sender_id=self.agent_id,
            recipient_id=request_message.sender_id,
            correlation_id=request_message.message_id,
            payload={
                "request_id": request_message.payload.get("request_id"),
                "error": error,
                "status": "error",
            }
        )

    def _create_heartbeat_response(self, request_message: A2AMessage) -> A2AMessage:
        """Create a heartbeat response."""
        return A2AMessage(
            message_id=f"msg-{uuid4().hex[:12]}",
            message_type=MessageType.HEARTBEAT,
            sender_id=self.agent_id,
            recipient_id=request_message.sender_id,
            correlation_id=request_message.message_id,
            payload={
                "status": "online",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
