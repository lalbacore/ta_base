import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../swarms')))

import unittest
from team_agent.registry import Registry
from team_agent.agent_card import AgentCard
from typing import Dict, Any

class AgentCard:
    def __init__(self, agent_id: str, name: str, endpoint: str, public_key: str, capabilities: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.endpoint = endpoint
        self.public_key = public_key
        self.capabilities = capabilities

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "endpoint": self.endpoint,
            "public_key": self.public_key,
            "capabilities": self.capabilities,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AgentCard":
        return AgentCard(
            agent_id=d["agent_id"],
            name=d.get("name", ""),
            endpoint=d.get("endpoint", ""),
            public_key=d.get("public_key", ""),
            capabilities=d.get("capabilities", {}),
        )

class TestAgentCardRegistry(unittest.TestCase):
    def test_publish_and_list_agent_card(self):
        reg = Registry(":memory:")
        card = AgentCard(
            agent_id="agent_001",
            name="Test Agent",
            endpoint="http://localhost:8000",
            public_key="abc123",
            capabilities={"search": True, "build": True}
        )
        reg.publish_agent_card(card.to_dict())
        cards = reg.list_agent_cards()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["agent_id"], "agent_001")
        self.assertEqual(cards[0]["name"], "Test Agent")