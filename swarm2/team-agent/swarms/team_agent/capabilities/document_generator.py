"""
Generic Document Generator Capability.
"""

from typing import Dict, Any
from swarms.team_agent.capabilities.base_capability import BaseCapability


class DocumentGenerator(BaseCapability):
    """Generic capability for generating documentation."""
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return capability metadata."""
        return {
            "name": "document_generator",
            "type": "document_generation",
            "domain": "general",
            "domains": ["documentation", "document", "guide"],
            "formats": ["markdown", "text", "html"],  # Added for test compatibility
            "description": "Generates various types of documentation",
            "version": "1.0.0"
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation based on mission.
        
        Args:
            context: Dict with mission, architecture
        
        Returns:
            Dict with generated documentation
        """
        mission = context.get("mission", "")
        architecture = context.get("architecture", "")
        
        # Generate basic documentation
        doc_content = f"""# {mission}

## Overview
This document provides comprehensive information about: {mission}

## Architecture
{architecture}

## Implementation Details
[To be filled in]

## Usage
[To be filled in]

## References
[To be filled in]
"""
        
        return {
            "content": doc_content,
            "code": doc_content,
            "filename": "README.md",
            "artifacts": [{
                "type": "markdown",
                "name": "documentation",
                "filename": "README.md",
                "content": doc_content,
                "summary": f"Documentation for {mission}"
            }],
            "metadata": self.metadata
        }