"""
Comprehensive tests for PKI (Public Key Infrastructure) system.

Tests certificate generation, signing, verification, and integration
with the orchestrator and roles.
"""

import os
import sys
import unittest
import json
import tempfile
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from swarms.team_agent.crypto import PKIManager, TrustDomain, Signer, Verifier
from swarms.team_agent.state.turing_tape import TuringTape


class TestPKIManager(unittest.TestCase):
    """Test PKI manager and certificate generation."""

    def setUp(self):
        """Create temporary directory for PKI files."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_pki_initialization(self):
        """Test PKI infrastructure initialization."""
        self.pki.initialize_pki()

        # Check root CA was created
        root_key = self.temp_dir / "root" / "root-ca.key"
        root_cert = self.temp_dir / "root" / "root-ca.crt"
        self.assertTrue(root_key.exists())
        self.assertTrue(root_cert.exists())

        # Check intermediate CAs were created
        for domain in TrustDomain:
            domain_dir = self.temp_dir / domain.value
            ca_key = domain_dir / f"{domain.value}-ca.key"
            ca_cert = domain_dir / f"{domain.value}-ca.crt"
            chain = domain_dir / "chain.pem"

            self.assertTrue(ca_key.exists(), f"{domain.value} CA key missing")
            self.assertTrue(ca_cert.exists(), f"{domain.value} CA cert missing")
            self.assertTrue(chain.exists(), f"{domain.value} chain missing")

    def test_certificate_chain_retrieval(self):
        """Test retrieving certificate chains."""
        self.pki.initialize_pki()

        for domain in TrustDomain:
            chain = self.pki.get_certificate_chain(domain)
            self.assertIn('key', chain)
            self.assertIn('cert', chain)
            self.assertIn('chain', chain)
            self.assertIsInstance(chain['key'], bytes)
            self.assertIsInstance(chain['cert'], bytes)
            self.assertIsInstance(chain['chain'], bytes)

    def test_certificate_info(self):
        """Test getting certificate information."""
        self.pki.initialize_pki()

        for domain in TrustDomain:
            info = self.pki.get_certificate_info(domain)
            self.assertIn('subject', info)
            self.assertIn('issuer', info)
            self.assertIn('serial', info)
            self.assertIn('not_before', info)
            self.assertIn('not_after', info)

            # Check subject contains domain name
            self.assertIn(domain.value.title(), info['subject'])

    def test_idempotent_initialization(self):
        """Test that re-initialization doesn't overwrite existing certs."""
        self.pki.initialize_pki()

        # Get cert info
        info1 = self.pki.get_certificate_info(TrustDomain.EXECUTION)

        # Re-initialize (should not overwrite)
        self.pki.initialize_pki()

        # Cert should be the same
        info2 = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        self.assertEqual(info1['serial'], info2['serial'])


class TestSigner(unittest.TestCase):
    """Test signing functionality."""

    def setUp(self):
        """Set up PKI and create signer."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)
        self.pki.initialize_pki()

        # Get execution plane cert chain
        self.cert_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        self.signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test_agent"
        )

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_sign_dict(self):
        """Test signing a dictionary."""
        data = {"test": "data", "number": 42, "list": [1, 2, 3]}
        signed = self.signer.sign_dict(data)

        # Check signature metadata was added
        self.assertIn('_signature', signed)
        self.assertIn('signature', signed['_signature'])
        self.assertIn('signer', signed['_signature'])
        self.assertIn('timestamp', signed['_signature'])
        self.assertIn('cert_subject', signed['_signature'])

        # Original data should still be present
        self.assertEqual(signed['test'], "data")
        self.assertEqual(signed['number'], 42)

    def test_sign_data(self):
        """Test signing arbitrary data."""
        data = {"workflow": "test", "step": 1}
        signed_data = self.signer.sign(data)

        self.assertEqual(signed_data.data, data)
        self.assertEqual(signed_data.signer, "test_agent")
        self.assertIsNotNone(signed_data.signature)
        self.assertIsNotNone(signed_data.timestamp)


class TestVerifier(unittest.TestCase):
    """Test verification functionality."""

    def setUp(self):
        """Set up PKI, signer, and verifier."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)
        self.pki.initialize_pki()

        # Get execution plane cert chain
        self.cert_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        self.signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test_agent"
        )
        self.verifier = Verifier(chain_pem=self.cert_chain['chain'])

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_verify_signed_data(self):
        """Test verifying signed data."""
        data = {"test": "data", "value": 123}
        signed_data = self.signer.sign(data)

        # Verification should succeed
        self.assertTrue(self.verifier.verify(signed_data))

    def test_verify_tampered_data(self):
        """Test that tampered data fails verification."""
        data = {"test": "data", "value": 123}
        signed_data = self.signer.sign(data)

        # Tamper with the data
        signed_data.data["value"] = 456

        # Verification should fail
        self.assertFalse(self.verifier.verify(signed_data))

    def test_verify_dict(self):
        """Test verifying signed dictionary."""
        data = {"mission": "test", "status": "success"}
        signed = self.signer.sign_dict(data)

        # Verification should succeed
        self.assertTrue(self.verifier.verify_dict(signed))

    def test_verify_tampered_dict(self):
        """Test that tampered dict fails verification."""
        data = {"mission": "test", "status": "success"}
        signed = self.signer.sign_dict(data)

        # Tamper with data
        signed["status"] = "failed"

        # Verification should fail
        self.assertFalse(self.verifier.verify_dict(signed))

    def test_verify_unsigned_dict(self):
        """Test that unsigned dict fails verification."""
        data = {"mission": "test"}
        self.assertFalse(self.verifier.verify_dict(data))


class TestTuringTapeWithSigning(unittest.TestCase):
    """Test TuringTape with cryptographic signing."""

    def setUp(self):
        """Set up PKI and TuringTape with signer."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)
        self.pki.initialize_pki()

        # Get execution plane cert chain
        self.cert_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        self.signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test_agent"
        )
        self.verifier = Verifier(chain_pem=self.cert_chain['chain'])

        # Create TuringTape with signer
        self.tape = TuringTape(
            base_dir=self.temp_dir,
            workflow_id="test_workflow",
            signer=self.signer
        )

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_append_signed_entry(self):
        """Test appending signed entries to tape."""
        self.tape.append(
            agent="architect",
            event="design_created",
            state={"components": ["frontend", "backend"]}
        )

        # Read back and verify
        entries = list(self.tape.read_all())
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertIn('_signature', entry)
        self.assertEqual(entry['agent'], "architect")
        self.assertEqual(entry['event'], "design_created")

    def test_verify_tape_entries(self):
        """Test verifying tape entries."""
        # Add multiple entries
        self.tape.append("architect", "start", {"step": 1})
        self.tape.append("builder", "build", {"step": 2})
        self.tape.append("critic", "review", {"step": 3})

        # Verify all entries
        results = self.tape.verify_all(self.verifier)

        self.assertEqual(results['total'], 3)
        self.assertEqual(results['verified'], 3)
        self.assertEqual(results['failed'], 0)
        self.assertEqual(results['unsigned'], 0)

    def test_verify_individual_entry(self):
        """Test verifying individual entry."""
        self.tape.append("recorder", "publish", {"artifacts": ["file1.py"]})

        entries = list(self.tape.read_all())
        self.assertTrue(self.tape.verify_entry(entries[0], self.verifier))


class TestCrossDomainVerification(unittest.TestCase):
    """Test that different trust domains are properly isolated."""

    def setUp(self):
        """Set up PKI with multiple domains."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir)
        self.pki.initialize_pki()

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_execution_plane_signing(self):
        """Test execution plane can sign and verify."""
        exec_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        signer = Signer(
            private_key_pem=exec_chain['key'],
            certificate_pem=exec_chain['cert'],
            signer_id="architect"
        )
        verifier = Verifier(chain_pem=exec_chain['chain'])

        data = {"design": "test"}
        signed = signer.sign_dict(data)
        self.assertTrue(verifier.verify_dict(signed))

    def test_government_plane_signing(self):
        """Test government plane can sign and verify."""
        gov_chain = self.pki.get_certificate_chain(TrustDomain.GOVERNMENT)
        signer = Signer(
            private_key_pem=gov_chain['key'],
            certificate_pem=gov_chain['cert'],
            signer_id="governance"
        )
        verifier = Verifier(chain_pem=gov_chain['chain'])

        data = {"policy": "approved"}
        signed = signer.sign_dict(data)
        self.assertTrue(verifier.verify_dict(signed))

    def test_logging_plane_signing(self):
        """Test logging plane can sign and verify."""
        log_chain = self.pki.get_certificate_chain(TrustDomain.LOGGING)
        signer = Signer(
            private_key_pem=log_chain['key'],
            certificate_pem=log_chain['cert'],
            signer_id="recorder"
        )
        verifier = Verifier(chain_pem=log_chain['chain'])

        data = {"artifacts": ["file1.py", "file2.py"]}
        signed = signer.sign_dict(data)
        self.assertTrue(verifier.verify_dict(signed))


if __name__ == "__main__":
    unittest.main()
