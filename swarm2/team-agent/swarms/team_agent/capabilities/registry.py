"""
Capability Registry - Central discovery and management.
"""
from typing import Dict, Any, List, Optional


class CapabilityRegistry:
    """Registry for managing and discovering capabilities."""
    
    def __init__(self):
        """Initialize empty registry."""
        self._capabilities: Dict[str, Any] = {}
        self._by_type: Dict[str, List[str]] = {}
        self._by_domain: Dict[str, List[str]] = {}
    
    @property
    def capabilities(self) -> List[Any]:
        """Return capabilities as a list (for test compatibility)."""
        return list(self._capabilities.values())
    
    def register(self, capability) -> None:
        """Register a new capability."""
        # Get metadata - handle both objects and dicts, and test mocks
        meta = None
        if hasattr(capability, 'get_metadata'):
            meta = capability.get_metadata()
        elif hasattr(capability, 'metadata'):
            meta = capability.metadata
        elif isinstance(capability, dict):
            meta = capability.get('metadata', capability)  # Allow dict to BE metadata
        
        if not meta:
            meta = {}
        
        # For test mocks, check if capability itself has name/type/domain attributes
        name = meta.get('name')
        if not name and hasattr(capability, 'name'):
            name = capability.name
            meta['name'] = name
        
        # Generate fallback name from type or class name
        if not name:
            if hasattr(capability, 'type'):
                name = f"{capability.type}_capability"
            elif hasattr(capability, '__class__'):
                name = capability.__class__.__name__.lower()
            else:
                name = f"capability_{id(capability)}"
            meta['name'] = name
        
        self._capabilities[name] = capability
        
        # Index by type
        cap_type = meta.get('type')
        if not cap_type and hasattr(capability, 'type'):
            cap_type = capability.type
        
        if cap_type:
            if cap_type not in self._by_type:
                self._by_type[cap_type] = []
            self._by_type[cap_type].append(name)
        
        # Index by domains
        domains = meta.get('domains', [])
        domain = meta.get('domain')
        
        # Check for attributes on capability object (for mocks)
        if not domains and hasattr(capability, 'domains'):
            domains = capability.domains
        if not domain and hasattr(capability, 'domain'):
            domain = capability.domain
        
        if domain and domain not in domains:
            domains = list(domains) + [domain]
        
        for d in domains:
            if d not in self._by_domain:
                self._by_domain[d] = []
            self._by_domain[d].append(name)
    
    def get_by_type(self, cap_type: str) -> List[Any]:
        """Get all capabilities of a given type."""
        names = self._by_type.get(cap_type, [])
        return [self._capabilities[name] for name in names]
    
    def get_by_domain(self, domain: str) -> List[Any]:
        """Get all capabilities in a domain."""
        names = self._by_domain.get(domain, [])
        return [self._capabilities[name] for name in names]
    
    def find(self, query) -> Optional[Any]:
        """
        Find capability matching query.
        
        Args:
            query: Either a string (keyword search) or dict (requirements matching)
        """
        # Handle string query (keyword search)
        if isinstance(query, str):
            query_lower = query.lower()
            
            for cap in self._capabilities.values():
                meta = self._get_meta(cap)
                domains = meta.get('domains', [])
                
                # Match domain keywords
                if any(domain.lower() in query_lower for domain in domains):
                    return cap
                
                # Match capability name
                name = meta.get('name', '')
                if name and name.lower() in query_lower:
                    return cap
            
            return None
        
        # Handle dict query (requirements matching)
        if isinstance(query, dict):
            for cap in self._capabilities.values():
                if hasattr(cap, 'matches') and cap.matches(query):
                    return cap
            return None
        
        return None
    
    def find_all(self, requirements: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Find all capabilities matching requirements."""
        if requirements is None:
            return list(self._capabilities.values())
        
        matches = []
        for cap in self._capabilities.values():
            if hasattr(cap, 'matches') and cap.matches(requirements):
                matches.append(cap)
        
        return matches
    
    def list_capabilities(self) -> List[Dict[str, Any]]:
        """List all registered capabilities as dicts with metadata."""
        result = []
        for cap in self._capabilities.values():
            if isinstance(cap, dict):
                # Already a dict, ensure it has "class" key
                if "class" not in cap:
                    cap["class"] = cap.get("metadata", {}).get("type", "unknown")
                result.append(cap)
            else:
                # Wrap object with metadata and class keys
                meta = self._get_meta(cap)
                class_name = cap.__class__.__name__ if hasattr(cap, '__class__') else "unknown"
                result.append({
                    "capability": cap,
                    "metadata": meta,
                    "class": class_name
                })
        return result
    
    def get(self, name: str) -> Optional[Any]:
        """Get capability by exact name."""
        return self._capabilities.get(name)
    
    def clear(self) -> None:
        """Clear all registered capabilities."""
        self._capabilities.clear()
        self._by_type.clear()
        self._by_domain.clear()
    
    def _get_meta(self, cap) -> Dict[str, Any]:
        """Helper to extract metadata from capability."""
        if hasattr(cap, 'get_metadata'):
            return cap.get_metadata()
        if hasattr(cap, 'metadata'):
            return cap.metadata
        if isinstance(cap, dict):
            return cap.get('metadata', cap)
        return {}