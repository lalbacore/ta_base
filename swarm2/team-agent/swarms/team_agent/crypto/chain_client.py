"""
Blockchain Client for Ethereum Optimism interactions.

Handles submitting workflows and publishing artifacts to the blockchain.
"""
import os
import json
from typing import List, Dict, Any, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from app.database import get_backend_session
from app.models.provider import NetworkProvider, WalletCredential

# Minimal ABI for WorkflowConductor
WORKFLOW_CONDUCTOR_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "mission", "type": "string"},
            {"internalType": "address[]", "name": "agents", "type": "address[]"}
        ],
        "name": "submitWorkflow",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "workflowId", "type": "bytes32"},
            {"internalType": "string", "name": "ipfsCid", "type": "string"}
        ],
        "name": "publishArtifacts",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# ABI for CapabilityMarketplace
CAPABILITY_REGISTRY_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "description", "type": "string"},
            {"internalType": "uint256", "name": "price", "type": "uint256"}
        ],
        "name": "registerCapability",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "capabilityId", "type": "bytes32"}
        ],
        "name": "hireAgent",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

class ChainClient:
    """Client for interacting with Ethereum Optimism L2."""

    def __init__(self, provider_id: str = None, wallet_id: str = None):
        """
        Initialize ChainClient with specific provider and wallet.
        
        If not provided, attempts to load defaults from DB or env (fallback).
        """
        self.w3 = None
        self.conductor = None
        self.registry = None
        self.account = None
        
        # Try Loading from DB
        try:
            with get_backend_session() as session:
                # Load Provider
                if provider_id:
                    provider = session.query(NetworkProvider).filter_by(provider_id=provider_id).first()
                else:
                    provider = session.query(NetworkProvider).filter_by(is_default=True).first()
                    
                # Load Wallet
                if wallet_id:
                    wallet = session.query(WalletCredential).filter_by(wallet_id=wallet_id).first()
                else:
                    wallet = session.query(WalletCredential).filter_by(is_default=True).first() # Assuming is_default exists or pick first
                
                if provider and wallet:
                    self._init_from_db(provider, wallet)
                    return
        except Exception as e:
            print(f"Failed to load chain config from DB: {e}")

        # Fallback to Environment Variables
        print("Falling back to environment variables for ChainClient")
        self.rpc_url = os.getenv('OPTIMISM_RPC_URL')
        self.private_key = os.getenv('AGENT_PRIVATE_KEY')
        self.conductor_address = os.getenv('WORKFLOW_CONDUCTOR_ADDRESS')
        
        if self.rpc_url and self.private_key:
            self._init_connection(self.rpc_url, self.private_key, self.conductor_address)

    def _init_from_db(self, provider, wallet):
        """Initialize connection from database models."""
        # Decrypt private key (simple strip prefix for prototype)
        private_key = wallet.encrypted_private_key
        if private_key.startswith("ENC_"):
            private_key = private_key[4:]
            
        self._init_connection(provider.rpc_url, private_key, provider.meta_data.get('conductor_address'))

    def _init_connection(self, rpc_url, private_key, conductor_address=None):
        """Common initialization logic."""
        try:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.account = Account.from_key(private_key)
            
            if conductor_address:
                self.conductor = self.w3.eth.contract(
                    address=conductor_address,
                    abi=WORKFLOW_CONDUCTOR_ABI
                )

            # Initialize CapabilityRegistry if address provided
            # For now, we can use a placeholder or check env/metadata
            registry_address = os.getenv('CAPABILITY_REGISTRY_ADDRESS')
            if registry_address:
                self.registry = self.w3.eth.contract(
                    address=registry_address,
                    abi=CAPABILITY_REGISTRY_ABI
                )
        except Exception as e:
            print(f"Failed to initialize web3 connection: {e}")

    def submit_workflow(self, mission: str, agent_addresses: List[str] = None) -> Optional[str]:
        """
        Submit a new workflow to the blockchain.
        
        Returns:
            Transaction hash as hex string
        """
        if not self.w3 or not self.conductor:
            print("Blockchain client not initialized")
            return None

        if not agent_addresses:
            agent_addresses = []

        try:
            # Build transaction
            tx = self.conductor.functions.submitWorkflow(
                mission,
                agent_addresses
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.w3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Failed to submit workflow to blockchain: {e}")
            return None

    def publish_artifacts(self, workflow_id: bytes, ipfs_cid: str) -> Optional[str]:
        """
        Publish artifacts CID to the blockchain.
        
        Returns:
            Transaction hash as hex string
        """
        if not self.w3 or not self.conductor:
            return None
            
        try:
            tx = self.conductor.functions.publishArtifacts(
                workflow_id,
                ipfs_cid
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.w3.to_hex(tx_hash)

        except Exception as e:
            print(f"Failed to publish artifacts: {e}")
            return None
<<<<<<< HEAD
    
    def hire_agent(self, capability_id: bytes, fee: int) -> Optional[str]:
        """
        Hire an agent by paying the fee on-chain.
        
        Args:
            capability_id: ID of the capability (bytes32)
            fee: Fee amount in wei
            
        Returns:
            Transaction hash as hex string
        """
        if not self.w3 or not self.registry:
            print("Capability registry not initialized")
            return None
            
        try:
            tx = self.registry.functions.hireAgent(
                capability_id
            ).build_transaction({
                'from': self.account.address,
                'value': fee,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.w3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Failed to hire agent: {e}")
            return None


    def register_capability(self, name: str, description: str, price: int) -> Optional[str]:
        """
        Register a new capability on the blockchain.
        
        Args:
            name: Capability name
            description: Capability description
            price: Price in wei
            
        Returns:
            Transaction hash as hex string
        """
        if not self.w3 or not self.registry:
            print("Capability registry not initialized")
            return None
            
        try:
            tx = self.registry.functions.registerCapability(
                name,
                description,
                price
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.w3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Failed to register capability: {e}")
            return None
