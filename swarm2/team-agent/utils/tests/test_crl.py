"""
Tests for Certificate Revocation List (CRL) system.

Tests CRL database operations, CRL generation, revocation checking,
and integration with PKIManager and Verifier.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from swarms.team_agent.crypto import (
    PKIManager,
    TrustDomain,
    CRLManager,
    RevocationReason,
    Signer,
    Verifier
)
from swarms.team_agent.roles import BaseRole
from swarms.team_agent.roles.base import CertificateRevokedException


class TestCRLManager(unittest.TestCase):
    """Test CRLManager database operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.crl_db = self.temp_dir / "crl.db"
        self.crl_manager = CRLManager(db_path=self.crl_db)

    def tearDown(self):
        """Clean up."""
        self.crl_manager.close()
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_revoke_certificate(self):
        """Test certificate revocation."""
        result = self.crl_manager.revoke_certificate(
            serial_number="abc123",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="orchestrator",
            trust_domain="execution",
            cert_subject="CN=test-agent"
        )

        self.assertTrue(result)
        self.assertTrue(self.crl_manager.is_revoked("abc123"))

    def test_duplicate_revocation(self):
        """Test that revoking the same cert twice returns False."""
        # First revocation
        result1 = self.crl_manager.revoke_certificate(
            serial_number="abc123",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="orchestrator",
            trust_domain="execution"
        )
        self.assertTrue(result1)

        # Second revocation
        result2 = self.crl_manager.revoke_certificate(
            serial_number="abc123",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="orchestrator",
            trust_domain="execution"
        )
        self.assertFalse(result2)

    def test_get_revocation_info(self):
        """Test getting revocation information."""
        self.crl_manager.revoke_certificate(
            serial_number="abc123",
            reason=RevocationReason.AFFILIATION_CHANGED,
            revoked_by="admin",
            trust_domain="government",
            cert_subject="CN=governance"
        )

        info = self.crl_manager.get_revocation_info("abc123")

        self.assertIsNotNone(info)
        self.assertEqual(info['serial_number'], "abc123")
        self.assertEqual(info['reason'], "AFFILIATION_CHANGED")
        self.assertEqual(info['revoked_by'], "admin")
        self.assertEqual(info['trust_domain'], "government")

    def test_suspend_and_reinstate(self):
        """Test certificate suspension and reinstatement."""
        # Suspend certificate
        result = self.crl_manager.suspend_certificate(
            serial_number="abc123",
            suspended_by="orchestrator",
            trust_domain="execution"
        )
        self.assertTrue(result)
        self.assertTrue(self.crl_manager.is_revoked("abc123"))

        # Reinstate certificate
        result = self.crl_manager.reinstate_certificate(
            serial_number="abc123",
            reinstated_by="orchestrator"
        )
        self.assertTrue(result)
        self.assertFalse(self.crl_manager.is_revoked("abc123"))

    def test_cannot_reinstate_permanent_revocation(self):
        """Test that permanently revoked certs cannot be reinstated."""
        # Revoke with permanent reason
        self.crl_manager.revoke_certificate(
            serial_number="abc123",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="orchestrator",
            trust_domain="execution"
        )

        # Try to reinstate
        result = self.crl_manager.reinstate_certificate(
            serial_number="abc123",
            reinstated_by="orchestrator"
        )
        self.assertFalse(result)
        self.assertTrue(self.crl_manager.is_revoked("abc123"))

    def test_list_revoked_certificates(self):
        """Test listing revoked certificates."""
        # Revoke multiple certificates
        self.crl_manager.revoke_certificate(
            "abc123", RevocationReason.KEY_COMPROMISE, "admin", "execution"
        )
        self.crl_manager.revoke_certificate(
            "def456", RevocationReason.SUPERSEDED, "admin", "execution"
        )
        self.crl_manager.revoke_certificate(
            "ghi789", RevocationReason.KEY_COMPROMISE, "admin", "government"
        )

        # List all
        all_revoked = self.crl_manager.list_revoked_certificates()
        self.assertEqual(len(all_revoked), 3)

        # List by trust domain
        exec_revoked = self.crl_manager.list_revoked_certificates(
            trust_domain="execution"
        )
        self.assertEqual(len(exec_revoked), 2)

    def test_get_statistics(self):
        """Test CRL statistics."""
        # Revoke some certificates
        self.crl_manager.revoke_certificate(
            "abc123", RevocationReason.KEY_COMPROMISE, "admin", "execution"
        )
        self.crl_manager.revoke_certificate(
            "def456", RevocationReason.KEY_COMPROMISE, "admin", "execution"
        )
        self.crl_manager.suspend_certificate("ghi789", "admin", "government")

        stats = self.crl_manager.get_statistics()

        self.assertEqual(stats['total_revoked'], 3)
        self.assertEqual(stats['by_trust_domain']['execution'], 2)
        self.assertEqual(stats['by_trust_domain']['government'], 1)
        self.assertEqual(stats['suspended'], 1)

    def test_audit_log(self):
        """Test that revocations are logged."""
        self.crl_manager.revoke_certificate(
            "abc123", RevocationReason.KEY_COMPROMISE, "admin", "execution"
        )

        audit_log = self.crl_manager.get_audit_log(limit=10)

        self.assertEqual(len(audit_log), 1)
        self.assertEqual(audit_log[0]['action'], "REVOKE")
        self.assertEqual(audit_log[0]['serial_number'], "abc123")
        self.assertEqual(audit_log[0]['operator'], "admin")


class TestCRLGeneration(unittest.TestCase):
    """Test CRL X.509 generation."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_generate_empty_crl(self):
        """Test generating CRL with no revoked certificates."""
        crl_pem = self.pki.generate_crl(TrustDomain.EXECUTION)

        self.assertIsNotNone(crl_pem)
        self.assertIn(b'BEGIN X509 CRL', crl_pem)
        self.assertIn(b'END X509 CRL', crl_pem)

    def test_generate_crl_with_revocations(self):
        """Test generating CRL with revoked certificates."""
        # Get cert info to extract serial
        cert_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        serial = cert_info['serial']

        # Revoke the certificate
        self.pki.revoke_certificate(
            serial_number=serial,
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="orchestrator",
            trust_domain=TrustDomain.EXECUTION,
            cert_subject=cert_info['subject']
        )

        # Generate CRL
        crl_pem = self.pki.generate_crl(TrustDomain.EXECUTION)

        self.assertIsNotNone(crl_pem)
        self.assertIn(b'BEGIN X509 CRL', crl_pem)

        # Verify CRL is saved to file
        crl_path = self.pki.execution_dir / "crl.pem"
        self.assertTrue(crl_path.exists())

    def test_generate_all_crls(self):
        """Test generating CRLs for all trust domains."""
        crls = self.pki.generate_all_crls()

        self.assertEqual(len(crls), 3)
        self.assertIn('execution', crls)
        self.assertIn('government', crls)
        self.assertIn('logging', crls)

        for crl_pem in crls.values():
            self.assertIn(b'BEGIN X509 CRL', crl_pem)


class TestPKIManagerRevocation(unittest.TestCase):
    """Test PKIManager revocation methods."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_revoke_and_check(self):
        """Test revoking and checking certificate status."""
        cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        serial = cert_info['serial']

        # Not revoked initially
        self.assertFalse(self.pki.is_revoked(serial))

        # Revoke
        result = self.pki.revoke_certificate(
            serial_number=serial,
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin",
            trust_domain=TrustDomain.EXECUTION
        )
        self.assertTrue(result)

        # Now revoked
        self.assertTrue(self.pki.is_revoked(serial))

    def test_list_revoked_certificates(self):
        """Test listing revoked certificates via PKIManager."""
        # Revoke certificates
        exec_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        gov_info = self.pki.get_certificate_info(TrustDomain.GOVERNMENT)

        self.pki.revoke_certificate(
            exec_info['serial'], RevocationReason.KEY_COMPROMISE,
            "admin", TrustDomain.EXECUTION
        )
        self.pki.revoke_certificate(
            gov_info['serial'], RevocationReason.SUPERSEDED,
            "admin", TrustDomain.GOVERNMENT
        )

        # List all
        all_certs = self.pki.list_revoked_certificates()
        self.assertEqual(len(all_certs), 2)

        # List by domain
        exec_certs = self.pki.list_revoked_certificates(
            trust_domain=TrustDomain.EXECUTION
        )
        self.assertEqual(len(exec_certs), 1)

    def test_get_crl_statistics(self):
        """Test getting CRL statistics via PKIManager."""
        exec_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)

        self.pki.revoke_certificate(
            exec_info['serial'], RevocationReason.KEY_COMPROMISE,
            "admin", TrustDomain.EXECUTION
        )

        stats = self.pki.get_crl_statistics()

        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_revoked'], 1)


class TestVerifierRevocationChecking(unittest.TestCase):
    """Test Verifier revocation checking."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

        self.cert_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        self.cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_verifier_without_crl(self):
        """Test that Verifier works without CRL manager."""
        signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test"
        )

        verifier = Verifier(chain_pem=self.cert_chain['chain'])

        # Sign and verify
        data = {"message": "test"}
        signed = signer.sign_dict(data)

        self.assertTrue(verifier.verify_dict(signed))

    def test_verifier_with_crl_valid_cert(self):
        """Test Verifier with CRL manager and valid certificate."""
        signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test"
        )

        verifier = Verifier(
            chain_pem=self.cert_chain['chain'],
            crl_manager=self.pki.crl_manager
        )

        # Sign and verify
        data = {"message": "test"}
        signed = signer.sign_dict(data)

        self.assertTrue(verifier.verify_dict(signed))

    def test_verifier_rejects_revoked_cert(self):
        """Test that Verifier rejects signatures from revoked certificates."""
        signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test"
        )

        # Sign data before revocation
        data = {"message": "test"}
        signed = signer.sign_dict(data)

        # Revoke certificate
        self.pki.revoke_certificate(
            serial_number=self.cert_info['serial'],
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin",
            trust_domain=TrustDomain.EXECUTION
        )

        # Verifier with CRL should reject
        verifier = Verifier(
            chain_pem=self.cert_chain['chain'],
            crl_manager=self.pki.crl_manager
        )

        self.assertFalse(verifier.verify_dict(signed))


class TestBaseRoleRevocationChecking(unittest.TestCase):
    """Test BaseRole revocation checking on initialization."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

        self.cert_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        self.cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_role_init_with_valid_cert(self):
        """Test role initialization with valid certificate."""
        role = BaseRole(
            workflow_id="test_wf",
            cert_chain=self.cert_chain,
            crl_manager=self.pki.crl_manager
        )

        self.assertIsNotNone(role.signer)

    def test_role_init_rejects_revoked_cert(self):
        """Test that role initialization fails with revoked certificate."""
        # Revoke certificate
        self.pki.revoke_certificate(
            serial_number=self.cert_info['serial'],
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin",
            trust_domain=TrustDomain.EXECUTION
        )

        # Try to initialize role
        with self.assertRaises(CertificateRevokedException):
            BaseRole(
                workflow_id="test_wf",
                cert_chain=self.cert_chain,
                crl_manager=self.pki.crl_manager
            )

    def test_role_init_without_crl_manager(self):
        """Test that role works without CRL manager (backward compatibility)."""
        role = BaseRole(
            workflow_id="test_wf",
            cert_chain=self.cert_chain
        )

        self.assertIsNotNone(role.signer)


if __name__ == "__main__":
    unittest.main()
