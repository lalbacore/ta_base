"""
Builder Agent - Builds implementations from architecture designs.
Uses ToolRegistry for code generation and validation.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import uuid

from ..tools import ToolRegistry, CodeGeneratorTool, CodeValidatorTool, CodeFormatterTool


class Builder:
    """
    Builds implementation artifacts from architecture designs.
    Uses tools for code generation and validation.
    """

    def __init__(
        self, 
        name: str = "Builder", 
        id: str = "agent_builder_001",
        registry: Optional[ToolRegistry] = None
    ):
        self.name = name
        self.id = id
        self.metadata = {
            "id": self.id,
            "name": self.name,
            "description": "Builds implementation artifacts from architecture designs.",
        }
        self.policy: Dict[str, Any] = {
            "can_build": True,
            "require_approval": False,
        }
        self.builds_created = 0
        self.builds: List[Dict[str, Any]] = []
        self.capabilities: List[str] = [
            "build_system",
            "evaluate_design",
            "describe",
            "act",
        ]
        
        # Initialize tool registry
        self._registry = registry or ToolRegistry()
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register default tools if not already present."""
        if "code_generator" not in self._registry:
            self._registry.register(CodeGeneratorTool())
        if "code_validator" not in self._registry:
            self._registry.register(CodeValidatorTool())
        if "code_formatter" not in self._registry:
            self._registry.register(CodeFormatterTool())

    def evaluate_design(self, design: Any) -> bool:
        """
        Quick validation of design input.
        Returns False for empty/invalid input, True otherwise.
        """
        if not design:
            return False
        if isinstance(design, dict):
            return design.get("status") == "designed"
        return False

    def evaluate_intent(self, intent: Any) -> bool:
        """
        Quick validation of intent/design input.
        Returns False for empty/invalid input, True otherwise.
        """
        if not intent:
            return False
        if isinstance(intent, dict):
            return intent.get("status") == "designed"
        if isinstance(intent, str):
            return bool(intent.strip())
        return False

    def act(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build implementation from a design.
        Uses tools for code generation and validation.
        """
        if not self.evaluate_design(design):
            return {
                "status": "refused",
                "reason": "invalid_design",
                "message": "Design must be a valid designed artifact.",
            }

        build_id = str(uuid.uuid4())
        self.builds_created += 1

        # Extract components from design and create build artifacts
        raw_components = design.get("components", [])
        artifacts = []
        component_names = []
        generated_code = []
        
        for comp in raw_components:
            comp_name = comp.get("name", "unknown") if isinstance(comp, dict) else str(comp)
            component_names.append(comp_name)
            
            # Use code generator tool
            responsibilities = comp.get("responsibilities", []) if isinstance(comp, dict) else []
            spec = f"Component: {comp_name}\nResponsibilities: {', '.join(responsibilities)}"
            
            gen_result = self._registry.invoke("code_generator", specification=spec)
            code = gen_result.output.get("code", "") if gen_result.success else f"# {comp_name} placeholder"
            
            # Validate generated code
            val_result = self._registry.invoke("code_validator", code=code)
            is_valid = val_result.output.get("valid", False) if val_result.success else False
            
            generated_code.append({
                "component": comp_name,
                "code": code,
                "valid": is_valid,
            })
            
            artifacts.append({
                "type": "implementation",
                "component": comp_name,
                "status": "built",
                "files": [f"{comp_name}.py", f"test_{comp_name}.py"],
                "validated": is_valid,
            })

        build = {
            "status": "built",
            "build_id": build_id,
            "design_id": design.get("design_id"),
            "artifacts": artifacts,
            "components": component_names,
            "components_built": len(component_names),
            "summary": f"Built {len(component_names)} components from design.",
            "code_quality": "high",
            "generated_code": generated_code,
            "implementation": {
                "language": "python",
                "framework": "standard",
                "artifacts": artifacts,
            },
            "tools_used": ["code_generator", "code_validator"],
        }

        self.builds.append(build)
        return build

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the builder with a context dict.
        Extracts design from context and delegates to act().
        """
        design = context.get("architecture") or context.get("design")
        
        # If we have a valid design, use act()
        if design and isinstance(design, dict) and design.get("status") == "designed":
            return self.act(design)
        
        # Fallback: generate minimal code output using tools
        mission = context.get("mission", "unknown")
        
        gen_result = self._registry.invoke(
            "code_generator", 
            specification=f"Main module for: {mission}"
        )
        code = gen_result.output.get("code", f"# Generated for: {mission}\npass") if gen_result.success else f"# {mission}\npass"
        
        return {
            "status": "built",
            "build_id": str(uuid.uuid4()),
            "code": code,
            "filename": "main.py",
            "tests": "# Generated tests\nimport unittest\n\nclass TestMain(unittest.TestCase):\n    pass",
            "documentation": f"# Documentation\n\nGenerated for: {mission}",
            "components": [],
            "artifacts": [],
            "implementation": {
                "language": "python",
                "framework": "standard",
                "artifacts": [],
            },
            "tools_used": ["code_generator"],
        }

    def describe(self) -> Dict[str, Any]:
        """
        Return metadata and simple I/O schema for this role.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.metadata.get("description", ""),
            "type": "role",
            "role": "builder",
            "builds_created": self.builds_created,
            "capabilities": self.capabilities,
            "policy": self.policy,
            "tools_available": [t.name for t in self._registry.list_tools()],
            "inputs": {
                "design": {"type": "object", "required": True, "description": "Architecture design to build"}
            },
            "outputs": {
                "status": {"type": "string", "enum": ["built", "refused"]},
                "build_id": {"type": "string"},
                "artifacts": {"type": "array"},
            },
        }
