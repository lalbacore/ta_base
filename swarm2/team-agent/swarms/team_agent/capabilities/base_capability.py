"""
Base Capability - Interface for all pluggable capabilities.
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod
from datetime import datetime


class BaseCapability(ABC):
    """Base class for all capabilities."""
    
    def __init__(self):
        """Initialize capability."""
        self.metadata = self.get_metadata()
        self.created_at = datetime.now()
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return capability metadata for discovery."""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the capability with given context."""
        pass
    
    def validate_context(self, context: Dict) -> bool:
        """Validate that context has required fields."""
        required = ["mission"]
        return all(key in context for key in required)
    
    def matches(self, requirements: Dict[str, Any]) -> bool:
        """Check if this capability matches given requirements."""
        meta = self.metadata
        
        # Check type
        if requirements.get("type") and requirements["type"] != meta.get("type"):
            return False
        
        # Check domain
        if requirements.get("domain") and requirements["domain"] != meta.get("domain"):
            return False
        
        # Check specialty if specified
        if requirements.get("specialty"):
            if meta.get("specialty") != requirements["specialty"]:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize capability to dict."""
        return {
            "class": self.__class__.__name__,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }