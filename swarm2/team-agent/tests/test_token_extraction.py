"""
Test Token Extraction from LLM Responses
"""

import pytest
from swarms.team_agent.llm.token_extractor import (
    extract_tokens_from_response,
    estimate_tokens,
    format_token_summary
)


class TestTokenExtraction:
    """Test token extraction from various LLM providers."""
    
    def test_openai_token_extraction(self):
        """Test extracting tokens from OpenAI response."""
        response = {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300
            }
        }
        
        tokens = extract_tokens_from_response(response, "openai")
        
        assert tokens['prompt'] == 100
        assert tokens['completion'] == 200
        assert tokens['total'] == 300
    
    def test_anthropic_token_extraction(self):
        """Test extracting tokens from Anthropic response."""
        response = {
            "usage": {
                "input_tokens": 150,
                "output_tokens": 250
            }
        }
        
        tokens = extract_tokens_from_response(response, "anthropic")
        
        assert tokens['prompt'] == 150
        assert tokens['completion'] == 250
        assert tokens['total'] == 400
    
    def test_missing_usage_data(self):
        """Test handling response without usage data."""
        response = {"content": "Some response"}
        
        tokens = extract_tokens_from_response(response, "openai")
        
        assert tokens['prompt'] == 0
        assert tokens['completion'] == 0
        assert tokens['total'] == 0
    
    def test_generic_provider_fallback(self):
        """Test fallback for unknown provider."""
        response = {
            "usage": {
                "total_tokens": 500
            }
        }
        
        tokens = extract_tokens_from_response(response, "unknown")
        
        assert tokens['total'] == 500
    
    def test_token_estimation(self):
        """Test rough token estimation."""
        text = "This is a test sentence with multiple words."
        
        estimated = estimate_tokens(text)
        
        # Should be roughly text length / 4
        assert estimated > 0
        assert estimated < len(text)
    
    def test_token_summary_formatting(self):
        """Test formatting token summary."""
        tokens = {"prompt": 100, "completion": 200, "total": 300}
        
        summary = format_token_summary(tokens)
        
        assert "300 tokens" in summary
        assert "100 prompt" in summary
        assert "200 completion" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
