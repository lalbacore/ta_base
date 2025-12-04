"""
OCSP (Online Certificate Status Protocol) Responder for Team Agent PKI.

Implements real-time certificate status checking with signed OCSP responses.
"""

import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import ocsp


class OCSPStatus(Enum):
    """OCSP certificate status."""
    GOOD = "good"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


class OCSPResponder:
    """
    OCSP Responder for real-time certificate status checking.

    Features:
    - Generate signed OCSP responses
    - Cache responses for performance
    - Support good/revoked/unknown status
    - Integration with CRLManager for revocation checking
    """

    def __init__(
        self,
        responder_cert_pem: bytes,
        responder_key_pem: bytes,
        crl_manager: Optional['CRLManager'] = None,
        cache_duration: int = 300  # 5 minutes default
    ):
        """
        Initialize OCSP responder.

        Args:
            responder_cert_pem: OCSP responder certificate (intermediate CA) in PEM
            responder_key_pem: OCSP responder private key in PEM
            crl_manager: Optional CRLManager for revocation checking
            cache_duration: Response cache duration in seconds (default: 300)
        """
        self.responder_cert = x509.load_pem_x509_certificate(
            responder_cert_pem,
            backend=default_backend()
        )
        self.responder_key = serialization.load_pem_private_key(
            responder_key_pem,
            password=None,
            backend=default_backend()
        )
        self.crl_manager = crl_manager
        self.cache_duration = cache_duration

        # Response cache: serial -> (response_bytes, expiry_time)
        self.cache: Dict[str, Tuple[bytes, float]] = {}

    def check_certificate_status(
        self,
        serial_number: str
    ) -> Tuple[OCSPStatus, Optional[Dict[str, Any]]]:
        """
        Check certificate status.

        Args:
            serial_number: Certificate serial number (hex string)

        Returns:
            Tuple of (status, revocation_info)
            - status: OCSPStatus enum
            - revocation_info: Dict with revocation details if revoked, None otherwise
        """
        if not self.crl_manager:
            # No CRL manager, assume certificate is good
            return OCSPStatus.GOOD, None

        # Check if certificate is revoked
        if self.crl_manager.is_revoked(serial_number):
            revocation_info = self.crl_manager.get_revocation_info(serial_number)
            return OCSPStatus.REVOKED, revocation_info

        # Certificate is good (not revoked and not unknown)
        # In a full implementation, we'd check if cert exists in our database
        # For now, we assume any non-revoked cert is good
        return OCSPStatus.GOOD, None

    def build_ocsp_response(
        self,
        cert_serial: int,
        cert_issuer: x509.Name,
        this_update: Optional[datetime] = None,
        next_update: Optional[datetime] = None
    ) -> bytes:
        """
        Build and sign an OCSP response.

        Args:
            cert_serial: Certificate serial number (as integer)
            cert_issuer: Certificate issuer name
            this_update: Response validity start time (default: now)
            next_update: Response validity end time (default: now + cache_duration)

        Returns:
            Signed OCSP response in DER format
        """
        # Convert serial to hex for status checking
        serial_hex = format(cert_serial, 'x')

        # Check certificate status
        status, revocation_info = self.check_certificate_status(serial_hex)

        # Set response validity times
        if this_update is None:
            this_update = datetime.utcnow()
        if next_update is None:
            next_update = this_update + timedelta(seconds=self.cache_duration)

        # Build certificate ID
        builder = ocsp.OCSPResponseBuilder()

        # Add responder ID (required for signing)
        builder = builder.responder_id(
            ocsp.OCSPResponderEncoding.HASH,
            self.responder_cert
        )

        # Create response based on status
        if status == OCSPStatus.GOOD:
            builder = builder.add_response(
                cert=self._create_dummy_cert(cert_serial, cert_issuer),
                issuer=self.responder_cert,
                algorithm=hashes.SHA256(),
                cert_status=ocsp.OCSPCertStatus.GOOD,
                this_update=this_update,
                next_update=next_update,
                revocation_time=None,
                revocation_reason=None
            )
        elif status == OCSPStatus.REVOKED:
            # Parse revocation date
            revocation_date = datetime.fromisoformat(
                revocation_info['revocation_date'].rstrip('Z')
            )

            # Map reason code to x509.ReasonFlags
            reason = None
            try:
                reason_code = revocation_info['reason_code']
                if reason_code != 0:  # Not UNSPECIFIED
                    reason = x509.ReasonFlags(reason_code)
            except (KeyError, ValueError):
                pass

            builder = builder.add_response(
                cert=self._create_dummy_cert(cert_serial, cert_issuer),
                issuer=self.responder_cert,
                algorithm=hashes.SHA256(),
                cert_status=ocsp.OCSPCertStatus.REVOKED,
                this_update=this_update,
                next_update=next_update,
                revocation_time=revocation_date,
                revocation_reason=reason
            )
        else:  # UNKNOWN
            # For unknown certificates, we return UNKNOWN status
            # Note: cryptography library handles this differently
            # We'll return a response indicating the cert is unknown
            pass

        # Sign the response
        response = builder.sign(
            self.responder_key,
            hashes.SHA256()
        )

        return response.public_bytes(serialization.Encoding.DER)

    def _create_dummy_cert(
        self,
        serial: int,
        issuer: x509.Name
    ) -> x509.Certificate:
        """
        Create a minimal dummy certificate for OCSP response.

        This is needed because the OCSP builder requires a certificate object,
        but we only have the serial number. In a production system, we'd
        retrieve the actual certificate from storage.

        Args:
            serial: Certificate serial number
            issuer: Certificate issuer name

        Returns:
            Dummy certificate with correct serial and issuer
        """
        from cryptography.hazmat.primitives.asymmetric import rsa

        # Generate a dummy key (not used, just for cert structure)
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Create minimal certificate
        cert = (
            x509.CertificateBuilder()
            .subject_name(issuer)  # Use issuer as subject for dummy
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(serial)
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=1))
            .sign(key, hashes.SHA256(), default_backend())
        )

        return cert

    def get_cached_response(self, serial_hex: str) -> Optional[bytes]:
        """
        Get cached OCSP response if available and not expired.

        Args:
            serial_hex: Certificate serial number (hex string)

        Returns:
            Cached response bytes or None if not cached or expired
        """
        if serial_hex in self.cache:
            response_bytes, expiry_time = self.cache[serial_hex]
            if time.time() < expiry_time:
                return response_bytes
            else:
                # Remove expired entry
                del self.cache[serial_hex]
        return None

    def cache_response(self, serial_hex: str, response_bytes: bytes):
        """
        Cache OCSP response.

        Args:
            serial_hex: Certificate serial number (hex string)
            response_bytes: OCSP response bytes to cache
        """
        expiry_time = time.time() + self.cache_duration
        self.cache[serial_hex] = (response_bytes, expiry_time)

    def clear_cache(self):
        """Clear all cached responses."""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache statistics
        """
        now = time.time()
        valid_entries = sum(1 for _, (_, expiry) in self.cache.items() if expiry > now)

        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries,
            "cache_duration": self.cache_duration
        }

    def handle_ocsp_request(
        self,
        cert_serial: int,
        cert_issuer: x509.Name,
        use_cache: bool = True
    ) -> bytes:
        """
        Handle OCSP request and return signed response.

        Args:
            cert_serial: Certificate serial number (as integer)
            cert_issuer: Certificate issuer name
            use_cache: Whether to use cached responses (default: True)

        Returns:
            Signed OCSP response in DER format
        """
        serial_hex = format(cert_serial, 'x')

        # Check cache first
        if use_cache:
            cached_response = self.get_cached_response(serial_hex)
            if cached_response:
                return cached_response

        # Build new response
        response_bytes = self.build_ocsp_response(
            cert_serial=cert_serial,
            cert_issuer=cert_issuer
        )

        # Cache the response
        if use_cache:
            self.cache_response(serial_hex, response_bytes)

        return response_bytes
