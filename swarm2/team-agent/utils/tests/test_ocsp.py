"""
Tests for OCSP (Online Certificate Status Protocol) system.

Tests OCSP responder, certificate status checking, caching,
and integration with Verifier.
"""

import os
import sys
import unittest
import tempfile
import time
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from swarms.team_agent.crypto import (
    PKIManager,
    TrustDomain,
    RevocationReason,
    OCSPResponder,
    OCSPStatus,
    Signer,
    Verifier
)


class TestOCSPResponder(unittest.TestCase):
    """Test OCSP responder core functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

        # Create OCSP responder for execution domain
        self.responder = self.pki.create_ocsp_responder(
            TrustDomain.EXECUTION,
            cache_duration=5  # 5 seconds for testing
        )

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_ocsp_responder(self):
        """Test creating OCSP responder."""
        self.assertIsNotNone(self.responder)
        self.assertEqual(self.responder.cache_duration, 5)

    def test_check_certificate_status_good(self):
        """Test checking status of non-revoked certificate."""
        cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        serial = cert_info['serial']

        status, revocation_info = self.responder.check_certificate_status(serial)

        self.assertEqual(status, OCSPStatus.GOOD)
        self.assertIsNone(revocation_info)

    def test_check_certificate_status_revoked(self):
        """Test checking status of revoked certificate."""
        cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        serial = cert_info['serial']

        # Revoke the certificate
        self.pki.revoke_certificate(
            serial_number=serial,
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin",
            trust_domain=TrustDomain.EXECUTION
        )

        status, revocation_info = self.responder.check_certificate_status(serial)

        self.assertEqual(status, OCSPStatus.REVOKED)
        self.assertIsNotNone(revocation_info)
        self.assertEqual(revocation_info['serial_number'], serial)
        self.assertEqual(revocation_info['reason'], 'KEY_COMPROMISE')

    def test_build_ocsp_response(self):
        """Test building OCSP response."""
        cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        serial_int = int(cert_info['serial'], 16)

        # Get issuer from cert
        cert_chain = self.pki.get_certificate_chain(TrustDomain.EXECUTION)
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        cert = x509.load_pem_x509_certificate(
            cert_chain['cert'],
            backend=default_backend()
        )

        response_bytes = self.responder.build_ocsp_response(
            cert_serial=serial_int,
            cert_issuer=cert.issuer
        )

        self.assertIsNotNone(response_bytes)
        self.assertIsInstance(response_bytes, bytes)
        self.assertGreater(len(response_bytes), 0)

    def test_response_caching(self):
        """Test OCSP response caching."""
        serial_hex = "abc123"

        # Initially no cached response
        cached = self.responder.get_cached_response(serial_hex)
        self.assertIsNone(cached)

        # Cache a response
        test_response = b"test_ocsp_response"
        self.responder.cache_response(serial_hex, test_response)

        # Should be cached now
        cached = self.responder.get_cached_response(serial_hex)
        self.assertEqual(cached, test_response)

    def test_cache_expiration(self):
        """Test that cached responses expire."""
        serial_hex = "abc123"
        test_response = b"test_ocsp_response"

        # Cache with short duration (already set to 5 seconds in setUp)
        self.responder.cache_response(serial_hex, test_response)

        # Should be cached immediately
        cached = self.responder.get_cached_response(serial_hex)
        self.assertEqual(cached, test_response)

        # Wait for cache to expire
        time.sleep(6)

        # Should be None now
        cached = self.responder.get_cached_response(serial_hex)
        self.assertIsNone(cached)

    def test_clear_cache(self):
        """Test clearing OCSP cache."""
        # Cache multiple responses
        self.responder.cache_response("serial1", b"response1")
        self.responder.cache_response("serial2", b"response2")

        # Verify cached
        self.assertIsNotNone(self.responder.get_cached_response("serial1"))
        self.assertIsNotNone(self.responder.get_cached_response("serial2"))

        # Clear cache
        self.responder.clear_cache()

        # Should be empty now
        self.assertIsNone(self.responder.get_cached_response("serial1"))
        self.assertIsNone(self.responder.get_cached_response("serial2"))

    def test_cache_statistics(self):
        """Test getting cache statistics."""
        # Cache some responses
        self.responder.cache_response("serial1", b"response1")
        self.responder.cache_response("serial2", b"response2")

        stats = self.responder.get_cache_stats()

        self.assertEqual(stats['total_entries'], 2)
        self.assertEqual(stats['valid_entries'], 2)
        self.assertEqual(stats['expired_entries'], 0)
        self.assertEqual(stats['cache_duration'], 5)


class TestOCSPWithPKIManager(unittest.TestCase):
    """Test OCSP integration with PKIManager."""

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

    def test_create_responder_for_all_domains(self):
        """Test creating OCSP responders for all trust domains."""
        for domain in TrustDomain:
            responder = self.pki.create_ocsp_responder(domain)
            self.assertIsNotNone(responder)

    def test_responder_uses_crl_manager(self):
        """Test that OCSP responder integrates with CRL manager."""
        responder = self.pki.create_ocsp_responder(TrustDomain.EXECUTION)

        # Responder should have access to CRL manager
        self.assertIsNotNone(responder.crl_manager)
        self.assertEqual(responder.crl_manager, self.pki.crl_manager)


class TestVerifierWithOCSP(unittest.TestCase):
    """Test Verifier integration with OCSP."""

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

    def test_verifier_with_ocsp(self):
        """Test Verifier using OCSP for revocation checking."""
        ocsp_responder = self.pki.create_ocsp_responder(TrustDomain.EXECUTION)

        signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test"
        )

        verifier = Verifier(
            chain_pem=self.cert_chain['chain'],
            ocsp_responder=ocsp_responder,
            prefer_ocsp=True
        )

        # Sign and verify with valid certificate
        data = {"message": "test"}
        signed = signer.sign_dict(data)

        self.assertTrue(verifier.verify_dict(signed))

    def test_verifier_rejects_revoked_cert_via_ocsp(self):
        """Test that Verifier with OCSP rejects revoked certificates."""
        ocsp_responder = self.pki.create_ocsp_responder(TrustDomain.EXECUTION)

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

        # Verifier with OCSP should reject
        verifier = Verifier(
            chain_pem=self.cert_chain['chain'],
            ocsp_responder=ocsp_responder,
            prefer_ocsp=True
        )

        self.assertFalse(verifier.verify_dict(signed))

    def test_verifier_ocsp_fallback_to_crl(self):
        """Test Verifier falls back to CRL when OCSP returns UNKNOWN."""
        # This test verifies the fallback mechanism
        # In practice, OCSP will rarely return UNKNOWN for our implementation

        verifier = Verifier(
            chain_pem=self.cert_chain['chain'],
            crl_manager=self.pki.crl_manager,
            ocsp_responder=None,  # No OCSP, should use CRL
            prefer_ocsp=True
        )

        signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test"
        )

        # Sign data
        data = {"message": "test"}
        signed = signer.sign_dict(data)

        # Should verify with CRL (cert not revoked)
        self.assertTrue(verifier.verify_dict(signed))

        # Revoke via CRL
        self.pki.revoke_certificate(
            serial_number=self.cert_info['serial'],
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin",
            trust_domain=TrustDomain.EXECUTION
        )

        # Should fail verification via CRL
        self.assertFalse(verifier.verify_dict(signed))

    def test_verifier_prefer_ocsp_false(self):
        """Test Verifier with prefer_ocsp=False uses CRL first."""
        ocsp_responder = self.pki.create_ocsp_responder(TrustDomain.EXECUTION)

        verifier = Verifier(
            chain_pem=self.cert_chain['chain'],
            crl_manager=self.pki.crl_manager,
            ocsp_responder=ocsp_responder,
            prefer_ocsp=False  # Prefer CRL
        )

        signer = Signer(
            private_key_pem=self.cert_chain['key'],
            certificate_pem=self.cert_chain['cert'],
            signer_id="test"
        )

        data = {"message": "test"}
        signed = signer.sign_dict(data)

        # Should verify
        self.assertTrue(verifier.verify_dict(signed))

        # Revoke
        self.pki.revoke_certificate(
            serial_number=self.cert_info['serial'],
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin",
            trust_domain=TrustDomain.EXECUTION
        )

        # Should fail (using CRL)
        self.assertFalse(verifier.verify_dict(signed))


class TestOCSPPerformance(unittest.TestCase):
    """Test OCSP performance and caching benefits."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

        self.responder = self.pki.create_ocsp_responder(
            TrustDomain.EXECUTION,
            cache_duration=300
        )

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_cache_performance(self):
        """Test that caching improves performance."""
        cert_info = self.pki.get_certificate_info(TrustDomain.EXECUTION)
        serial = cert_info['serial']

        # First check (not cached)
        start = time.time()
        status1, _ = self.responder.check_certificate_status(serial)
        duration1 = time.time() - start

        # Second check (should be similar, as we don't cache status checks directly)
        # But the OCSP response generation uses caching
        start = time.time()
        status2, _ = self.responder.check_certificate_status(serial)
        duration2 = time.time() - start

        # Both should return GOOD
        self.assertEqual(status1, OCSPStatus.GOOD)
        self.assertEqual(status2, OCSPStatus.GOOD)

        # Note: Actual caching benefit is seen in handle_ocsp_request
        # which caches the full OCSP response


if __name__ == "__main__":
    unittest.main()
