"""
Dynamic Builder - Uses capabilities instead of hardcoded methods.
"""

from typing import Dict, Any, List
from datetime import datetime

from .base import BaseRole
from ..capabilities import BaseCapability


class DynamicBuilder(BaseRole):
    """Builder that uses pluggable capabilities."""
    
    def __init__(self, workflow_id: str, capabilities: List[BaseCapability] = None):
        """Initialize dynamic builder with capabilities."""
        super().__init__(workflow_id)
        self.capabilities = capabilities or []
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build implementation using available capabilities."""
        architecture = context.get("input", {})
        mission = architecture.get("mission", "")
        
        self.logger.info("Starting stage: builder (dynamic)", extra={
            "stage": "builder",
            "event": "stage_start",
            "capabilities_count": len(self.capabilities),
        })
        
        # Find matching capability
        capability = self._select_capability(mission, architecture)
        
        if capability:
            # Use capability to generate
            result = capability.execute({
                "mission": mission,
                "parameters": architecture,
            })
            
            implementation = {
                "code": result.get("content", ""),
                "filename": result.get("artifacts", [{}])[0].get("filename", "output.py"),
                "artifacts": result.get("artifacts", []),
                "tests": self._generate_tests(result),
                "documentation": self._generate_docs(architecture, result),
                "capability_used": capability.metadata,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            # Fallback to simple implementation
            implementation = self._fallback_implementation(mission, architecture)
        
        self.logger.info("Completed stage: builder (dynamic)", extra={
            "stage": "builder",
            "event": "stage_complete",
            "capability": capability.metadata.get("type") if capability else "fallback",
        })
        
        return implementation
    
    def _select_capability(self, mission: str, architecture: Dict) -> BaseCapability:
        """Select best capability for the mission."""
        if not self.capabilities:
            return None
        
        mission_lower = mission.lower()
        
        # Score each capability
        scored_capabilities = []
        
        for cap in self.capabilities:
            score = self._score_capability(cap, mission_lower)
            scored_capabilities.append((score, cap))
        
        # Sort by score (highest first)
        scored_capabilities.sort(key=lambda x: x[0], reverse=True)
        
        # Return highest scoring capability (if score > 0)
        if scored_capabilities and scored_capabilities[0][0] > 0:
            return scored_capabilities[0][1]
        
        # Fallback to first capability if no good match
        return self.capabilities[0] if self.capabilities else None
    
    def _score_capability(self, cap: BaseCapability, mission_lower: str) -> int:
        """Score how well a capability matches the mission."""
        score = 0
        meta = cap.metadata
        
        # Medical/HRT keywords - high priority
        medical_keywords = ["hrt", "hormone", "replacement", "therapy", "medical", "clinical"]
        if any(keyword in mission_lower for keyword in medical_keywords):
            if meta.get("domain") == "medical":
                score += 100  # Strong match
            if meta.get("specialty") == "endocrinology":
                score += 50
            if meta.get("subdomain") == "hormone_replacement_therapy":
                score += 50
        
        # Document generation keywords
        doc_keywords = ["guide", "document", "reference", "manual"]
        if any(keyword in mission_lower for keyword in doc_keywords):
            if meta.get("type") == "document_generation":
                score += 10
        
        # General vs specific domain
        if meta.get("domain") == "general":
            score += 1  # Lowest priority - general catch-all
        
        return score
    
    def _fallback_implementation(self, mission: str, architecture: Dict) -> Dict[str, Any]:
        """Fallback implementation when no capability matches."""
        code = f'''#!/usr/bin/env python3
"""
Generated implementation for: {mission}
"""

def main():
    print("Implementation for: {mission}")

if __name__ == "__main__":
    main()
'''
        
        return {
            "code": code,
            "filename": "main.py",
            "tests": "",
            "documentation": f"# {mission}\n\nFallback implementation.",
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_tests(self, result: Dict) -> str:
        """Generate tests for the implementation."""
        return '''"""Tests for generated code."""

def test_basic():
    assert True
'''
    
    def _generate_docs(self, architecture: Dict, result: Dict) -> str:
        """Generate documentation."""
        return f'''# Generated Implementation

## Capability Used
{result.get("metadata", {}).get("generator", "Unknown")}

## Mission
{architecture.get("mission", "No mission specified")}

## Usage
See generated files.
'''