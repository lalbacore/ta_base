"""Tests for LLM integration."""
import pytest
from unittest.mock import patch, MagicMock
import os
from swarms.team_agent.tools import LLMClient, LLMConfig, LLMResponse, CodeGeneratorTool

class TestLLMConfig:
    def test_default_config(self):
        config = LLMConfig()
        assert config.model == "gpt-4o-mini"
    
    def test_api_key_from_env(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            config = LLMConfig()
            assert config.api_key == "test-key"

class TestLLMResponse:
    def test_tokens_used(self):
        r = LLMResponse(content="x", model="m", usage={"total_tokens": 100}, success=True)
        assert r.tokens_used == 100

class TestCodeGeneratorWithLLM:
    def test_fallback_without_llm(self):
        tool = CodeGeneratorTool()
        tool._llm = LLMClient(LLMConfig(api_key=None))
        result = tool(specification="Add two numbers")
        assert result.success
        assert result.output["llm_used"] is False
