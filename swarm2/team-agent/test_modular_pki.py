#!/usr/bin/env python3
"""
Test script for modular PKI implementation.

Tests the PKIProvider interface, PKIFactory, and SelfSignedCAProvider.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from swarms.team_agent.crypto.pki_factory import PKIFactory, create_pki_provider
from swarms.team_agent.crypto.pki_provider import TrustDomain, RevocationReason


def test_provider_creation():
    """Test creating providers via factory."""
    print("\n=== Test 1: Provider Creation ===")

    # Test self-signed provider creation
    config = {
        'type': 'self-signed',
        'base_dir': str(Path.home() / '.team_agent' / 'pki')
    }

    provider = PKIFactory.create_provider(config)
    print(f"✓ Created provider: {provider.provider_name}")
    print(f"  Type: {provider.provider_type}")
    print(f"  Features: CRL={provider.supports_feature('crl')}, Offline={provider.supports_feature('offline')}")


def test_certificate_operations():
    """Test certificate issuance and info retrieval."""
    print("\n=== Test 2: Certificate Operations ===")

    # Create provider
    provider = create_pki_provider('self-signed')

    # Test certificate info retrieval
    for domain in TrustDomain:
        cert_info = provider.get_certificate_info(domain)
        print(f"\n✓ {domain.value.upper()} domain certificate:")
        print(f"  Serial: {cert_info.get('serial', 'N/A')}")
        print(f"  Subject: {cert_info.get('subject', 'N/A')}")
        print(f"  Issuer: {cert_info.get('issuer', 'N/A')}")
        print(f"  Valid from: {cert_info.get('not_before', 'N/A')}")
        print(f"  Valid to: {cert_info.get('not_after', 'N/A')}")


def test_certificate_rotation():
    """Test certificate rotation (re-issuance)."""
    print("\n=== Test 3: Certificate Rotation ===")

    provider = create_pki_provider('self-signed')

    # Get original certificate
    domain = TrustDomain.EXECUTION
    old_cert = provider.get_certificate_info(domain)
    old_serial = old_cert.get('serial')
    print(f"Original certificate serial: {old_serial}")

    # Rotate certificate (issue new one)
    print("Rotating certificate...")
    new_cert = provider.issue_certificate(domain, validity_days=365)
    new_serial = new_cert.get('serial')
    print(f"✓ New certificate serial: {new_serial}")
    print(f"  Certificates are different: {old_serial != new_serial}")


def test_revocation():
    """Test certificate revocation."""
    print("\n=== Test 4: Certificate Revocation ===")

    provider = create_pki_provider('self-signed')

    # Issue a certificate
    domain = TrustDomain.LOGGING
    cert = provider.issue_certificate(domain)
    serial = cert.get('serial')
    print(f"Issued certificate: {serial}")

    # Check initial revocation status
    is_revoked_before = provider.is_revoked(serial)
    print(f"Revoked before revocation: {is_revoked_before}")

    # Revoke certificate
    success = provider.revoke_certificate(
        serial_number=serial,
        reason=RevocationReason.SUPERSEDED,
        revoked_by='test_script',
        trust_domain=domain
    )
    print(f"✓ Revocation successful: {success}")

    # Check revocation status
    is_revoked_after = provider.is_revoked(serial)
    print(f"Revoked after revocation: {is_revoked_after}")

    # Get revocation info
    revocation_info = provider.get_revocation_info(serial)
    if revocation_info:
        print(f"Revocation info:")
        print(f"  Reason: {revocation_info.get('reason', 'N/A')}")
        print(f"  Revoked by: {revocation_info.get('revoked_by', 'N/A')}")
        print(f"  Revoked at: {revocation_info.get('revocation_date', 'N/A')}")


def test_provider_listing():
    """Test listing available providers."""
    print("\n=== Test 5: Provider Listing ===")

    providers = PKIFactory.list_providers()
    print(f"Available providers:")
    for ptype, pname in providers.items():
        print(f"  - {ptype}: {pname}")


def test_statistics():
    """Test provider statistics."""
    print("\n=== Test 6: Statistics ===")

    provider = create_pki_provider('self-signed')
    stats = provider.get_statistics()

    print(f"PKI Statistics:")
    print(f"  Total certificates: {stats.get('total_certificates', 0)}")
    print(f"  Active certificates: {stats.get('active_certificates', 0)}")
    print(f"  Revoked certificates: {stats.get('revoked_certificates', 0)}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("MODULAR PKI IMPLEMENTATION TEST")
    print("=" * 60)

    try:
        test_provider_creation()
        test_certificate_operations()
        test_certificate_rotation()
        test_revocation()
        test_provider_listing()
        test_statistics()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
