"""
Creative Writing Capability - Generates creative content, essays, stories, and blog posts.
"""

from typing import Dict, Any
from swarms.team_agent.capabilities.base_capability import BaseCapability


class CreativeWritingCapability(BaseCapability):
    """Capability for generating creative and academic writing content."""
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return capability metadata."""
        return {
            "name": "creative_writing",
            "type": "content_generation",
            "domain": "writing",
            "domains": ["creative", "academic", "blog", "storytelling", "copywriting"],
            "formats": ["markdown", "text"],
            "description": "Helps users overcome writer's block by generating outlines, drafts, and creative content.",
            "version": "1.0.0"
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate writing content based on mission.
        
        Args:
            context: Dict with mission, architecture
        
        Returns:
            Dict with generated content
        """
        mission = context.get("mission", "")
        # Architecture might contain tone/style preferences
        architecture = context.get("architecture", "")
        
        # Determine content type based on keywords (naive implementation)
        content_type = "Content"
        if "story" in mission.lower():
            content_type = "Story"
        elif "blog" in mission.lower():
            content_type = "Blog Post"
        elif "essay" in mission.lower() or "academic" in mission.lower():
            content_type = "Essay"
            
        # Generate structured response
        content = f"""# {content_type}: Response to "{mission}"

## Brainstorming & Outline
To tackle this writing assignment and overcome writer's block, here is a structured approach:

1. **Core Theme**: {mission}
2. **Target Audience**: General readers (unless specified)
3. **Key Points**:
   - Introduction to the concept
   - Main argument or narrative arc
   - Supporting details/examples
   - Conclusion/Call to action

## Draft Content
*(Here is a draft to get you started...)*

In the realm of {mission}, one must consider the impact of... 

[...Creative generation would happen here...]

## Tips for Refinement
- Focus on active voice.
- Ensure transitions between paragraphs are smooth.
- Review for clarity and tone.
"""
        
        return {
            "content": content,
            "filename": f"{content_type.lower().replace(' ', '_')}.md",
            "artifacts": [{
                "type": "markdown",
                "name": f"{content_type} Draft",
                "filename": f"{content_type.lower().replace(' ', '_')}.md",
                "content": content,
                "summary": f"Draft content for {mission}"
            }],
            "metadata": self.metadata
        }
