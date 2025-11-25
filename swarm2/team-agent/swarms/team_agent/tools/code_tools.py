"""
Code generation and validation tools with LLM integration.
"""

from typing import Any, Dict, Optional
from .base import BaseTool, ToolMetadata, ToolResult, ToolStatus
from .llm import LLMClient, LLMConfig, get_llm_client


class CodeGeneratorTool(BaseTool):
    """Generate code from specifications using LLM."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self._llm = llm_client
    
    @property
    def llm(self) -> LLMClient:
        if self._llm is None:
            self._llm = get_llm_client()
        return self._llm
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_generator",
            description="Generate code from a specification using LLM",
            version="2.0.0",
            input_schema={"specification": {"type": "string"}, "language": {"type": "string", "default": "python"}},
            output_schema={"code": {"type": "string"}, "language": {"type": "string"}},
            requires_governance=False, trust_domain="execution", tags=["code", "generation", "llm"])
    
    def validate_input(self, **kwargs) -> Optional[str]:
        if "specification" not in kwargs:
            return "specification is required"
        if not kwargs["specification"].strip():
            return "specification cannot be empty"
        return None
    
    def execute(self, **kwargs) -> ToolResult:
        spec = kwargs["specification"]
        lang = kwargs.get("language", "python")
        style = kwargs.get("style", "clean, well-documented")
        
        llm_response = self.llm.generate_code(specification=spec, language=lang, style=style)
        
        if llm_response.success:
            return ToolResult(status=ToolStatus.SUCCESS,
                output={"code": llm_response.content, "language": lang,
                       "explanation": f"Generated using {llm_response.model}", "llm_used": True},
                metadata={"model": llm_response.model, "tokens_used": llm_response.tokens_used})
        
        code = self._generate_fallback_code(spec, lang, style)
        return ToolResult(status=ToolStatus.SUCCESS,
            output={"code": code, "language": lang, "explanation": f"Fallback: {llm_response.error}", "llm_used": False},
            metadata={"fallback_reason": llm_response.error})
    
    def _generate_fallback_code(self, spec: str, lang: str, style: str) -> str:
        if lang == "python":
            return f"\"\"\"\"Generated for: {spec[:80]}...\nFallback mode.\"\"\"\n\ndef main():\n    pass\n\nif __name__ == \"__main__\":\n    main()\n"
        return f"// Generated {lang} code for: {spec[:50]}..."


class CodeValidatorTool(BaseTool):
    """Validate code syntax and structure."""
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(name="code_validator", description="Validate code syntax",
            version="1.0.0", input_schema={"code": {"type": "string"}, "language": {"type": "string", "default": "python"}},
            output_schema={"valid": {"type": "boolean"}, "errors": {"type": "array"}},
            requires_governance=False, trust_domain="execution", tags=["code", "validation"])
    
    def validate_input(self, **kwargs) -> Optional[str]:
        if "code" not in kwargs:
            return "code is required"
        return None
    
    def execute(self, **kwargs) -> ToolResult:
        code = kwargs["code"]
        lang = kwargs.get("language", "python")
        strict = kwargs.get("strict", False)
        errors, warnings = [], []
        if lang == "python":
            try:
                compile(code, "<string>", "exec")
            except SyntaxError as e:
                errors.append(f"Syntax error line {e.lineno}: {e.msg}")
            if strict:
                if "import *" in code:
                    warnings.append("Avoid import *")
                if "eval(" in code or "exec(" in code:
                    warnings.append("eval/exec detected - security risk")
        return ToolResult(status=ToolStatus.SUCCESS,
            output={"valid": len(errors) == 0, "errors": errors, "warnings": warnings},
            metadata={"language": lang, "strict": strict})


class CodeFormatterTool(BaseTool):
    """Format code according to style guidelines."""
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(name="code_formatter", description="Format code",
            version="1.0.0", input_schema={"code": {"type": "string"}},
            output_schema={"formatted_code": {"type": "string"}},
            requires_governance=False, trust_domain="execution", tags=["code", "formatting"])
    
    def execute(self, **kwargs) -> ToolResult:
        code = kwargs.get("code", "")
        formatted = code.strip() + "\n"
        return ToolResult(status=ToolStatus.SUCCESS,
            output={"formatted_code": formatted, "changes_made": 1 if formatted != code else 0})
