"""
Blockchain Client for Ethereum Optimism interactions.

Handles submitting workflows and publishing artifacts to the blockchain.
"""
import os
import json
from typing import List, Dict, Any, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account

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

class ChainClient:
    """Client for interacting with Ethereum Optimism L2."""

    def __init__(self):
        self.rpc_url = os.getenv('OPTIMISM_RPC_URL')
        self.private_key = os.getenv('AGENT_PRIVATE_KEY')
        self.conductor_address = os.getenv('WORKFLOW_CONDUCTOR_ADDRESS')
        
        if not self.rpc_url or not self.private_key:
            print("Warning: Blockchain not configured (OPTIMISM_RPC_URL or AGENT_PRIVATE_KEY missing)")
            self.w3 = None
            return

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        self.account = Account.from_key(self.private_key)
        
        if self.conductor_address:
            self.conductor = self.w3.eth.contract(
                address=self.conductor_address,
                abi=WORKFLOW_CONDUCTOR_ABI
            )
        else:
            self.conductor = None

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
