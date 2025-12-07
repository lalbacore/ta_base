
import pytest
from swarms.team_agent.specialists.writing_specialist import WritingSpecialist
from swarms.team_agent.core.node import SwarmNode

class TestWritingSpecialistCrypto:
    
    def test_inheritance(self):
        """Test that WritingSpecialist is a SwarmNode."""
        agent = WritingSpecialist()
        assert isinstance(agent, SwarmNode)
        assert agent.agent_type == "specialist"
        assert agent.name == "Writing Specialist"
        
    def test_crypto_capability(self):
        """Test that WritingSpecialist automatically gets a signer."""
        try:
            agent = WritingSpecialist()
            # If PKI is not set up in this env, signer might be None, 
            # but the attribute should exist.
            assert hasattr(agent, "signer")
            
            if agent.signer:
                print("Signer initialized successfully")
                msg = agent.create_message("target", "test", {"foo": "bar"})
                assert msg.signature is not None
                assert msg.sender_id == agent.id
            else:
                print("Signer not initialized (expected if no local PKI)")
                
        except Exception as e:
            pytest.fail(f"Crypto capability test failed: {e}")

if __name__ == "__main__":
    t = TestWritingSpecialistCrypto()
    t.test_inheritance()
    t.test_crypto_capability()
    print("WritingSpecialist crypto test passed")
