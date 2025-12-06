"""
Agent models for dynamic agent card system and agent discovery.

Models:
- AgentCard: Registered agent with capabilities and configuration
- AgentTemplate: Pre-configured agent templates
- AgentInvocation: Historical record of agent executions
- CapabilityRegistry: Catalog of available capabilities
- AgentCapabilityMapping: Relationship between agents and capabilities
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class AgentCard(Base, TimestampMixin):
    """
    Agent card for dynamic agent registration and discovery.

    Supports:
    - Dynamic agent creation without code changes
    - Capability-based discovery
    - Trust and reputation tracking
    - Versioning and lifecycle management
    - Provider pattern integration

    Each agent card represents a unique agent that can be:
    - Discovered by capability requirements
    - Instantiated dynamically from module_path and class_name
    - Tracked for reputation and performance
    - Assigned to swarms
    """
    __tablename__ = 'agent_cards'

    # Identity
    agent_id = Column(String, primary_key=True)
    agent_name = Column(String, nullable=False, index=True)
    agent_type = Column(String, nullable=False, index=True)  # "role", "specialist", "tool"
    description = Column(Text)
    version = Column(String, default="1.0.0", nullable=False)

    # Capabilities
    capabilities = Column(JSON)  # List of capability IDs (e.g., ["code_generation", "python"])
    specialties = Column(JSON)  # Domain specialties (e.g., ["backend", "api", "data_processing"])
    supported_languages = Column(JSON)  # Programming languages (e.g., ["python", "javascript"])

    # Configuration
    base_class = Column(String)  # Base class name (e.g., "BaseRole", "BaseAgent")
    config_schema = Column(JSON)  # JSON schema for configuration validation
    default_config = Column(JSON)  # Default configuration parameters

    # Metadata
    author = Column(String)
    homepage = Column(String)
    license = Column(String, default="MIT")
    tags = Column(JSON)  # Searchable tags

    # Trust & Reputation
    trust_score = Column(Float, default=0.0, index=True)
    total_invocations = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)

    # Lifecycle
    status = Column(String, default="active", index=True)  # active, inactive, deprecated
    certificate_serial = Column(String)  # PKI certificate serial number
    trust_domain = Column(String)  # EXECUTION, GOVERNMENT, LOGGING

    # Implementation
    module_path = Column(String, nullable=False)  # Python module path
    class_name = Column(String, nullable=False)  # Class to instantiate

    # Relationships
    invocations = relationship('AgentInvocation', back_populates='agent_card', cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<AgentCard(id={self.agent_id}, name='{self.agent_name}', "
                f"type={self.agent_type}, trust_score={self.trust_score})>")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'description': self.description,
            'version': self.version,
            'capabilities': self.capabilities,
            'specialties': self.specialties,
            'supported_languages': self.supported_languages,
            'base_class': self.base_class,
            'config_schema': self.config_schema,
            'default_config': self.default_config,
            'author': self.author,
            'homepage': self.homepage,
            'license': self.license,
            'tags': self.tags,
            'trust_score': self.trust_score,
            'total_invocations': self.total_invocations,
            'success_rate': self.success_rate,
            'average_rating': self.average_rating,
            'status': self.status,
            'certificate_serial': self.certificate_serial,
            'trust_domain': self.trust_domain,
            'module_path': self.module_path,
            'class_name': self.class_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AgentTemplate(Base, TimestampMixin):
    """
    Pre-configured agent template for quick agent creation.

    Templates provide:
    - Reusable agent configurations
    - Role templates (code_generator, reviewer, analyst, etc.)
    - Base agent card with specific configuration
    - Quick instantiation with template.instantiate()

    Example templates:
    - python_code_reviewer
    - javascript_generator
    - security_auditor
    - performance_optimizer
    """
    __tablename__ = 'agent_templates'

    template_id = Column(String, primary_key=True)
    template_name = Column(String, nullable=False, index=True)
    template_type = Column(String, index=True)  # "code_generator", "reviewer", "analyst"
    description = Column(Text)

    # Template configuration
    base_agent_card_id = Column(String, ForeignKey('agent_cards.agent_id'))
    configuration = Column(JSON)  # Template-specific configuration

    # Relationship
    base_agent_card = relationship('AgentCard', foreign_keys=[base_agent_card_id])

    def __repr__(self):
        return (f"<AgentTemplate(id={self.template_id}, name='{self.template_name}', "
                f"type={self.template_type})>")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'template_id': self.template_id,
            'template_name': self.template_name,
            'template_type': self.template_type,
            'description': self.description,
            'base_agent_card_id': self.base_agent_card_id,
            'configuration': self.configuration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AgentInvocation(Base, TimestampMixin):
    """
    Historical record of agent invocations for reputation tracking.

    Tracks:
    - Which agent was invoked
    - For which workflow/mission
    - Input/output data
    - Execution duration and status
    - User feedback and ratings

    Used for:
    - Reputation calculation
    - Performance metrics
    - Debugging and auditing
    - Agent selection optimization
    """
    __tablename__ = 'agent_invocations'

    invocation_id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey('agent_cards.agent_id'), nullable=False, index=True)
    workflow_id = Column(String, index=True)
    mission_id = Column(String, index=True)
    stage = Column(String)  # Stage name in workflow

    # Execution details
    input_data = Column(JSON)
    output_data = Column(JSON)

    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration = Column(Float)  # Execution duration in seconds
    status = Column(String, nullable=False, index=True)  # success, failure, timeout
    error_message = Column(Text)

    # Feedback
    rating = Column(Float)  # User feedback 0-5
    feedback = Column(Text)

    # Relationship
    agent_card = relationship('AgentCard', back_populates='invocations')

    def __repr__(self):
        return (f"<AgentInvocation(id={self.invocation_id}, agent={self.agent_id}, "
                f"status={self.status}, duration={self.duration}s)>")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'invocation_id': self.invocation_id,
            'agent_id': self.agent_id,
            'workflow_id': self.workflow_id,
            'mission_id': self.mission_id,
            'stage': self.stage,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'status': self.status,
            'error_message': self.error_message,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CapabilityRegistry(Base, TimestampMixin):
    """
    Registry of available capabilities (tools, functions, modules).

    Capabilities are reusable components that agents can invoke to perform
    domain-specific tasks (e.g., legal document generation, code analysis).

    Tracks:
    - Capability metadata (name, type, domains, keywords)
    - Implementation details (module path, class name)
    - Version and status for lifecycle management

    Used for:
    - Capability discovery by keywords/domains
    - Agent-capability mapping
    - Dynamic capability loading
    """
    __tablename__ = 'capability_registry'

    # Identity
    capability_id = Column(String, primary_key=True)
    capability_name = Column(String, nullable=False, index=True)
    capability_type = Column(String, nullable=False, index=True)  # document_generation, code_generation, analysis
    description = Column(Text)
    version = Column(String, default="1.0.0", nullable=False)

    # Discovery metadata
    domains = Column(JSON)  # ["legal", "contracts", "compliance"]
    keywords = Column(JSON)  # ["nda", "contract", "privacy", "gdpr"]
    tags = Column(JSON)  # Additional searchable tags

    # Implementation
    module_path = Column(String, nullable=False)  # Python module path
    class_name = Column(String, nullable=False)  # Class to instantiate

    # Lifecycle
    status = Column(String, default="active", index=True)  # active, deprecated
    author = Column(String)
    license = Column(String, default="MIT")

    # Relationships
    agent_mappings = relationship('AgentCapabilityMapping', back_populates='capability', cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<CapabilityRegistry(id={self.capability_id}, name='{self.capability_name}', "
                f"type={self.capability_type}, status={self.status})>")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'capability_id': self.capability_id,
            'capability_name': self.capability_name,
            'capability_type': self.capability_type,
            'description': self.description,
            'version': self.version,
            'domains': self.domains,
            'keywords': self.keywords,
            'tags': self.tags,
            'module_path': self.module_path,
            'class_name': self.class_name,
            'status': self.status,
            'author': self.author,
            'license': self.license,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AgentCapabilityMapping(Base, TimestampMixin):
    """
    Maps agents to capabilities they can use.

    Defines the relationship between agents (who) and capabilities (what they can do).
    An agent can use multiple capabilities, and a capability can be used by multiple agents.

    Tracks:
    - Which capabilities each agent uses
    - Priority/preference for capability selection
    - Performance metrics per agent-capability combination
    - Primary vs. secondary capabilities

    Used for:
    - Agent capability discovery
    - Performance tracking per agent-capability pair
    - Capability selection by agent
    """
    __tablename__ = 'agent_capabilities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey('agent_cards.agent_id'), nullable=False, index=True)
    capability_id = Column(String, ForeignKey('capability_registry.capability_id'), nullable=False, index=True)

    # Capability metadata
    is_primary = Column(Boolean, default=False)  # Is this the agent's primary capability?
    priority = Column(Integer, default=1)  # Order of preference (1=highest)

    # Performance tracking
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)

    # Relationships
    agent = relationship('AgentCard', foreign_keys=[agent_id])
    capability = relationship('CapabilityRegistry', back_populates='agent_mappings')

    def __repr__(self):
        return (f"<AgentCapabilityMapping(agent={self.agent_id}, capability={self.capability_id}, "
                f"primary={self.is_primary}, priority={self.priority})>")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'capability_id': self.capability_id,
            'is_primary': self.is_primary,
            'priority': self.priority,
            'times_used': self.times_used,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
