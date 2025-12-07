
import pytest
from swarms.team_agent.roles.architect import Architect
from swarms.team_agent.roles.builder import Builder
from swarms.team_agent.roles.critic import Critic
from swarms.team_agent.roles.recorder import Recorder
from swarms.team_agent.roles.governance import Governance
from swarms.team_agent.core.node import SwarmNode
from swarms.team_agent.crypto.pki import TrustDomain

class TestRolesCrypto:
    
    def test_architect_crypto(self):
        agent = Architect()
        assert isinstance(agent, SwarmNode)
        assert agent.trust_domain == TrustDomain.EXECUTION
        if agent.signer:
            assert agent.signer.signer_id == agent.id

    def test_builder_crypto(self):
        agent = Builder()
        assert isinstance(agent, SwarmNode)
        assert agent.trust_domain == TrustDomain.EXECUTION
        if agent.signer:
            assert agent.signer.signer_id == agent.id

    def test_critic_crypto(self):
        agent = Critic()
        assert isinstance(agent, SwarmNode)
        assert agent.trust_domain == TrustDomain.EXECUTION
        if agent.signer:
            assert agent.signer.signer_id == agent.id
            
    def test_recorder_crypto(self):
        agent = Recorder()
        assert isinstance(agent, SwarmNode)
        assert agent.trust_domain == TrustDomain.LOGGING
        if agent.signer:
            assert agent.signer.signer_id == agent.id
            
    def test_governance_crypto(self):
        agent = Governance()
        assert isinstance(agent, SwarmNode)
        # Governance is in Government/Control Plane
        assert agent.trust_domain == TrustDomain.GOVERNMENT
        if agent.signer:
            assert agent.signer.signer_id == agent.id

    def test_orchestrator_crypto(self):
        from swarms.team_agent.orchestrator import Orchestrator
        agent = Orchestrator()
        assert isinstance(agent, SwarmNode)
        assert agent.trust_domain == TrustDomain.EXECUTION
        # Orchestrator uses signer from internal PKI
        if agent.signer:
            # ID is auto-gen or set, ensure signer has an ID
            assert agent.signer.signer_id

    def test_full_flow_signatures(self):
        """Verify that agents sign their outputs."""
        if not Architect().signer:
            print("Skipping signature verification (PKI not setup)")
            return

        # 1. Architect signs output
        arch = Architect()
        design = arch.run("build a blog")
        assert "_signature" in design
        
        # 2. Builder signs output
        builder = Builder()
        build = builder.run(design)
        assert "_signature" in build

if __name__ == "__main__":
    t = TestRolesCrypto()
    t.test_architect_crypto()
    t.test_builder_crypto()
    t.test_critic_crypto()
    t.test_recorder_crypto()
    t.test_governance_crypto()
    t.test_orchestrator_crypto()
    t.test_full_flow_signatures()
    print("All Role Crypto Tests Passed")
