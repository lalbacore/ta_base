"""
Provider Registry Models - Multi-chain and multi-provider support.

Models:
- NetworkProvider: Configuration for external networks (Optimism, Filecoin, etc.)
- WalletCredential: User credentials for accessing these networks
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, Text
from app.models.base import Base, TimestampMixin

class NetworkProvider(Base, TimestampMixin):
    """
    Configuration for an external blockchain or service provider.
    
    Examples:
    - Optimism Goerli (EVM)
    - Filecoin Hyperspace (FILECOIN)
    - Local Hardhat (EVM)
    - University Research Chain (ACADEMIC)
    """
    __tablename__ = 'network_providers'

    provider_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    provider_type = Column(String, nullable=False, index=True)  # EVM, FILECOIN, SOLANA, STORAGE
    
    # Connection details
    rpc_url = Column(String, nullable=False)
    chain_id = Column(Integer)  # For EVM chains
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    meta_data = Column(JSON)  # Extra config (e.g. explorer URL, gas limits)
    
    def to_dict(self):
        return {
            'provider_id': self.provider_id,
            'name': self.name,
            'provider_type': self.provider_type,
            'rpc_url': self.rpc_url,
            'chain_id': self.chain_id,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WalletCredential(Base, TimestampMixin):
    """
    Secure storage for user wallet credentials.
    
    Allows users to bring their own keys for specific networks.
    Private keys should be encrypted at rest.
    """
    __tablename__ = 'wallet_credentials'

    wallet_id = Column(String, primary_key=True)
    user_id = Column(String, index=True)  # For future multi-user support
    
    # Wallet details
    label = Column(String)  # e.g., "Main Deployer", "Test Account"
    address = Column(String, nullable=False)
    provider_type = Column(String, nullable=False)  # Must match NetworkProvider type
    
    # Security
    encrypted_private_key = Column(Text, nullable=False)
    encryption_version = Column(String, default="v1")
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'wallet_id': self.wallet_id,
            'user_id': self.user_id,
            'label': self.label,
            'address': self.address,
            'provider_type': self.provider_type,
            # Never return private key in to_dict
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
