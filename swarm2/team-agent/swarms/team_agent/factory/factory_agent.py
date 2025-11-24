"""
Factory Agent - Creates new agents and capabilities.
"""

from typing import Dict, Any
from pathlib import Path


class FactoryAgent:
    """Agent that creates other agents and capabilities."""
    
    def create_capability(self, spec: Dict[str, Any]) -> Any:
        """Create a new capability based on specification."""
        cap_type = spec.get("type")
        
        if cap_type == "document_generation":
            return self._create_document_capability(spec)
        elif cap_type == "code_generation":
            return self._create_code_capability(spec)
        else:
            return self._create_generic_capability(spec)
    
    def _create_document_capability(self, spec: Dict) -> Any:
        """Create a new document generation capability."""
        # Generate Python code for new capability
        code = self._generate_capability_code(spec)
        
        # Save to capabilities directory
        self._save_capability(code, spec)
        
        # Import and return instance
        return self._instantiate_capability(spec)
    
    def _generate_capability_code(self, spec: Dict) -> str:
        """Generate Python code for capability using LLM."""
        prompt = f"""
Generate a Python capability class that:
- Extends BaseCapability
- Implements {spec['type']}
- Handles {spec.get('domain', 'general')} domain
- Outputs {spec.get('format', 'text')} format

Spec: {spec}
"""
        # Call LLM to generate code
        return generated_code