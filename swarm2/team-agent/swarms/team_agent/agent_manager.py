"""
Agent Manager - Manages workflow orchestration agents.

Responsibilities:
- Register workflow agents (Architect, Critic, Recorder, Governance) in agent_cards
- Track agent invocations and performance
- Update trust scores
- Provide agent discovery and stats

This fixes the "bogus agents" issue where trust scoring tracked agents
that weren't registered in the agent_cards table.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add backend to path for database access
backend_path = Path(__file__).parent.parent.parent / 'backend'
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from utils.logging import get_logger


class AgentManager:
    """
    Manages Level 1 workflow orchestration agents.

    Does NOT manage Level 2 capabilities - those are handled by DynamicBuilder.
    """

    def __init__(self):
        self.logger = get_logger("agent_manager")
        self._db_available = False
        self._init_database()

    def _init_database(self):
        """Initialize database connection."""
        try:
            from app.database import get_backend_session, init_backend_db
            from app.models.agent import AgentCard, AgentInvocation

            # Ensure schema exists
            init_backend_db()

            self._get_session = get_backend_session
            self._AgentCard = AgentCard
            self._AgentInvocation = AgentInvocation
            self._db_available = True
            self.logger.info("AgentManager initialized with database access")

        except Exception as e:
            self.logger.warning(f"Database not available for AgentManager: {e}")
            self._db_available = False

    def ensure_registered(self, agent) -> Optional[Any]:
        """
        Register agent in agent_cards table if not already registered.

        Args:
            agent: Agent instance with id, name, metadata attributes

        Returns:
            AgentCard instance if database available, None otherwise
        """
        if not self._db_available:
            self.logger.debug(f"Skipping registration for {agent.name} - database not available")
            return None

        try:
            with self._get_session() as session:
                # Check if already registered
                existing = session.query(self._AgentCard).filter_by(
                    agent_id=agent.id
                ).first()

                if existing:
                    self.logger.debug(f"Agent {agent.name} already registered")
                    return existing

                # Infer trust domain from agent name
                trust_domain = self._infer_trust_domain(agent)

                # Get metadata safely (some agents may not have it)
                metadata = getattr(agent, "metadata", {}) or {}
                description = metadata.get("description", f"{agent.name} workflow agent")

                # Create new agent card
                card = self._AgentCard(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type="role",  # Workflow orchestration role
                    description=description,
                    capabilities=json.dumps(getattr(agent, "capabilities", [])),
                    module_path=f"swarms.team_agent.roles.{agent.__class__.__name__.lower()}",
                    class_name=agent.__class__.__name__,
                    trust_domain=trust_domain,
                    trust_score=0.0,
                    total_invocations=0,
                    success_rate=0.0,
                    status="active",
                    version="1.0.0"
                )

                session.add(card)
                session.commit()

                self.logger.info(
                    f"Registered agent: {agent.name} (ID: {agent.id}, "
                    f"Type: role, Domain: {trust_domain})"
                )

                return card

        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.name}: {e}")
            return None

    def track_invocation(
        self,
        agent_id: str,
        workflow_id: str,
        result: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Record agent invocation and update statistics.

        Args:
            agent_id: Unique agent identifier
            workflow_id: Workflow this invocation belongs to
            result: Agent execution result (optional)
            success: Whether invocation succeeded
            error: Error message if failed
        """
        if not self._db_available:
            return

        try:
            with self._get_session() as session:
                # Generate unique invocation ID
                import uuid
                invocation_id = f"inv_{uuid.uuid4().hex[:16]}"

                # Create invocation record with correct fields
                now = datetime.now()
                invocation = self._AgentInvocation(
                    invocation_id=invocation_id,
                    agent_id=agent_id,
                    workflow_id=workflow_id,
                    started_at=now,
                    completed_at=now,
                    duration=0.0,  # Would need to track actual duration
                    status="success" if success else "failure",
                    error_message=error,
                    output_data=self._summarize_result(result)
                )
                session.add(invocation)

                # Update agent card statistics
                card = session.query(self._AgentCard).filter_by(agent_id=agent_id).first()
                if card:
                    # Update total invocations
                    card.total_invocations += 1

                    # Update success rate (running average)
                    if card.total_invocations == 1:
                        card.success_rate = 1.0 if success else 0.0
                    else:
                        old_total = card.total_invocations - 1
                        card.success_rate = (
                            (card.success_rate * old_total + (1.0 if success else 0.0)) /
                            card.total_invocations
                        )

                    # Update trust score (simple heuristic for now)
                    # Trust score = success_rate * 100
                    card.trust_score = card.success_rate * 100.0

                    self.logger.debug(
                        f"Updated stats for {agent_id}: "
                        f"invocations={card.total_invocations}, "
                        f"success_rate={card.success_rate:.2%}, "
                        f"trust_score={card.trust_score:.1f}"
                    )

                session.commit()

        except Exception as e:
            self.logger.error(f"Failed to track invocation for {agent_id}: {e}")

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for an agent.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Dictionary with agent statistics or None if not found
        """
        if not self._db_available:
            return None

        try:
            with self._get_session() as session:
                card = session.query(self._AgentCard).filter_by(agent_id=agent_id).first()
                if not card:
                    return None

                return {
                    "agent_id": card.agent_id,
                    "agent_name": card.agent_name,
                    "agent_type": card.agent_type,
                    "trust_domain": card.trust_domain,
                    "trust_score": card.trust_score,
                    "total_invocations": card.total_invocations,
                    "success_rate": card.success_rate,
                    "status": card.status,
                    "created_at": card.created_at.isoformat() if card.created_at else None,
                }

        except Exception as e:
            self.logger.error(f"Failed to get stats for {agent_id}: {e}")
            return None

    def get_all_agents(self) -> list:
        """
        Get all registered agents.

        Returns:
            List of agent statistics dictionaries
        """
        if not self._db_available:
            return []

        try:
            with self._get_session() as session:
                cards = session.query(self._AgentCard).all()
                return [
                    {
                        "agent_id": card.agent_id,
                        "agent_name": card.agent_name,
                        "agent_type": card.agent_type,
                        "trust_domain": card.trust_domain,
                        "trust_score": card.trust_score,
                        "total_invocations": card.total_invocations,
                        "success_rate": card.success_rate,
                        "status": card.status,
                    }
                    for card in cards
                ]

        except Exception as e:
            self.logger.error(f"Failed to get all agents: {e}")
            return []

    def _infer_trust_domain(self, agent) -> str:
        """
        Infer trust domain from agent name/class.

        Args:
            agent: Agent instance

        Returns:
            Trust domain string (EXECUTION, GOVERNMENT, or LOGGING)
        """
        agent_name = agent.name.lower()

        if "governance" in agent_name or "policy" in agent_name:
            return "GOVERNMENT"
        elif "recorder" in agent_name or "logger" in agent_name or "audit" in agent_name:
            return "LOGGING"
        else:
            # Default: Architect, Builder, Critic, etc.
            return "EXECUTION"

    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of agent result for storage.

        Args:
            result: Full agent result dictionary

        Returns:
            Summarized result (lighter weight for database)
        """
        if not result:
            return {}

        summary = {}

        # Include basic metrics
        if "score" in result:
            summary["score"] = result["score"]
        if "issues" in result:
            summary["issue_count"] = len(result["issues"])
        if "artifacts" in result:
            artifacts = result["artifacts"]
            if isinstance(artifacts, list):
                summary["artifact_count"] = len(artifacts)
            elif isinstance(artifacts, dict):
                summary["artifact_count"] = len(artifacts)
        if "capability_used" in result:
            summary["capability_used"] = result["capability_used"]

        return summary

    # ========================================================================
    # Specialist Agent Registration
    # ========================================================================

    def register_specialist(self, specialist_instance) -> Optional[Any]:
        """
        Register a specialist agent with its capabilities.

        Args:
            specialist_instance: Instance of a specialist agent (BaseSpecialist subclass)

        Returns:
            AgentCard instance if successful, None otherwise
        """
        if not self._db_available:
            return None

        try:
            with self._get_session() as session:
                # Import CapabilityRegistry and AgentCapabilityMapping models
                from app.models.agent import CapabilityRegistry, AgentCapabilityMapping

                # Get specialist metadata
                metadata = specialist_instance.get_metadata()

                # Check if already registered
                existing = session.query(self._AgentCard).filter_by(
                    agent_id=metadata["agent_id"]
                ).first()

                if existing:
                    self.logger.debug(f"Specialist {metadata['agent_name']} already registered")
                    return existing

                # Register primary capability in capability_registry
                primary_cap = specialist_instance.get_primary_capability()
                cap_metadata = primary_cap.get_metadata()

                capability_id = cap_metadata["name"]
                existing_cap = session.query(CapabilityRegistry).filter_by(
                    capability_id=capability_id
                ).first()

                if not existing_cap:
                    cap_record = CapabilityRegistry(
                        capability_id=capability_id,
                        capability_name=cap_metadata.get("display_name", cap_metadata["name"]),
                        capability_type=cap_metadata.get("type", "document_generation"),
                        description=cap_metadata.get("description", ""),
                        version=cap_metadata.get("version", "1.0.0"),
                        domains=json.dumps(cap_metadata.get("domains", [])),
                        keywords=json.dumps(specialist_instance.get_keywords() if hasattr(specialist_instance, 'get_keywords') else []),
                        module_path=cap_metadata.get("module_path", ""),
                        class_name=primary_cap.__class__.__name__,
                        status="active"
                    )
                    session.add(cap_record)
                    self.logger.info(f"Registered capability: {capability_id}")

                # Create agent card for specialist
                card = self._AgentCard(
                    agent_id=metadata["agent_id"],
                    agent_name=metadata["agent_name"],
                    agent_type="specialist",
                    description=metadata["description"],
                    capabilities=json.dumps(metadata["capabilities"]),
                    module_path=metadata["module_path"],
                    class_name=metadata["class_name"],
                    trust_domain=metadata["trust_domain"],
                    trust_score=0.0,
                    total_invocations=0,
                    success_rate=0.0,
                    status="active",
                    version=metadata["version"]
                )

                session.add(card)
                self.logger.info(f"Registered specialist agent: {metadata['agent_name']} (ID: {metadata['agent_id']})")

                # Create agent-capability mapping
                mapping = AgentCapabilityMapping(
                    agent_id=metadata["agent_id"],
                    capability_id=capability_id,
                    is_primary=True,
                    priority=1,
                    times_used=0,
                    success_rate=0.0
                )

                session.add(mapping)
                session.commit()

                self.logger.info(f"Mapped specialist {metadata['agent_name']} to capability {capability_id}")

                return card

        except Exception as e:
            self.logger.error(f"Failed to register specialist: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    def find_specialist_by_keywords(self, mission: str):
        """
        Find specialist agent matching mission keywords.

        Args:
            mission: Mission description string

        Returns:
            Specialist agent instance if match found, None otherwise
        """
        if not self._db_available:
            return None

        try:
            import importlib
            from app.models.agent import CapabilityRegistry, AgentCapabilityMapping
            from sqlalchemy import text

            mission_lower = mission.lower()

            with self._get_session() as session:
                # Query for specialist agents with matching keywords
                query = text("""
                    SELECT DISTINCT
                        ac.agent_id,
                        ac.agent_name,
                        ac.module_path,
                        ac.class_name,
                        ac.trust_score,
                        cr.keywords
                    FROM agent_cards ac
                    JOIN agent_capabilities acm ON ac.agent_id = acm.agent_id
                    JOIN capability_registry cr ON acm.capability_id = cr.capability_id
                    WHERE ac.agent_type = 'specialist'
                      AND ac.status = 'active'
                      AND acm.is_primary = 1
                    ORDER BY ac.trust_score DESC
                """)

                result = session.execute(query)
                rows = result.fetchall()

                # Find best match by keywords
                for row in rows:
                    try:
                        keywords_json = row[5]  # keywords column
                        keywords = json.loads(keywords_json) if keywords_json else []

                        # Check if any keyword matches mission
                        if any(kw.lower() in mission_lower for kw in keywords):
                            # Dynamically import and instantiate specialist
                            module = importlib.import_module(row[2])  # module_path
                            specialist_class = getattr(module, row[3])  # class_name

                            # Create instance
                            specialist = specialist_class(
                                agent_id=row[0],  # agent_id
                                workflow_id=getattr(self, 'workflow_id', None)
                            )

                            self.logger.info(
                                f"Selected specialist: {row[1]} (trust_score: {row[4]})"
                            )

                            return specialist

                    except Exception as e:
                        self.logger.error(f"Error loading specialist {row[1]}: {e}")
                        continue

                # No match found
                return None

        except Exception as e:
            self.logger.error(f"Failed to find specialist by keywords: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
