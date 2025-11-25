"""
LLM client wrapper for tool integration.
"""

import os
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 30.0
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    success: bool = True
    error: Optional[str] = None
    
    @property
    def tokens_used(self) -> int:
        return self.usage.get("total_tokens", 0)


class LLMClient:
    """Wrapper for LLM API calls."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._client: Optional[OpenAI] = None
        self._initialized = False
    
    def _ensure_client(self) -> bool:
        if self._initialized:
            return self._client is not None
        self._initialized = True
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not installed")
            return False
        if not self.config.api_key:
            logger.warning("OPENAI_API_KEY not set")
            return False
        try:
            kwargs = {"api_key": self.config.api_key}
            if self.config.base_url:
                kwargs["base_url"] = self.config.base_url
            self._client = OpenAI(**kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> LLMResponse:
        if not self._ensure_client():
            return LLMResponse(content="", model=self.config.model, success=False,
                             error="LLM client not available. Check API key and openai package.")
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self._client.chat.completions.create(
                model=self.config.model, messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens)
            choice = response.choices[0]
            return LLMResponse(content=choice.message.content or "", model=response.model,
                             usage={"prompt_tokens": response.usage.prompt_tokens,
                                   "completion_tokens": response.usage.completion_tokens,
                                   "total_tokens": response.usage.total_tokens},
                             finish_reason=choice.finish_reason or "stop", success=True)
        except Exception as e:
            logger.exception("LLM completion failed")
            return LLMResponse(content="", model=self.config.model, success=False, error=str(e))
    
    def generate_code(self, specification: str, language: str = "python",
                      style: str = "clean, well-documented") -> LLMResponse:
        system_prompt = f"You are an expert {language} programmer. Generate clean, production-ready code. Return ONLY code, no markdown."
        prompt = f"Generate {language} code for: {specification}\nStyle: {style}\nInclude type hints and docstrings."
        return self.complete(prompt, system_prompt=system_prompt, temperature=0.3)
    
    def review_code(self, code: str, criteria: Optional[List[str]] = None) -> LLMResponse:
        criteria = criteria or ["security", "quality", "maintainability"]
        system_prompt = "You are an expert code reviewer. Provide structured JSON feedback."
        prompt = f"Review this code for: {', '.join(criteria)}\n\n{code}\n\nReturn JSON with overall_score, issues, suggestions, summary."
        return self.complete(prompt, system_prompt=system_prompt, temperature=0.2)


_default_client: Optional[LLMClient] = None

def get_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    global _default_client
    if config is not None:
        return LLMClient(config)
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client
