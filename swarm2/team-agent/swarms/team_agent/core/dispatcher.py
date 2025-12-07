"""
Message Dispatcher - Routes messages between SwarmNodes.
"""
from typing import Dict, Any, Optional
import logging

from swarms.team_agent.core.message import AgentMessage
from swarms.team_agent.core.node import SwarmNode

class MessageDispatcher:
    """
    Central hub for routing messages between agents in the runtime mesh.
    In a distributed system, this would be a message queue (RabbitMQ/Kafka).
    Here, it's an in-memory router.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MessageDispatcher")
        self.registry: Dict[str, SwarmNode] = {}
        
    def register_node(self, node: SwarmNode):
        """Register a node for message reception."""
        self.registry[node.id] = node
        self.logger.debug(f"Registered node: {node.id} ({node.name})")

    def unregister_node(self, node_id: str):
        """Unregister a node."""
        if node_id in self.registry:
            del self.registry[node_id]

    def send_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Route a message to its target.
        Returns the synchronous response message (if any).
        """
        target_id = message.target_id
        
        if target_id == "broadcast":
            # Handle broadcast (not implemented for sync return)
            self.logger.warning("Broadcast not supported for synchronous send_message")
            return None
            
        target_node = self.registry.get(target_id)
        if not target_node:
            self.logger.error(f"Target node not found: {target_id}")
            return None
            
        try:
            # Deliver message
            self.logger.info(f"Routing {message.message_type} from {message.sender_id} to {target_id}")
            response_payload = target_node.receive_message(message)
            
            # Convert dict response to AgentMessage from target
            # Note: receive_message currently returns a dict. 
            # Ideally, nodes should reply with AgentMessage.
            # For now, we wrap the dict.
            
            response = target_node.create_message(
                target_id=message.sender_id,
                message_type="response",
                payload=response_payload,
                conversation_id=message.conversation_id
            )
            return response
            
        except Exception as e:
            self.logger.error(f"Error delivering message to {target_id}: {e}")
            return None

    def find_node_by_role(self, role: str) -> Optional[SwarmNode]:
        """Find a single node by role/type."""
        for node in self.registry.values():
            if node.agent_type == "role" and node.name.lower() == role.lower():
                return node
            if node.name.lower() == role.lower():
                return node
        return None
