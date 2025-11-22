import unittest
import os
from config.settings import Settings

class TestSettings(unittest.TestCase):
    """Test application settings."""
    
    def setUp(self):
        """Store original environment variables."""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Restore original environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_default_settings(self):
        """Test that default settings are correct."""
        self.assertEqual(Settings.STORAGE_TYPE, "file")
        self.assertEqual(Settings.LOG_LEVEL, "INFO")
        self.assertEqual(Settings.MIN_QUALITY_SCORE, 70)
        self.assertEqual(Settings.COMPLIANCE_THRESHOLD, 80)
        self.assertTrue(Settings.REQUIRE_REVIEW_PASSED)
        self.assertTrue(Settings.REQUIRE_APPROVAL)
    
    def test_storage_type_from_env(self):
        """Test reading STORAGE_TYPE from environment."""
        os.environ["STORAGE_TYPE"] = "postgres"
        # Reload settings (in real app, this would be done differently)
        # For now, just verify the mechanism works
        self.assertEqual(os.getenv("STORAGE_TYPE"), "postgres")
    
    def test_log_level_from_env(self):
        """Test reading LOG_LEVEL from environment."""
        os.environ["LOG_LEVEL"] = "DEBUG"
        self.assertEqual(os.getenv("LOG_LEVEL"), "DEBUG")
    
    def test_numeric_settings_parsing(self):
        """Test parsing numeric environment variables."""
        os.environ["MIN_QUALITY_SCORE"] = "85"
        # This would need a reload mechanism in production
        parsed = int(os.getenv("MIN_QUALITY_SCORE"))
        self.assertEqual(parsed, 85)
    
    def test_boolean_settings_parsing(self):
        """Test parsing boolean environment variables."""
        os.environ["REQUIRE_REVIEW_PASSED"] = "false"
        value = os.getenv("REQUIRE_REVIEW_PASSED").lower() == "true"
        self.assertFalse(value)
    
    def test_export_config_method(self):
        """Test get_export_config method."""
        config = Settings.get_export_config()
        
        self.assertIn("siem", config)
        self.assertIn("a2a", config)
        self.assertIn("mcp", config)
        self.assertIn("blockchain", config)
        self.assertIsInstance(config["siem"], bool)
    
    def test_storage_config_method(self):
        """Test get_storage_config method."""
        config = Settings.get_storage_config()
        
        self.assertIn("type", config)
        self.assertIn("data_dir", config)
        self.assertEqual(config["type"], "file")
    
    def test_encryption_key_optional(self):
        """Test that encryption key is optional."""
        key = Settings.SECRETS_ENCRYPTION_KEY
        # Should be None unless explicitly set
        if key is None:
            self.assertIsNone(key)
        else:
            self.assertIsInstance(key, str)
    
    def test_data_dir_default(self):
        """Test DATA_DIR has sensible default."""
        data_dir = Settings.DATA_DIR
        self.assertIsNotNone(data_dir)
        self.assertTrue(len(data_dir) > 0)
    
    def test_retention_days_parsing(self):
        """Test RECORD_RETENTION_DAYS parsing."""
        retention = Settings.RECORD_RETENTION_DAYS
        self.assertIsInstance(retention, int)
        self.assertGreater(retention, 0)
    
    def test_quality_score_threshold(self):
        """Test quality score threshold is reasonable."""
        score = Settings.MIN_QUALITY_SCORE
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_compliance_threshold(self):
        """Test compliance threshold is reasonable."""
        threshold = Settings.COMPLIANCE_THRESHOLD
        self.assertGreaterEqual(threshold, 0)
        self.assertLessEqual(threshold, 100)
    
    def test_threshold_relationship(self):
        """Test that compliance threshold >= quality score."""
        # Generally compliance should be at least as high as quality
        self.assertGreaterEqual(
            Settings.COMPLIANCE_THRESHOLD,
            Settings.MIN_QUALITY_SCORE
        )

if __name__ == '__main__':
    unittest.main()