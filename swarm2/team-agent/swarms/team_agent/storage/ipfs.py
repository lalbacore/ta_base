"""
IPFS Client for decentralized artifact storage.
"""
import os
import requests
from typing import Dict, Any, Optional

class IPFSClient:
    """Client for interacting with IPFS (via Pinata or Gateway)."""

    def __init__(self):
        self.gateway_url = os.getenv('IPFS_GATEWAY_URL', 'https://gateway.pinata.cloud/ipfs/')
        self.api_key = os.getenv('PINATA_API_KEY')
        self.secret_key = os.getenv('PINATA_SECRET_API_KEY')
        self.pinata_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

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
        """Upload JSON data to IPFS."""
        # TODO: Implement JSON pinning
        pass
