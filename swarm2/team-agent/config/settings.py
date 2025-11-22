import os
from typing import Optional

class Settings:
    """Application settings with environment variable support."""
    
    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "file")  # file, postgres, mongodb
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Policy Engine
    MIN_QUALITY_SCORE: int = int(os.getenv("MIN_QUALITY_SCORE", "70"))
    COMPLIANCE_THRESHOLD: int = int(os.getenv("COMPLIANCE_THRESHOLD", "80"))
    
    # Governance
    REQUIRE_REVIEW_PASSED: bool = os.getenv("REQUIRE_REVIEW_PASSED", "true").lower() == "true"
    REQUIRE_APPROVAL: bool = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"
    
    # Recording & Signing
    ENABLE_CRYPTOGRAPHIC_SIGNING: bool = os.getenv("ENABLE_CRYPTOGRAPHIC_SIGNING", "true").lower() == "true"
    RECORD_RETENTION_DAYS: int = int(os.getenv("RECORD_RETENTION_DAYS", "90"))
    
    # Exports
    EXPORT_SIEM: bool = os.getenv("EXPORT_SIEM", "false").lower() == "true"
    EXPORT_A2A: bool = os.getenv("EXPORT_A2A", "false").lower() == "true"
    EXPORT_MCP: bool = os.getenv("EXPORT_MCP", "false").lower() == "true"
    EXPORT_BLOCKCHAIN: bool = os.getenv("EXPORT_BLOCKCHAIN", "false").lower() == "true"
    
    # Secrets Management
    SECRETS_ENCRYPTION_KEY: Optional[str] = os.getenv("SECRETS_ENCRYPTION_KEY")
    
    @classmethod
    def get_storage_config(cls) -> dict:
        """Get storage configuration."""
        return {
            "type": cls.STORAGE_TYPE,
            "data_dir": cls.DATA_DIR
        }
    
    @classmethod
    def get_export_config(cls) -> dict:
        """Get export configuration."""
        return {
            "siem": cls.EXPORT_SIEM,
            "a2a": cls.EXPORT_A2A,
            "mcp": cls.EXPORT_MCP,
            "blockchain": cls.EXPORT_BLOCKCHAIN
        }