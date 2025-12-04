"""
Base Role - Abstract base class for all agent roles.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from utils.logging import get_logger

# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None


class BaseRole(ABC):
    """Abstract base class for agent roles with cryptographic signing."""

    def __init__(
        self,
        workflow_id: str = "unknown",
        cert_chain: Optional[Dict[str, bytes]] = None
    ):
        """
        Initialize base role.

        Args:
            workflow_id: Current workflow identifier
            cert_chain: Optional certificate chain dict with 'key', 'cert', 'chain'
        """
        self.workflow_id = workflow_id
        self.logger = get_logger(f"team_agent.{self.__class__.__name__.lower()}")

        # Initialize signer if cert_chain is provided
        self.signer = None
        if cert_chain and CRYPTO_AVAILABLE:
            try:
                self.signer = Signer(
                    private_key_pem=cert_chain['key'],
                    certificate_pem=cert_chain['cert'],
                    signer_id=self.__class__.__name__.lower()
                )
                self.logger.info(f"Initialized with cryptographic signing")
            except Exception as e:
                self.logger.warning(f"Failed to initialize signer: {e}")
    
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the role's logic.
        
        Args:
            context: Input context dict
        
        Returns:
            Result dict
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    def _log_stage_start(self, stage: str, input_data: Any):
        """Log stage start."""
        self.logger.info(
            f"Starting stage: {stage}",
            extra={
                "stage": stage,
                "event": "stage_start",
                "input_size": len(str(input_data))
            }
        )
    
    def _log_stage_complete(self, stage: str, output: Any, start_time: float):
        """Log stage completion."""
        duration = time.time() - start_time
        self.logger.info(
            f"Completed stage: {stage}",
            extra={
                "stage": stage,
                "event": "stage_complete",
                "output_size": len(str(output)),
                "duration_seconds": round(duration, 2)
            }
        )
    
    def _extract_input(self, context: Dict[str, Any]) -> str:
        """Extract input string from context."""
        if isinstance(context, str):
            return context

        return context.get("input", context.get("mission", ""))

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