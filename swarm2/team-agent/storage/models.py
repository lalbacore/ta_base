from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
from datetime import datetime
import json

@dataclass
class AgentConfig:
    """Configuration for an agent role."""
    id: str
    name: str
    role_type: str  # architect, builder, critic, governance, recorder
    enabled: bool = True
    capabilities: List[str] = field(default_factory=list)
    policy: Dict = field(default_factory=dict)
    model_config: Optional[Dict] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        return asdict(self)


@dataclass
class TeamConfig:
    """Configuration for a team of agents."""
    id: str
    name: str
    description: str
    agent_ids: List[str]
    enabled: bool = True
    settings: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        return asdict(self)


@dataclass
class WorkflowRecord:
    """Complete workflow execution record."""
    workflow_id: str
    team_id: str
    request: str
    status: str  # success, rejected, failed
    result: Dict
    stages: Dict
    composite_score: Dict
    signature: Dict
    audit_log: Dict = field(default_factory=dict)  # ADD DEFAULT
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        return asdict(self)


@dataclass
class SIEMConnector:
    """Configuration for SIEM integration."""
    id: str
    name: str
    enabled: bool
    connector_type: str  # splunk, elasticsearch, datadog, etc.
    endpoint: str
    credentials: Dict  # Will be encrypted in storage
    format: str = "CEF"  # Common Event Format
    batch_size: int = 100
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        data = asdict(self)
        data.pop("credentials")  # Never return credentials
        return data


@dataclass
class BlockchainConfig:
    """Configuration for blockchain integration."""
    id: str
    name: str
    enabled: bool
    chain_type: str  # ethereum, polygon, hyperledger, etc.
    network: str  # mainnet, testnet, etc.
    contract_address: Optional[str] = None
    credentials: Dict = field(default_factory=dict)  # Will be encrypted
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        data = asdict(self)
        data.pop("credentials")
        return data


@dataclass
class Secret:
    """Encrypted secret storage."""
    id: str
    name: str
    secret_type: str  # api_key, password, token, etc.
    encrypted_value: str
    associated_resource: str  # siem_connector_id, blockchain_config_id, etc.
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        data = asdict(self)
        data.pop("encrypted_value")
        return data