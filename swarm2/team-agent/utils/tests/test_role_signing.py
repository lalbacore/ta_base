"""
Tests for role signing implementations (Critic, Recorder, Governance).

Tests that all roles properly sign their outputs when provided with
certificate chains.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from swarms.team_agent.crypto import PKIManager, TrustDomain, Verifier
from swarms.team_agent.roles import Critic, Recorder, Governance


class TestCriticSigning(unittest.TestCase):
    """Test Critic role signing."""

    def setUp(self):
        """Set up PKI and cert chains."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)
        self.pki.initialize_pki()

        self.exec_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        self.verifier = Verifier(chain_pem=self.exec_chain['chain'])

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_critic_signs_output(self):
        """Test that Critic signs its review output."""
        critic = Critic(
            workflow_id="test_wf",
            cert_chain=self.exec_chain
        )

        # Create test payload
        payload = {
            "design": {
                "status": "designed",
                "components": [{"name": "frontend"}, {"name": "backend"}]
            },
            "build": {
                "status": "built",
                "code": "def test(): pass",
                "artifacts": [{"name": "test.py"}]
            }
        }

        result = critic.act(payload)

        # Check that signature exists
        self.assertIn('_signature', result)
        self.assertEqual(result['_signature']['signer'], 'critic')

        # Verify signature
        self.assertTrue(self.verifier.verify_dict(result))

    def test_critic_output_integrity(self):
        """Test that signed output can't be tampered with."""
        critic = Critic(
            workflow_id="test_wf",
            cert_chain=self.exec_chain
        )

        payload = {
            "design": {"status": "designed"},
            "build": {"status": "built"}
        }

        result = critic.act(payload)

        # Original should verify
        self.assertTrue(self.verifier.verify_dict(result))

        # Tampered version should fail
        result['score'] = 0.99
        self.assertFalse(self.verifier.verify_dict(result))


class TestRecorderSigning(unittest.TestCase):
    """Test Recorder role signing."""

    def setUp(self):
        """Set up PKI and cert chains."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)
        self.pki.initialize_pki()

        self.log_chain = self.pki.get_certificate_chain(TrustDomain.LOGGING)
        self.verifier = Verifier(chain_pem=self.log_chain['chain'])

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_recorder_signs_output(self):
        """Test that Recorder signs its record output."""
        recorder = Recorder(
            workflow_id="test_wf",
            cert_chain=self.log_chain
        )

        payload = {
            "request": "test mission",
            "design": {"status": "designed"},
            "build": {"status": "built"},
            "review": {"status": "reviewed", "score": 0.85},
            "governance": {"status": "enforced", "allowed": True, "composite_score": 0.9}
        }

        result = recorder.act(payload)

        # Check that signature exists
        self.assertIn('_signature', result)
        self.assertEqual(result['_signature']['signer'], 'recorder')

        # Verify signature
        self.assertTrue(self.verifier.verify_dict(result))

    def test_recorder_artifact_integrity(self):
        """Test that recorded artifacts maintain integrity."""
        recorder = Recorder(
            workflow_id="test_wf",
            cert_chain=self.log_chain
        )

        payload = {
            "design": {"status": "designed"},
            "build": {"status": "built"},
            "review": {"status": "reviewed", "score": 0.8},
            "governance": {"status": "enforced", "allowed": True}
        }

        result = recorder.act(payload)

        # Check that composite score is preserved
        original_score = result['composite_score']['overall']

        # Verify original
        self.assertTrue(self.verifier.verify_dict(result))

        # Tampering with score should fail verification
        result['composite_score']['overall'] = 100.0
        self.assertFalse(self.verifier.verify_dict(result))


class TestGovernanceSigning(unittest.TestCase):
    """Test Governance role signing."""

    def setUp(self):
        """Set up PKI and cert chains."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)
        self.pki.initialize_pki()

        self.gov_chain = self.pki.get_certificate_chain(TrustDomain.GOVERNMENT)
        self.verifier = Verifier(chain_pem=self.gov_chain['chain'])

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_governance_signs_output(self):
        """Test that Governance signs its policy decision."""
        governance = Governance(
            workflow_id="test_wf",
            cert_chain=self.gov_chain
        )

        review = {
            "status": "reviewed",
            "score": 0.85,
            "risks": []
        }

        result = governance.act(review)

        # Check that signature exists
        self.assertIn('_signature', result)
        self.assertEqual(result['_signature']['signer'], 'governance')

        # Verify signature
        self.assertTrue(self.verifier.verify_dict(result))

    def test_governance_decision_integrity(self):
        """Test that governance decisions can't be altered."""
        governance = Governance(
            workflow_id="test_wf",
            cert_chain=self.gov_chain
        )

        review = {
            "status": "reviewed",
            "score": 0.4,  # Below threshold
            "risks": [{"level": "high", "description": "Security issue"}]
        }

        result = governance.act(review)

        # Original decision should be "not allowed"
        self.assertFalse(result['allowed'])

        # Verify original
        self.assertTrue(self.verifier.verify_dict(result))

        # Tampering with decision should fail verification
        result['allowed'] = True
        self.assertFalse(self.verifier.verify_dict(result))


class TestRoleSigningWithoutCerts(unittest.TestCase):
    """Test that roles work without certificates."""

    def test_critic_without_cert_chain(self):
        """Test Critic works without cert chain."""
        critic = Critic(workflow_id="test_wf")

        payload = {
            "design": {"status": "designed"},
            "build": {"status": "built"}
        }

        result = critic.act(payload)

        # Should work, but not have signature
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'reviewed')

    def test_recorder_without_cert_chain(self):
        """Test Recorder works without cert chain."""
        recorder = Recorder(workflow_id="test_wf")

        payload = {
            "design": {"status": "designed"},
            "build": {"status": "built"},
            "review": {"status": "reviewed", "score": 0.8},
            "governance": {"status": "enforced", "allowed": True}
        }

        result = recorder.act(payload)

        # Should work, but not have signature
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'recorded')

    def test_governance_without_cert_chain(self):
        """Test Governance works without cert chain."""
        governance = Governance(workflow_id="test_wf")

        review = {"status": "reviewed", "score": 0.8, "risks": []}

        result = governance.act(review)

        # Should work, but not have signature
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'enforced')


if __name__ == "__main__":
    unittest.main()
