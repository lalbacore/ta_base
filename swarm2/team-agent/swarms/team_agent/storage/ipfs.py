"""
IPFS Client for decentralized artifact storage.
"""
import os
import requests
from typing import Dict, Any, Optional
from app.database import get_backend_session
from app.models.provider import NetworkProvider

class IPFSClient:
    """Client for interacting with IPFS (via Pinata or Gateway)."""

    def __init__(self, provider_id: str = None):
        """
        Initialize IPFSClient with specific provider.
        
        If not provided, attempts to load defaults from DB or env (fallback).
        """
        self.gateway_url = None
        self.api_key = None
        self.secret_key = None
        self.pinata_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

        # Try Loading from DB
        try:
            with get_backend_session() as session:
                if provider_id:
                    provider = session.query(NetworkProvider).filter_by(provider_id=provider_id).first()
                else:
                    # Look for default STORAGE provider
                    provider = session.query(NetworkProvider).filter_by(provider_type="STORAGE", is_default=True).first()
                
                if provider:
                    self.gateway_url = provider.rpc_url # reusing rpc_url for gateway
                    self.api_key = provider.meta_data.get('api_key')
                    self.secret_key = provider.meta_data.get('secret_key')
                    return
        except Exception as e:
            print(f"Failed to load IPFS config from DB: {e}")

        # Fallback to Environment Variables
        print("Falling back to environment variables for IPFSClient")
        self.gateway_url = os.getenv('IPFS_GATEWAY_URL', 'https://gateway.pinata.cloud/ipfs/')
        self.api_key = os.getenv('PINATA_API_KEY')
        self.secret_key = os.getenv('PINATA_SECRET_API_KEY')

    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to IPFS.

        Returns:
            IPFS CID (Content Identifier)
        """
        if not self.api_key or not self.secret_key:
            print("IPFS credentials not configured")
            return None

        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                headers = {
                    'pinata_api_key': self.api_key,
                    'pinata_secret_api_key': self.secret_key
                }
                
                response = requests.post(
                    self.pinata_url,
                    files=files,
                    headers=headers
                )
                response.raise_for_status()
                
                return response.json()['IpfsHash']

        except Exception as e:
            print(f"Failed to upload to IPFS: {e}")
            return None

    def upload_json(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Upload JSON data to IPFS via Pinata.
        
        Args:
            data: Dictionary to upload as JSON
            
        Returns:
            IPFS CID (Content Identifier)
        """
        if not self.api_key or not self.secret_key:
            print("IPFS credentials not configured")
            return None
            
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        
        try:
            headers = {
                'pinata_api_key': self.api_key,
                'pinata_secret_api_key': self.secret_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                "pinataContent": data,
                "pinataMetadata": {
                    "name": f"workflow_artifact_{data.get('workflow_id', 'unknown')}.json"
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            return response.json()['IpfsHash']
            
        except Exception as e:
            print(f"Failed to upload JSON to IPFS: {e}")
            return None
