import json
import os
from typing import List, Optional, Dict, Any
from storage.models import (
    AgentConfig, TeamConfig, WorkflowRecord, 
    SIEMConnector, BlockchainConfig, Secret
)

class StorageBackend:
    """Abstract storage backend."""
    
    def save_agent_config(self, config: AgentConfig) -> bool:
        raise NotImplementedError
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        raise NotImplementedError
    
    def list_agent_configs(self) -> List[AgentConfig]:
        raise NotImplementedError
    
    def save_team_config(self, config: TeamConfig) -> bool:
        raise NotImplementedError
    
    def get_team_config(self, team_id: str) -> Optional[TeamConfig]:
        raise NotImplementedError
    
    def save_workflow_record(self, record: WorkflowRecord) -> bool:
        raise NotImplementedError
    
    def get_workflow_record(self, workflow_id: str) -> Optional[WorkflowRecord]:
        raise NotImplementedError
    
    def save_siem_connector(self, connector: SIEMConnector) -> bool:
        raise NotImplementedError
    
    def list_siem_connectors(self, enabled_only: bool = False) -> List[SIEMConnector]:
        raise NotImplementedError
    
    def save_blockchain_config(self, config: BlockchainConfig) -> bool:
        raise NotImplementedError
    
    def list_blockchain_configs(self) -> List[BlockchainConfig]:
        raise NotImplementedError
    
    def save_secret(self, secret: Secret) -> bool:
        raise NotImplementedError
    
    def get_secret(self, secret_id: str) -> Optional[Secret]:
        raise NotImplementedError


class FileStorageBackend(StorageBackend):
    """File-based storage for development/testing."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create data directories if they don't exist."""
        dirs = [
            f"{self.data_dir}/agents",
            f"{self.data_dir}/teams",
            f"{self.data_dir}/workflows",
            f"{self.data_dir}/connectors",
            f"{self.data_dir}/secrets"
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def save_agent_config(self, config: AgentConfig) -> bool:
        try:
            path = f"{self.data_dir}/agents/{config.id}.json"
            with open(path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        try:
            path = f"{self.data_dir}/agents/{agent_id}.json"
            with open(path, 'r') as f:
                data = json.load(f)
            return AgentConfig(**data)
        except Exception:
            return None
    
    def list_agent_configs(self) -> List[AgentConfig]:
        configs = []
        agents_dir = f"{self.data_dir}/agents"
        try:
            for filename in os.listdir(agents_dir):
                if filename.endswith('.json'):
                    agent_id = filename.replace('.json', '')
                    config = self.get_agent_config(agent_id)
                    if config:
                        configs.append(config)
        except Exception:
            pass
        return configs
    
    def save_team_config(self, config: TeamConfig) -> bool:
        try:
            path = f"{self.data_dir}/teams/{config.id}.json"
            with open(path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def get_team_config(self, team_id: str) -> Optional[TeamConfig]:
        try:
            path = f"{self.data_dir}/teams/{team_id}.json"
            with open(path, 'r') as f:
                data = json.load(f)
            return TeamConfig(**data)
        except Exception:
            return None
    
    def save_workflow_record(self, record: WorkflowRecord) -> bool:
        try:
            path = f"{self.data_dir}/workflows/{record.workflow_id}.json"
            with open(path, 'w') as f:
                json.dump(record.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def get_workflow_record(self, workflow_id: str) -> Optional[WorkflowRecord]:
        try:
            path = f"{self.data_dir}/workflows/{workflow_id}.json"
            with open(path, 'r') as f:
                data = json.load(f)
            return WorkflowRecord(**data)
        except Exception:
            return None
    
    def save_siem_connector(self, connector: SIEMConnector) -> bool:
        try:
            path = f"{self.data_dir}/connectors/siem_{connector.id}.json"
            with open(path, 'w') as f:
                # Save the full object, not just to_dict()
                data = {
                    "id": connector.id,
                    "name": connector.name,
                    "enabled": connector.enabled,
                    "connector_type": connector.connector_type,
                    "endpoint": connector.endpoint,
                    "format": connector.format,
                    "batch_size": connector.batch_size,
                    "created_at": connector.created_at,
                    "credentials": connector.credentials  # Include for storage
                }
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving SIEM connector: {e}")
            return False
    
    def list_siem_connectors(self, enabled_only: bool = False) -> List[SIEMConnector]:
        connectors = []
        try:
            connectors_dir = f"{self.data_dir}/connectors"
            if not os.path.exists(connectors_dir):
                return connectors
                
            for filename in os.listdir(connectors_dir):
                if filename.startswith('siem_') and filename.endswith('.json'):
                    connector_id = filename.replace('siem_', '').replace('.json', '')
                    path = f"{connectors_dir}/{filename}"
                    try:
                        with open(path, 'r') as f:
                            data = json.load(f)
                        connector = SIEMConnector(**data)
                        if not enabled_only or connector.enabled:
                            connectors.append(connector)
                    except Exception:
                        continue
        except Exception:
            pass
        return connectors
    
    def save_blockchain_config(self, config: BlockchainConfig) -> bool:
        try:
            path = f"{self.data_dir}/connectors/blockchain_{config.id}.json"
            with open(path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def list_blockchain_configs(self) -> List[BlockchainConfig]:
        configs = []
        try:
            connectors_dir = f"{self.data_dir}/connectors"
            for filename in os.listdir(connectors_dir):
                if filename.startswith('blockchain_') and filename.endswith('.json'):
                    config_id = filename.replace('blockchain_', '').replace('.json', '')
                    path = f"{connectors_dir}/{filename}"
                    with open(path, 'r') as f:
                        data = json.load(f)
                    configs.append(BlockchainConfig(**data))
        except Exception:
            pass
        return configs
    
    def save_secret(self, secret: Secret) -> bool:
        try:
            path = f"{self.data_dir}/secrets/{secret.id}.json"
            with open(path, 'w') as f:
                data = {
                    "id": secret.id,
                    "name": secret.name,
                    "secret_type": secret.secret_type,
                    "encrypted_value": secret.encrypted_value,
                    "associated_resource": secret.associated_resource,
                    "created_at": secret.created_at
                }
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving secret: {e}")
            return False
    
    def get_secret(self, secret_id: str) -> Optional[Secret]:
        try:
            path = f"{self.data_dir}/secrets/{secret_id}.json"
            if not os.path.exists(path):
                return None
            with open(path, 'r') as f:
                data = json.load(f)
            return Secret(**data)
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            return None


# Global storage instance (dependency injection pattern)
_storage_backend: Optional[StorageBackend] = None

def get_storage() -> StorageBackend:
    global _storage_backend
    if _storage_backend is None:
        _storage_backend = FileStorageBackend()
    return _storage_backend

def set_storage(backend: StorageBackend):
    global _storage_backend
    _storage_backend = backend