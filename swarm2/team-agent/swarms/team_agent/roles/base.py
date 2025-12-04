"""
Base Role - Foundation for all agent roles.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.logging import get_logger

# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None
    x509 = None
    default_backend = None


class CertificateRevokedException(Exception):
    """Raised when attempting to use a revoked certificate."""
    pass


class BaseRole:
    """Base class for all agent roles with cryptographic signing support."""

    def __init__(
        self,
        workflow_id: str,
        cert_chain: Optional[Dict[str, bytes]] = None,
        crl_manager: Optional['CRLManager'] = None
    ):
        """
        Initialize base role with workflow ID and optional cert chain.

        Args:
            workflow_id: Current workflow identifier
            cert_chain: Optional certificate chain dict with 'key', 'cert', 'chain'
            crl_manager: Optional CRLManager for revocation checking

        Raises:
            CertificateRevokedException: If certificate is revoked
        """
        self.workflow_id = workflow_id
        self.role_name = self.__class__.__name__.lower()
        self.logger = get_logger(f"team_agent.{self.role_name}")

        # Initialize signer if cert_chain is provided
        self.signer = None
        if cert_chain and CRYPTO_AVAILABLE:
            try:
                # Check revocation status if CRL manager is provided
                if crl_manager:
                    # Extract serial number from certificate
                    cert = x509.load_pem_x509_certificate(
                        cert_chain['cert'],
                        backend=default_backend()
                    )
                    serial_hex = format(cert.serial_number, 'x')

                    if crl_manager.is_revoked(serial_hex):
                        raise CertificateRevokedException(
                            f"Certificate {serial_hex} has been revoked"
                        )

                self.signer = Signer(
                    private_key_pem=cert_chain['key'],
                    certificate_pem=cert_chain['cert'],
                    signer_id=self.role_name
                )
                self.logger.info(f"Initialized with cryptographic signing")
            except CertificateRevokedException:
                # Re-raise revocation exceptions
                raise
            except Exception as e:
                self.logger.warning(f"Failed to initialize signer: {e}")
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the role's primary function."""
        raise NotImplementedError("Subclasses must implement run()")

    def _sign_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign output if signer is available.

        Args:
            output: Output dict to sign

        Returns:
            Signed output dict
        """
        if self.signer and CRYPTO_AVAILABLE:
            return self.signer.sign_dict(output)
        return output