"""
Code generation and validation tools.
"""

from typing import Any, Dict, Optional
from .base import BaseTool, ToolMetadata, ToolResult, ToolStatus


class CodeGeneratorTool(BaseTool):
    """Generate code from specifications."""
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_generator",
            description="Generate code from a specification or description",
            version="1.0.0",
            input_schema={
                "specification": {"type": "string", "description": "Code specification"},
                "language": {"type": "string", "default": "python"},
                "style": {"type": "string", "default": "standard"}
            },
            output_schema={
                "code": {"type": "string"},
                "language": {"type": "string"},
                "explanation": {"type": "string"}
            },
            requires_governance=False,
            trust_domain="execution",
            tags=["code", "generation", "builder"]
        )
    
    def validate_input(self, **kwargs) -> Optional[str]:
        if "specification" not in kwargs:
            return "specification is required"
        if not kwargs["specification"].strip():
            return "specification cannot be empty"
        return None
    
    def execute(self, **kwargs) -> ToolResult:
        specification = kwargs["specification"]
        language = kwargs.get("language", "python")
        style = kwargs.get("style", "standard")
        
        # TODO: Replace with LLM call
        code = self._generate_mock_code(specification, language, style)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={
                "code": code,
                "language": language,
                "explanation": f"Generated {language} code for: {specification[:50]}..."
            },
            metadata={"lines": len(code.split("\n")), "style": style}
        )
    
    def _generate_mock_code(self, spec: str, language: str, style: str) -> str:
        """Mock code generation - will be replaced with LLM."""
        if language == "python":
            return f'"""\nGenerated code for: {spec[:50]}...\nStyle: {style}\n"""\n\ndef main():\n    # TODO: Implement based on specification\n    print("Implementation pending")\n    \nif __name__ == "__main__":\n    main()\n'
        return f"// Generated {language} code for: {spec[:50]}...\n// TODO: Implement"


class CodeValidatorTool(BaseTool):
    """Validate code syntax and structure."""
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_validator",
            description="Validate code syntax and check for common issues",
            version="1.0.0",
            input_schema={
                "code": {"type": "string", "description": "Code to validate"},
                "language": {"type": "string", "default": "python"},
                "strict": {"type": "boolean", "default": False}
            },
            output_schema={
                "valid": {"type": "boolean"},
                "errors": {"type": "array"},
                "warnings": {"type": "array"}
            },
            requires_governance=False,
            trust_domain="execution",
            tags=["code", "validation", "critic"]
        )
    
    def validate_input(self, **kwargs) -> Optional[str]:
        if "code" not in kwargs:
            return "code is required"
        return None
    
    def execute(self, **kwargs) -> ToolResult:
        code = kwargs["code"]
        language = kwargs.get("language", "python")
        strict = kwargs.get("strict", False)
        
        errors = []
        warnings = []
        
        if language == "python":
            try:
                compile(code, "<string>", "exec")
            except SyntaxError as e:
                errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            
            if strict:
                if "import *" in code:
                    warnings.append("Avoid 'import *' - use explicit imports")
                if "eval(" in code or "exec(" in code:
                    warnings.append("Use of eval/exec detected - potential security risk")
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={"valid": len(errors) == 0, "errors": errors, "warnings": warnings},
            metadata={"language": language, "strict": strict}
        )


class CodeFormatterTool(BaseTool):
    """Format code according to style guidelines."""
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_formatter",
            description="Format code according to language style guidelines",
            version="1.0.0",
            input_schema={
                "code": {"type": "string"},
                "language": {"type": "string", "default": "python"},
                "style_guide": {"type": "string", "default": "pep8"}
            },
            output_schema={
                "formatted_code": {"type": "string"},
                "changes_made": {"type": "integer"}
            },
            requires_governance=False,
            trust_domain="execution",
            tags=["code", "formatting", "builder"]
        )
    
    def execute(self, **kwargs) -> ToolResult:
        code = kwargs.get("code", "")
        formatted = code.strip() + "\n"
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={"formatted_code": formatted, "changes_made": 1 if formatted != code else 0}
        )
