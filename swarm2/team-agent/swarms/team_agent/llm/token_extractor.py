"""
Token Extractor - Extract token usage from LLM API responses

Supports multiple LLM providers:
- OpenAI (GPT-3.5, GPT-4, etc.)
- Anthropic (Claude)
- Local models (fallback)
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def extract_tokens_from_response(
    response: Dict,
    provider: str = "openai"
) -> Dict[str, int]:
    """
    Extract token usage from LLM API response.
    
    Args:
        response: LLM API response dictionary
        provider: LLM provider name (openai, anthropic, local)
        
    Returns:
        Dictionary with prompt, completion, and total tokens
        
    Example:
        >>> response = {"usage": {"prompt_tokens": 100, "completion_tokens": 200}}
        >>> extract_tokens_from_response(response, "openai")
        {'prompt': 100, 'completion': 200, 'total': 300}
    """
    try:
        if provider.lower() == "openai":
            return _extract_openai_tokens(response)
        elif provider.lower() == "anthropic":
            return _extract_anthropic_tokens(response)
        else:
            # Fallback for unknown providers
            return _extract_generic_tokens(response)
    except Exception as e:
        logger.warning(f"Failed to extract tokens from {provider} response: {e}")
        return {"prompt": 0, "completion": 0, "total": 0}


def _extract_openai_tokens(response: Dict) -> Dict[str, int]:
    """Extract tokens from OpenAI API response."""
    usage = response.get("usage", {})
    
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
    
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": total_tokens
    }


def _extract_anthropic_tokens(response: Dict) -> Dict[str, int]:
    """Extract tokens from Anthropic API response."""
    usage = response.get("usage", {})
    
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    
    return {
        "prompt": input_tokens,
        "completion": output_tokens,
        "total": input_tokens + output_tokens
    }


def _extract_generic_tokens(response: Dict) -> Dict[str, int]:
    """
    Attempt to extract tokens from unknown provider.
    Tries common field names.
    """
    # Try common patterns
    if "usage" in response:
        usage = response["usage"]
        
        # Try OpenAI-style
        if "prompt_tokens" in usage:
            return _extract_openai_tokens(response)
        
        # Try Anthropic-style
        if "input_tokens" in usage:
            return _extract_anthropic_tokens(response)
        
        # Try generic total
        if "total_tokens" in usage:
            return {
                "prompt": 0,
                "completion": 0,
                "total": usage["total_tokens"]
            }
    
    # No tokens found
    logger.debug("No token usage found in response")
    return {"prompt": 0, "completion": 0, "total": 0}


def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Estimate token count for text using tiktoken.
    
    Args:
        text: Input text
        model: Model name for tokenization rules
        
    Returns:
        Estimated token count
        
    Note:
        Uses tiktoken for accurate counting when available.
        Falls back to rough estimation (4 chars/token) if tiktoken unavailable.
    """
    if not text:
        return 0
    
    try:
        import tiktoken
        
        # Get encoding for model
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base (GPT-4, GPT-3.5-turbo)
            encoding = tiktoken.get_encoding("cl100k_base")
        
        # Count tokens
        return len(encoding.encode(text))
        
    except ImportError:
        # tiktoken not available, use rough estimation
        logger.debug("tiktoken not available, using rough estimation")
        return len(text) // 4


def format_token_summary(tokens: Dict[str, int]) -> str:
    """
    Format token usage as human-readable string.
    
    Args:
        tokens: Token dictionary from extract_tokens_from_response
        
    Returns:
        Formatted string like "300 tokens (100 prompt + 200 completion)"
    """
    return (
        f"{tokens['total']:,} tokens "
        f"({tokens['prompt']:,} prompt + {tokens['completion']:,} completion)"
    )
