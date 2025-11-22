import unittest
import tempfile
import shutil
from storage.models import (
    AgentConfig, TeamConfig, WorkflowRecord, 
    SIEMConnector, BlockchainConfig, Secret
)
from storage.database import FileStorageBackend, get_storage, set_storage

class TestStorageModels(unittest.TestCase):
    """Test data models."""
    
    def test_agent_config_creation(self):
        """Test creating an AgentConfig."""
        config = AgentConfig(
            id="architect_001",
            name="Architect",
            role_type="architect",
            capabilities=["design_system", "evaluate_requirements"],
            policy={"can_design": True}
        )
        
        self.assertEqual(config.id, "architect_001")
        self.assertEqual(config.name, "Architect")
        self.assertTrue(config.enabled)
        self.assertIn("design_system", config.capabilities)
    
    def test_agent_config_to_dict(self):
        """Test converting AgentConfig to dict."""
        config = AgentConfig(
            id="test_001",
            name="Test Agent",
            role_type="test"
        )
        data = config.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data["id"], "test_001")
        self.assertIn("created_at", data)
    
    def test_team_config_creation(self):
        """Test creating a TeamConfig."""
        team = TeamConfig(
            id="team_001",
            name="Default Team",
            description="Standard 5-agent team",
            agent_ids=["arch_001", "build_001", "critic_001", "gov_001", "rec_001"]
        )
        
        self.assertEqual(team.id, "team_001")
        self.assertEqual(len(team.agent_ids), 5)
        self.assertTrue(team.enabled)
    
    def test_workflow_record_creation(self):
        """Test creating a WorkflowRecord."""
        record = WorkflowRecord(
            workflow_id="wf_001",
            team_id="team_001",
            request="Build a system",
            status="success",
            result={},
            stages={},
            composite_score={},
            signature={}
            # audit_log now optional with default
        )
        
        self.assertEqual(record.workflow_id, "wf_001")
        self.assertEqual(record.status, "success")
    
    def test_siem_connector_creation(self):
        """Test creating a SIEMConnector."""
        connector = SIEMConnector(
            id="siem_001",
            name="Splunk Enterprise",
            enabled=True,
            connector_type="splunk",
            endpoint="https://splunk.example.com:8088",
            credentials={"token": "secret123"}
        )
        
        self.assertEqual(connector.id, "siem_001")
        self.assertEqual(connector.connector_type, "splunk")
        self.assertEqual(connector.format, "CEF")
    
    def test_siem_connector_to_dict_hides_credentials(self):
        """Test that SIEMConnector.to_dict() hides credentials."""
        connector = SIEMConnector(
            id="siem_001",
            name="Splunk",
            enabled=True,
            connector_type="splunk",
            endpoint="https://splunk.example.com:8088",
            credentials={"token": "secret123"}
        )
        
        data = connector.to_dict()
        self.assertNotIn("credentials", data)
        self.assertEqual(data["name"], "Splunk")
    
    def test_blockchain_config_creation(self):
        """Test creating a BlockchainConfig."""
        config = BlockchainConfig(
            id="blockchain_001",
            name="Ethereum Mainnet",
            enabled=True,
            chain_type="ethereum",
            network="mainnet",
            contract_address="0x1234567890123456789012345678901234567890"
        )
        
        self.assertEqual(config.id, "blockchain_001")
        self.assertEqual(config.chain_type, "ethereum")
    
    def test_secret_creation(self):
        """Test creating a Secret."""
        secret = Secret(
            id="secret_001",
            name="API Key",
            secret_type="api_key",
            encrypted_value="encrypted_abc123",
            associated_resource="siem_connector_001"
        )
        
        self.assertEqual(secret.id, "secret_001")
        self.assertEqual(secret.secret_type, "api_key")


class TestFileStorageBackend(unittest.TestCase):
    """Test file-based storage backend."""
    
    def setUp(self):
        """Create temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = FileStorageBackend(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_storage_initializes_directories(self):
        """Test that storage creates required directories."""
        import os
        self.assertTrue(os.path.exists(f"{self.test_dir}/agents"))
        self.assertTrue(os.path.exists(f"{self.test_dir}/teams"))
        self.assertTrue(os.path.exists(f"{self.test_dir}/workflows"))
        self.assertTrue(os.path.exists(f"{self.test_dir}/connectors"))
        self.assertTrue(os.path.exists(f"{self.test_dir}/secrets"))
    
    def test_save_and_get_agent_config(self):
        """Test saving and retrieving agent config."""
        config = AgentConfig(
            id="arch_001",
            name="Architect",
            role_type="architect",
            capabilities=["design"]
        )
        
        # Save
        result = self.storage.save_agent_config(config)
        self.assertTrue(result)
        
        # Retrieve
        retrieved = self.storage.get_agent_config("arch_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "arch_001")
        self.assertEqual(retrieved.name, "Architect")
    
    def test_list_agent_configs(self):
        """Test listing all agent configs."""
        config1 = AgentConfig(id="arch_001", name="Architect", role_type="architect")
        config2 = AgentConfig(id="build_001", name="Builder", role_type="builder")
        
        self.storage.save_agent_config(config1)
        self.storage.save_agent_config(config2)
        
        configs = self.storage.list_agent_configs()
        self.assertEqual(len(configs), 2)
        ids = [c.id for c in configs]
        self.assertIn("arch_001", ids)
        self.assertIn("build_001", ids)
    
    def test_save_and_get_team_config(self):
        """Test saving and retrieving team config."""
        team = TeamConfig(
            id="team_001",
            name="Default Team",
            description="Test team",
            agent_ids=["arch_001", "build_001"]
        )
        
        result = self.storage.save_team_config(team)
        self.assertTrue(result)
        
        retrieved = self.storage.get_team_config("team_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved.agent_ids), 2)
    
    def test_save_and_get_workflow_record(self):
        """Test saving and retrieving workflow record."""
        record = WorkflowRecord(
            workflow_id="wf_001",
            team_id="team_001",
            request="Build a system",
            status="success",
            result={},
            stages={},
            composite_score={},
            signature={}
            # audit_log optional
        )
        
        result = self.storage.save_workflow_record(record)
        self.assertTrue(result)
        
        retrieved = self.storage.get_workflow_record("wf_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.request, "Build a system")
    
    def test_save_and_list_siem_connectors(self):
        """Test saving and listing SIEM connectors."""
        connector1 = SIEMConnector(
            id="siem_001",
            name="Splunk",
            enabled=True,
            connector_type="splunk",
            endpoint="https://splunk.example.com",
            credentials={}
        )
        connector2 = SIEMConnector(
            id="siem_002",
            name="Elasticsearch",
            enabled=False,
            connector_type="elasticsearch",
            endpoint="https://es.example.com",
            credentials={}
        )
        
        self.storage.save_siem_connector(connector1)
        self.storage.save_siem_connector(connector2)
        
        # List all
        all_connectors = self.storage.list_siem_connectors()
        self.assertEqual(len(all_connectors), 2)
        
        # List enabled only
        enabled = self.storage.list_siem_connectors(enabled_only=True)
        self.assertEqual(len(enabled), 1)
        self.assertEqual(enabled[0].id, "siem_001")
    
    def test_save_and_list_blockchain_configs(self):
        """Test saving and listing blockchain configs."""
        config1 = BlockchainConfig(
            id="bc_001",
            name="Ethereum",
            enabled=True,
            chain_type="ethereum",
            network="mainnet"
        )
        config2 = BlockchainConfig(
            id="bc_002",
            name="Polygon",
            enabled=True,
            chain_type="polygon",
            network="mainnet"
        )
        
        self.storage.save_blockchain_config(config1)
        self.storage.save_blockchain_config(config2)
        
        configs = self.storage.list_blockchain_configs()
        self.assertEqual(len(configs), 2)
    
    def test_save_and_get_secret(self):
        """Test saving and retrieving secrets."""
        secret = Secret(
            id="secret_001",
            name="API Token",
            secret_type="api_key",
            encrypted_value="encrypted_token_abc123",
            associated_resource="siem_001"
        )
        
        result = self.storage.save_secret(secret)
        self.assertTrue(result)
        
        retrieved = self.storage.get_secret("secret_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "API Token")
    
    def test_get_nonexistent_config(self):
        """Test getting a config that doesn't exist."""
        result = self.storage.get_agent_config("nonexistent")
        self.assertIsNone(result)
    
    def test_storage_persistence(self):
        """Test that storage persists across instances."""
        config = AgentConfig(id="persist_001", name="Persistent", role_type="test")
        self.storage.save_agent_config(config)
        
        # Create new storage instance with same directory
        storage2 = FileStorageBackend(data_dir=self.test_dir)
        retrieved = storage2.get_agent_config("persist_001")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Persistent")


class TestStorageGlobalInstance(unittest.TestCase):
    """Test global storage instance management."""
    
    def test_get_storage_returns_instance(self):
        """Test that get_storage returns a storage instance."""
        storage = get_storage()
        self.assertIsNotNone(storage)
    
    def test_set_storage_updates_instance(self):
        """Test that set_storage updates the global instance."""
        test_dir = tempfile.mkdtemp()
        try:
            custom_storage = FileStorageBackend(data_dir=test_dir)
            set_storage(custom_storage)
            
            retrieved = get_storage()
            self.assertEqual(retrieved, custom_storage)
        finally:
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    unittest.main()