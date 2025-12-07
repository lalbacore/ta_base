
import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.services.enhanced_artifacts_service import EnhancedArtifactsService, PublishOptions

from app.storage import StorageType

class TestEnhancedPublishing(unittest.TestCase):
    
    def setUp(self):
        self.service = EnhancedArtifactsService()
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        # Mock providers
        self.mock_provider = MagicMock()
        self.service.providers = {StorageType.LOCAL: self.mock_provider}
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_list_backends(self):
        self.mock_provider.get_info.return_value = {'name': 'Local'}
        backends = self.service.list_available_backends()
        self.assertEqual(len(backends), 1)
        # Use .value to match the actual implementation which returns string value of enum
        self.assertEqual(backends[0]['storage_type'], StorageType.LOCAL.value)

    def test_publish_encrypted(self):
        # Mock crypto instance directly on the service
        self.service.crypto = MagicMock()
        self.service.crypto.derive_key_from_password.return_value = (b'key', b'salt')
        self.service.crypto.encrypt.return_value = (b'encrypted_content', {'nonce': '123'})
        self.service.crypto.export_key.return_value = 'base64key'
        
        # Setup mock provider
        mock_provider = MagicMock()
        # Ensure store returns success
        mock_provider.store.return_value = MagicMock(success=True, identifier='loc1', metadata={})
        
        # NOTE: self.service.providers is already set in setUp, but we'll override for clarity if needed
        self.service.providers = {StorageType.LOCAL: mock_provider}

        # Execute
        result = self.service.publish_artifact(
            workflow_id='wf1',
            artifact_name='test.txt',
            content=b'secret data',
            storage_backend='local',
            options=PublishOptions.ENCRYPT,
            encryption_password='password123'
        )
        
        if not result['success']:
            print(f"DEBUG: Publish failed: {result.get('error')}")

        # Verify
        self.assertTrue(result['success'])
        self.assertTrue(result['encrypted'])
        self.assertEqual(result['storage_identifier'], 'loc1')
        self.assertEqual(result['encryption_key'], 'base64key')
        
        # Verify crypto calls
        self.service.crypto.derive_key_from_password.assert_called_with('password123')
        self.service.crypto.encrypt.assert_called_with(b'secret data')
        
        # Verify storage call
        mock_provider.store.assert_called()
        args = mock_provider.store.call_args
        self.assertEqual(args[0][0], b'encrypted_content') # Content should be encrypted

if __name__ == '__main__':
    unittest.main()
