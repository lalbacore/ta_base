"""
Certificate Revocation List (CRL) Manager for Team Agent PKI.

Implements SQLite-based CRL storage, generation, and verification.
"""

import sqlite3
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
from cryptography import x509
from cryptography.x509.oid import ExtensionOID, CRLEntryExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


class RevocationReason(Enum):
    """CRL revocation reasons (RFC 5280)."""
    UNSPECIFIED = 0
    KEY_COMPROMISE = 1
    CA_COMPROMISE = 2
    AFFILIATION_CHANGED = 3
    SUPERSEDED = 4
    CESSATION_OF_OPERATION = 5
    CERTIFICATE_HOLD = 6
    # 7 is unused
    REMOVE_FROM_CRL = 8
    PRIVILEGE_WITHDRAWN = 9


class CRLManager:
    """
    Manages Certificate Revocation Lists with SQLite backend.

    Features:
    - Revoke certificates with reason codes
    - Generate CRL in PEM/DER formats
    - Check revocation status
    - Suspend/reinstate certificates (certificate hold)
    - Audit trail of all revocations
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize CRL manager.

        Args:
            db_path: Path to SQLite database (default: .team_agent/pki/crl.db)
        """
        self.db_path = db_path or Path(".team_agent/pki/crl.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Allow cross-thread usage for Flask request handlers
        # Safe because: 1) Writes are immediately committed, 2) No complex transactions
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self._init_database()

    def _init_database(self):
        """Initialize CRL database schema."""
        cursor = self.conn.cursor()

        # Revoked certificates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revoked_certificates (
                serial_number TEXT PRIMARY KEY,
                revocation_date TEXT NOT NULL,
                reason TEXT NOT NULL,
                reason_code INTEGER NOT NULL,
                revoked_by TEXT NOT NULL,
                trust_domain TEXT NOT NULL,
                cert_subject TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CRL versions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crl_versions (
                version INTEGER PRIMARY KEY AUTOINCREMENT,
                issued_at TEXT NOT NULL,
                next_update TEXT NOT NULL,
                cert_count INTEGER NOT NULL,
                signature TEXT,
                issuer TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CRL audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crl_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                serial_number TEXT,
                reason TEXT,
                operator TEXT,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_serial
            ON revoked_certificates(serial_number)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trust_domain
            ON revoked_certificates(trust_domain)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_revocation_date
            ON revoked_certificates(revocation_date)
        """)

        self.conn.commit()

    def revoke_certificate(
        self,
        serial_number: str,
        reason: RevocationReason,
        revoked_by: str,
        trust_domain: str,
        cert_subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Revoke a certificate.

        Args:
            serial_number: Certificate serial number (hex string)
            reason: Revocation reason
            revoked_by: Who revoked the certificate
            trust_domain: Trust domain (execution, government, logging)
            cert_subject: Certificate subject (optional)
            metadata: Additional metadata (optional)

        Returns:
            True if revoked, False if already revoked
        """
        # Check if already revoked
        if self.is_revoked(serial_number):
            return False

        cursor = self.conn.cursor()
        revocation_date = datetime.utcnow().isoformat() + 'Z'

        cursor.execute("""
            INSERT INTO revoked_certificates
            (serial_number, revocation_date, reason, reason_code, revoked_by,
             trust_domain, cert_subject, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            serial_number,
            revocation_date,
            reason.name,
            reason.value,
            revoked_by,
            trust_domain,
            cert_subject,
            str(metadata) if metadata else None
        ))

        # Audit log
        cursor.execute("""
            INSERT INTO crl_audit_log
            (timestamp, action, serial_number, reason, operator, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            revocation_date,
            "REVOKE",
            serial_number,
            reason.name,
            revoked_by,
            f"Certificate revoked: {reason.name}"
        ))

        self.conn.commit()
        return True

    def is_revoked(self, serial_number: str) -> bool:
        """
        Check if certificate is revoked.

        Args:
            serial_number: Certificate serial number

        Returns:
            True if revoked, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 1 FROM revoked_certificates
            WHERE serial_number = ?
            AND reason != 'REMOVE_FROM_CRL'
        """, (serial_number,))

        return cursor.fetchone() is not None

    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Get revocation information for a certificate.

        Args:
            serial_number: Certificate serial number

        Returns:
            Dict with revocation info, or None if not revoked
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM revoked_certificates
            WHERE serial_number = ?
        """, (serial_number,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def suspend_certificate(
        self,
        serial_number: str,
        suspended_by: str,
        trust_domain: str
    ) -> bool:
        """
        Suspend certificate (certificate hold).

        Args:
            serial_number: Certificate serial number
            suspended_by: Who suspended the certificate
            trust_domain: Trust domain

        Returns:
            True if suspended
        """
        return self.revoke_certificate(
            serial_number=serial_number,
            reason=RevocationReason.CERTIFICATE_HOLD,
            revoked_by=suspended_by,
            trust_domain=trust_domain,
            metadata={"action": "suspend"}
        )

    def reinstate_certificate(
        self,
        serial_number: str,
        reinstated_by: str
    ) -> bool:
        """
        Reinstate suspended certificate (remove from CRL).

        Only works for certificates with CERTIFICATE_HOLD reason.

        Args:
            serial_number: Certificate serial number
            reinstated_by: Who reinstated the certificate

        Returns:
            True if reinstated, False if not suspended or permanently revoked
        """
        # Check if certificate is in hold status
        info = self.get_revocation_info(serial_number)
        if not info or info['reason'] != 'CERTIFICATE_HOLD':
            return False

        cursor = self.conn.cursor()

        # Update reason to REMOVE_FROM_CRL
        cursor.execute("""
            UPDATE revoked_certificates
            SET reason = 'REMOVE_FROM_CRL',
                reason_code = ?,
                metadata = ?
            WHERE serial_number = ?
        """, (
            RevocationReason.REMOVE_FROM_CRL.value,
            f"Reinstated by {reinstated_by}",
            serial_number
        ))

        # Audit log
        cursor.execute("""
            INSERT INTO crl_audit_log
            (timestamp, action, serial_number, operator, details)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat() + 'Z',
            "REINSTATE",
            serial_number,
            reinstated_by,
            "Certificate reinstated from hold"
        ))

        self.conn.commit()
        return True

    def list_revoked_certificates(
        self,
        trust_domain: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List revoked certificates.

        Args:
            trust_domain: Filter by trust domain (optional)
            limit: Maximum number to return

        Returns:
            List of revoked certificate records
        """
        cursor = self.conn.cursor()

        if trust_domain:
            cursor.execute("""
                SELECT * FROM revoked_certificates
                WHERE trust_domain = ?
                AND reason != 'REMOVE_FROM_CRL'
                ORDER BY revocation_date DESC
                LIMIT ?
            """, (trust_domain, limit))
        else:
            cursor.execute("""
                SELECT * FROM revoked_certificates
                WHERE reason != 'REMOVE_FROM_CRL'
                ORDER BY revocation_date DESC
                LIMIT ?
            """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get CRL statistics.

        Returns:
            Dict with statistics
        """
        cursor = self.conn.cursor()

        # Total revoked
        cursor.execute("""
            SELECT COUNT(*) as total FROM revoked_certificates
            WHERE reason != 'REMOVE_FROM_CRL'
        """)
        total_revoked = cursor.fetchone()['total']

        # By trust domain
        cursor.execute("""
            SELECT trust_domain, COUNT(*) as count
            FROM revoked_certificates
            WHERE reason != 'REMOVE_FROM_CRL'
            GROUP BY trust_domain
        """)
        by_domain = {row['trust_domain']: row['count'] for row in cursor.fetchall()}

        # By reason
        cursor.execute("""
            SELECT reason, COUNT(*) as count
            FROM revoked_certificates
            WHERE reason != 'REMOVE_FROM_CRL'
            GROUP BY reason
        """)
        by_reason = {row['reason']: row['count'] for row in cursor.fetchall()}

        # Suspended (on hold)
        cursor.execute("""
            SELECT COUNT(*) as count FROM revoked_certificates
            WHERE reason = 'CERTIFICATE_HOLD'
        """)
        suspended = cursor.fetchone()['count']

        return {
            "total_revoked": total_revoked,
            "by_trust_domain": by_domain,
            "by_reason": by_reason,
            "suspended": suspended,
            "database_path": str(self.db_path)
        }

    def generate_crl_data(self) -> List[Dict[str, Any]]:
        """
        Generate CRL data for X.509 CRL generation.

        Returns:
            List of revoked certificate entries
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT serial_number, revocation_date, reason_code
            FROM revoked_certificates
            WHERE reason != 'REMOVE_FROM_CRL'
            ORDER BY revocation_date ASC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def record_crl_version(
        self,
        issued_at: str,
        next_update: str,
        cert_count: int,
        issuer: str
    ) -> int:
        """
        Record a CRL version.

        Args:
            issued_at: ISO timestamp
            next_update: ISO timestamp
            cert_count: Number of certificates in CRL
            issuer: CRL issuer

        Returns:
            Version number
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO crl_versions
            (issued_at, next_update, cert_count, issuer)
            VALUES (?, ?, ?, ?)
        """, (issued_at, next_update, cert_count, issuer))

        self.conn.commit()
        return cursor.lastrowid

    def get_audit_log(
        self,
        limit: int = 100,
        since: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get CRL audit log.

        Args:
            limit: Maximum entries to return
            since: ISO timestamp to filter from

        Returns:
            List of audit log entries
        """
        cursor = self.conn.cursor()

        if since:
            cursor.execute("""
                SELECT * FROM crl_audit_log
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (since, limit))
        else:
            cursor.execute("""
                SELECT * FROM crl_audit_log
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def generate_crl(
        self,
        issuer_key_pem: bytes,
        issuer_cert_pem: bytes,
        validity_days: int = 7
    ) -> bytes:
        """
        Generate X.509 CRL in PEM format.

        Args:
            issuer_key_pem: Issuer (intermediate CA) private key in PEM format
            issuer_cert_pem: Issuer certificate in PEM format
            validity_days: CRL validity period in days (default: 7)

        Returns:
            CRL in PEM format
        """
        # Load issuer key and certificate
        issuer_key = serialization.load_pem_private_key(
            issuer_key_pem,
            password=None,
            backend=default_backend()
        )
        issuer_cert = x509.load_pem_x509_certificate(
            issuer_cert_pem,
            backend=default_backend()
        )

        # Get revoked certificates from database
        crl_data = self.generate_crl_data()

        # Build CRL
        crl_builder = x509.CertificateRevocationListBuilder()
        crl_builder = crl_builder.issuer_name(issuer_cert.subject)

        now = datetime.utcnow()
        crl_builder = crl_builder.last_update(now)
        crl_builder = crl_builder.next_update(now + timedelta(days=validity_days))

        # Add revoked certificates
        for entry in crl_data:
            serial = int(entry['serial_number'], 16)  # Convert hex to int
            revocation_date = datetime.fromisoformat(
                entry['revocation_date'].rstrip('Z')
            )
            reason_code = entry['reason_code']

            # Create revoked certificate entry
            revoked_cert = (
                x509.RevokedCertificateBuilder()
                .serial_number(serial)
                .revocation_date(revocation_date)
            )

            # Add revocation reason extension
            if reason_code != RevocationReason.UNSPECIFIED.value:
                try:
                    reason = x509.ReasonFlags(reason_code)
                    revoked_cert = revoked_cert.add_extension(
                        x509.CRLReason(reason),
                        critical=False
                    )
                except (ValueError, KeyError):
                    # Skip invalid reason codes
                    pass

            crl_builder = crl_builder.add_revoked_certificate(revoked_cert.build())

        # Add CRL extensions
        crl_builder = crl_builder.add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(
                issuer_cert.public_key()
            ),
            critical=False
        )

        # CRL number (version-like tracking)
        # Use the count of CRL versions as CRL number
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM crl_versions")
        crl_number = cursor.fetchone()['count'] + 1

        crl_builder = crl_builder.add_extension(
            x509.CRLNumber(crl_number),
            critical=False
        )

        # Sign CRL
        crl = crl_builder.sign(
            private_key=issuer_key,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        # Record CRL version
        self.record_crl_version(
            issued_at=now.isoformat() + 'Z',
            next_update=(now + timedelta(days=validity_days)).isoformat() + 'Z',
            cert_count=len(crl_data),
            issuer=issuer_cert.subject.rfc4514_string()
        )

        # Return PEM-encoded CRL
        return crl.public_bytes(serialization.Encoding.PEM)

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
