"""
Architect Agent - Design system architecture.
Uses ToolRegistry for design validation and documentation.
"""
from typing import Dict, Any, List, Optional
import uuid

from ..tools import ToolRegistry, ScoringTool

# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None


class Architect:
    """
    Generates a simple high-level architecture plan from a mission/intent.
    Uses tools for design scoring and validation.
    """

    def __init__(
        self,
        workflow_id: str = "unknown",
        name: str = "Architect",
        id: str = "agent_architect_001",
        registry: Optional[ToolRegistry] = None,
        cert_chain: Optional[Dict[str, bytes]] = None
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.id = id
        self.metadata = {
            "id": self.id,
            "name": self.name,
            "description": "Designs high-level system architecture from intent.",
        }
        self.policy: Dict[str, Any] = {
            "can_design": True,
            "require_approval": False,
        }
        self.designs_created = 0
        self.designs: List[Dict[str, Any]] = []
        self.capabilities: List[str] = [
            "design_system",
            "evaluate_intent",
            "describe",
            "act",
        ]

        # Initialize tool registry
        self._registry = registry or ToolRegistry()
        self._register_default_tools()

        # Initialize signer if cert_chain is provided
        self.signer = None
        if cert_chain and CRYPTO_AVAILABLE:
            try:
                self.signer = Signer(
                    private_key_pem=cert_chain['key'],
                    certificate_pem=cert_chain['cert'],
                    signer_id="architect"
                )
            except Exception:
                pass
    
    def _register_default_tools(self) -> None:
        """Register default tools if not already present."""
        if "content_scorer" not in self._registry:
            self._registry.register(ScoringTool())

    def act(self, intent: str) -> Dict[str, Any]:
        """
        Produce an architecture from a free-form intent string.
        Returns an error dict when the intent is invalid.
        """
        if not self.evaluate_intent(intent):
            return {
                "status": "refused",
                "reason": "invalid_intent",
                "message": "Intent must be a non-empty string.",
            }

        design_id = str(uuid.uuid4())
        self.designs_created += 1

        # Generate components based on intent keywords
        intent_lower = intent.lower()
        components = []
        
        if "microservice" in intent_lower or "api" in intent_lower or "rest" in intent_lower:
            components = [
                {"name": "frontend", "responsibilities": ["presentation", "client routes"]},
                {"name": "backend", "responsibilities": ["business logic", "orchestration"]},
                {"name": "database", "responsibilities": ["data persistence", "queries"]},
                {"name": "api", "responsibilities": ["REST endpoints", "authentication"]},
            ]
        else:
            components = [
                {"name": "frontend", "responsibilities": ["presentation", "client routes"]},
                {"name": "backend", "responsibilities": ["business logic", "orchestration"]},
                {"name": "database", "responsibilities": ["data persistence", "queries"]},
                {"name": "api", "responsibilities": ["REST endpoints", "authentication"]},
            ]

        architecture = {
            "summary": "High-level architecture derived from intent.",
            "components": components,
            "interfaces": [],
            "risks": [],
            "decisions": [{"adr": "Monolith-first", "status": "accepted"}],
            "assumptions": ["stateless services where possible"],
        }
        
        doc = self._document(architecture, intent.strip())
        
        # Use scoring tool to evaluate design quality
        design_text = f"Intent: {intent}\nComponents: {', '.join(c['name'] for c in components)}\n{doc}"
        score_result = self._registry.invoke(
            "content_scorer",
            content=design_text,
            rubric={
                "completeness": {"weight": 0.4},
                "clarity": {"weight": 0.3},
                "feasibility": {"weight": 0.3},
            }
        )
        
        design_score = None
        if score_result.success:
            design_score = score_result.output
        
        # Record the design
        self.designs.append({
            "design_id": design_id,
            "intent": intent.strip(),
            "components": architecture.get("components", []),
            "summary": architecture.get("summary", ""),
        })

        result = {
            "status": "designed",
            "intent": intent.strip(),
            "design_id": design_id,
            "architecture": architecture,
            "documentation": doc,
            "components": architecture.get("components", []),
            "interfaces": architecture.get("interfaces", []),
            "risks": architecture.get("risks", []),
            "decisions": architecture.get("decisions", []),
            "design_score": design_score,
            "artifacts": [
                {
                    "type": "architecture",
                    "name": "high_level_plan",
                    "data": architecture,
                }
            ],
            "tools_used": ["content_scorer"],
        }

        # Sign output if signer is available
        if self.signer and CRYPTO_AVAILABLE:
            result = self.signer.sign_dict(result)

        return result

    def _design_architecture(self, intent: str) -> Dict[str, Any]:
        """
        Very lightweight heuristic decomposition into typical components.
        """
        intent_l = intent.lower()

        components: List[Dict[str, Any]] = []

        if any(w in intent_l for w in ("ui", "frontend", "front end", "react", "view")):
            components.append({"name": "frontend_ui", "responsibilities": ["presentation", "client routes"]})

        if "api" in intent_l or any(w in intent_l for w in ("server", "backend", "back end")):
            components.append({"name": "api_gateway", "responsibilities": ["http interface", "auth", "routing"]})
            components.append({"name": "application_service", "responsibilities": ["business logic"]})

        if any(w in intent_l for w in ("db", "database", "postgres", "mysql", "sqlite", "data model", "persist")):
            components.append({"name": "database", "responsibilities": ["persistence", "queries"]})

        if "auth" in intent_l or "authentication" in intent_l or "authorization" in intent_l:
            components.append({"name": "auth_service", "responsibilities": ["identity", "tokens", "roles"]})

        if "queue" in intent_l or "event" in intent_l or "kafka" in intent_l:
            components.append({"name": "message_bus", "responsibilities": ["async events", "decoupling"]})

        if not components:
            components.extend([
                {"name": "application_service", "responsibilities": ["business logic"]},
                {"name": "database", "responsibilities": ["persistence"]},
            ])

        seen = set()
        components = [c for c in components if not (c["name"] in seen or seen.add(c["name"]))]

        interfaces = []
        names = [c["name"] for c in components]
        if "frontend_ui" in names and "api_gateway" in names:
            interfaces.append({"from": "frontend_ui", "to": "api_gateway", "protocol": "HTTP/JSON"})
        if "api_gateway" in names and "application_service" in names:
            interfaces.append({"from": "api_gateway", "to": "application_service", "protocol": "in-process"})
        if "application_service" in names and "database" in names:
            interfaces.append({"from": "application_service", "to": "database", "protocol": "SQL"})

        risks = [
            {"risk": "auth_required_but_missing", "severity": "medium"}
        ] if ("auth" in intent_l and "auth_service" not in names) else []

        decisions = [
            {"adr": "Monolith-first", "status": "accepted"},
        ]

        return {
            "summary": "High-level architecture derived from intent.",
            "components": components,
            "interfaces": interfaces,
            "risks": risks,
            "decisions": decisions,
            "assumptions": ["stateless services where possible"],
        }

    def _document(self, plan: Dict[str, Any], intent: str) -> str:
        """
        Produce a concise textual documentation for the plan.
        """
        comps = ", ".join(c["name"] for c in plan.get("components", []))
        return (
            f"Architecture for: {intent}\n"
            f"Components: {comps}\n"
            f"Interfaces: {len(plan.get('interfaces', []))}\n"
            f"Decisions: {len(plan.get('decisions', []))}\n"
            f"Risks: {len(plan.get('risks', []))}\n"
        )

    def run(self, context: Any) -> Dict[str, Any]:
        """
        Run the architect with a context.
        Extracts intent/mission and delegates to act().
        """
        if isinstance(context, str):
            return self.act(context)
        if isinstance(context, dict):
            intent = context.get("mission") or context.get("intent") or context.get("input", "")
            if isinstance(intent, str):
                return self.act(intent)
            return self.act(str(intent))
        return self.act(str(context))

    def describe(self) -> Dict[str, Any]:
        """
        Return metadata and simple I/O schema for this role.
        """
        return {
            "id": self.id,
            "name": self.metadata.get("name", self.name),
            "description": self.metadata.get("description", ""),
            "type": "role",
            "role": "architect",
            "designs_created": self.designs_created,
            "capabilities": self.capabilities,
            "policy": self.policy,
            "tools_available": [t.name for t in self._registry.list_tools()],
            "inputs": {
                "intent": {"type": "string", "required": True, "description": "User intent or mission"}
            },
            "outputs": {
                "status": {"type": "string", "enum": ["designed", "refused"]},
                "design_id": {"type": "string", "required": False},
                "architecture": {"type": "object"},
                "documentation": {"type": "string"},
                "components": {"type": "array"},
                "interfaces": {"type": "array"},
                "risks": {"type": "array"},
                "decisions": {"type": "array"},
            },
        }

    def evaluate_intent(self, intent: str) -> bool:
        """
        Quick validation of intent text.
        Returns False for empty/invalid input, True otherwise.
        """
        return bool(isinstance(intent, str) and intent.strip())
