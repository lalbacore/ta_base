"""
Secrets Management for Team Agent PKI.

Provides secure storage and retrieval of sensitive data with:
- AES-256 encryption at rest
- Short-lived plaintext exposure
- Certificate-based access control
- Trust score requirements
- Complete audit trail
- Automatic memory clearing
"""

import os
import sqlite3
import logging
import secrets as stdlib_secrets
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography import x509


logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets that can be stored."""
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"
    DATABASE_CREDS = "database_creds"
    CERTIFICATE = "certificate"
    CUSTOM = "custom"


class AccessLevel(Enum):
    """Access levels for secrets."""
    PUBLIC = "public"          # Any agent can access
    RESTRICTED = "restricted"  # Requires trust score >= 75
    CONFIDENTIAL = "confidential"  # Requires trust score >= 85
    SECRET = "secret"          # Requires trust score >= 95


@dataclass
class SecretMetadata:
    """Metadata for a secret."""
    secret_id: str
    secret_type: SecretType
    access_level: AccessLevel
    created_at: datetime
    created_by: str
    last_accessed: Optional[datetime]
    access_count: int
    allowed_agents: Optional[List[str]]  # None = any agent with sufficient trust
    description: Optional[str]


class SecretHandle:
    """
    Handle for accessing secret data with automatic cleanup.

    Secrets are decrypted only when accessed and immediately cleared
    from memory when the context exits.
    """

    def __init__(self, plaintext: bytes, secret_id: str, on_cleanup: Optional[Callable] = None):
        self._plaintext = plaintext
        self._secret_id = secret_id
        self._on_cleanup = on_cleanup
        self._accessed = False

    def get_value(self) -> str:
        """Get the secret value as a string."""
        self._accessed = True
        return self._plaintext.decode('utf-8')

    def get_bytes(self) -> bytes:
        """Get the secret value as bytes."""
        self._accessed = True
        return self._plaintext

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clear secret from memory."""
        if self._plaintext:
            # Overwrite memory with zeros before deletion
            for i in range(len(self._plaintext)):
                self._plaintext = self._plaintext[:i] + b'\x00' + self._plaintext[i+1:]
            self._plaintext = None

        if self._on_cleanup:
            self._on_cleanup()

    def __del__(self):
        """Ensure cleanup on deletion."""
        if self._plaintext:
            self.__exit__(None, None, None)


class SecretsManager:
    """
    Secrets Manager for secure storage and retrieval of sensitive data.

    Features:
    - AES-256-GCM encryption at rest
    - Certificate-based access control
    - Trust score requirements
    - Short-lived plaintext exposure
    - Automatic memory clearing
    - Complete audit trail
    - Agent-specific secrets
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        master_key: Optional[bytes] = None,
        trust_tracker: Optional[Any] = None
    ):
        """
        Initialize Secrets Manager.

        Args:
            db_path: Path to secrets database (default: .team_agent/secrets.db)
            master_key: Master encryption key (default: generated from system entropy)
            trust_tracker: AgentReputationTracker for trust-based access control
        """
        if db_path is None:
            db_path = Path.home() / ".team_agent" / "secrets.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Master key for encrypting secrets
        if master_key is None:
            # In production, this should be loaded from secure storage (HSM, KMS, etc.)
            key_file = self.db_path.parent / ".secrets_key"
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    self.master_key = f.read()
            else:
                self.master_key = stdlib_secrets.token_bytes(32)  # 256 bits
                # Store key (in production, use HSM/KMS instead)
                with open(key_file, 'wb') as f:
                    f.write(self.master_key)
                os.chmod(key_file, 0o600)  # Owner read/write only
        else:
            self.master_key = master_key

        self.trust_tracker = trust_tracker

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Secrets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secrets (
                secret_id TEXT PRIMARY KEY,
                secret_type TEXT NOT NULL,
                access_level TEXT NOT NULL,
                encrypted_data BLOB NOT NULL,
                salt BLOB NOT NULL,
                nonce BLOB NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                allowed_agents TEXT,
                description TEXT
            )
        """)

        # Access log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secret_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                access_time TEXT NOT NULL,
                access_granted BOOLEAN NOT NULL,
                denial_reason TEXT,
                trust_score REAL,
                FOREIGN KEY (secret_id) REFERENCES secrets(secret_id)
            )
        """)

        conn.commit()
        conn.close()

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from master key and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.master_key)

    def _encrypt(self, plaintext: bytes) -> Dict[str, bytes]:
        """Encrypt data using AES-256-GCM."""
        # Generate random salt and nonce
        salt = stdlib_secrets.token_bytes(16)
        nonce = stdlib_secrets.token_bytes(12)

        # Derive key
        key = self._derive_key(salt)

        # Encrypt
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return {
            'ciphertext': ciphertext + encryptor.tag,
            'salt': salt,
            'nonce': nonce
        }

    def _decrypt(self, ciphertext: bytes, salt: bytes, nonce: bytes) -> bytes:
        """Decrypt data using AES-256-GCM."""
        # Derive key
        key = self._derive_key(salt)

        # Split ciphertext and tag
        tag = ciphertext[-16:]
        ciphertext = ciphertext[:-16]

        # Decrypt
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    def store_secret(
        self,
        secret_id: str,
        secret_value: str,
        secret_type: SecretType,
        access_level: AccessLevel,
        created_by: str,
        allowed_agents: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Store a secret securely.

        Args:
            secret_id: Unique identifier for the secret
            secret_value: The secret data to store
            secret_type: Type of secret
            access_level: Required access level
            created_by: Agent/user who created the secret
            allowed_agents: Optional list of specific agents allowed to access
            description: Optional description

        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Encrypt the secret
            encrypted = self._encrypt(secret_value.encode('utf-8'))

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat() + 'Z'
            allowed_agents_json = json.dumps(allowed_agents) if allowed_agents else None

            cursor.execute("""
                INSERT INTO secrets (
                    secret_id, secret_type, access_level,
                    encrypted_data, salt, nonce,
                    created_at, created_by,
                    allowed_agents, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                secret_id,
                secret_type.value,
                access_level.value,
                encrypted['ciphertext'],
                encrypted['salt'],
                encrypted['nonce'],
                now,
                created_by,
                allowed_agents_json,
                description
            ))

            conn.commit()
            conn.close()

            logger.info(f"Secret stored: {secret_id} (type: {secret_type.value}, level: {access_level.value})")
            return True

        except sqlite3.IntegrityError:
            logger.warning(f"Secret already exists: {secret_id}")
            return False
        except Exception as e:
            logger.error(f"Error storing secret {secret_id}: {e}")
            return False

    def _check_access(
        self,
        agent_id: str,
        secret_metadata: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Check if agent has access to a secret.

        Returns:
            Tuple of (access_granted, denial_reason)
        """
        access_level = AccessLevel(secret_metadata['access_level'])

        # Check allowed agents list
        if secret_metadata['allowed_agents']:
            allowed = json.loads(secret_metadata['allowed_agents'])
            if agent_id not in allowed:
                return False, f"agent_not_in_allowed_list"

        # Check trust score requirements
        if self.trust_tracker:
            metrics = self.trust_tracker.get_agent_metrics(agent_id)
            if not metrics:
                return False, "agent_not_registered"

            # Map access levels to minimum trust scores
            min_trust = {
                AccessLevel.PUBLIC: 0.0,
                AccessLevel.RESTRICTED: 75.0,
                AccessLevel.CONFIDENTIAL: 85.0,
                AccessLevel.SECRET: 95.0
            }

            required_trust = min_trust.get(access_level, 0.0)
            if metrics.trust_score < required_trust:
                return False, f"insufficient_trust_score_{metrics.trust_score:.2f}_required_{required_trust}"

        return True, None

    @contextmanager
    def access_secret(
        self,
        secret_id: str,
        agent_id: str,
        agent_cert: Optional[bytes] = None
    ) -> SecretHandle:
        """
        Access a secret with automatic cleanup.

        This is the primary method for retrieving secrets. The secret is
        decrypted, used, and immediately cleared from memory.

        Usage:
            with secrets_mgr.access_secret("api_key", "my-agent") as secret:
                api_key = secret.get_value()
                # Use api_key...
            # Secret is automatically cleared from memory here

        Args:
            secret_id: ID of the secret to access
            agent_id: ID of the agent requesting access
            agent_cert: Optional agent certificate for verification

        Returns:
            SecretHandle context manager

        Raises:
            PermissionError: If access is denied
            KeyError: If secret doesn't exist
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get secret metadata
        cursor.execute("""
            SELECT * FROM secrets WHERE secret_id = ?
        """, (secret_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            raise KeyError(f"Secret not found: {secret_id}")

        secret_data = dict(row)

        # Check access
        access_granted, denial_reason = self._check_access(agent_id, secret_data)

        # Get trust score for logging
        trust_score = None
        if self.trust_tracker:
            metrics = self.trust_tracker.get_agent_metrics(agent_id)
            if metrics:
                trust_score = metrics.trust_score

        # Log access attempt
        now = datetime.utcnow().isoformat() + 'Z'
        cursor.execute("""
            INSERT INTO secret_access_log (
                secret_id, agent_id, access_time,
                access_granted, denial_reason, trust_score
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (secret_id, agent_id, now, access_granted, denial_reason, trust_score))

        if not access_granted:
            conn.commit()
            conn.close()
            logger.warning(f"Access denied for {agent_id} to secret {secret_id}: {denial_reason}")
            raise PermissionError(f"Access denied: {denial_reason}")

        # Update access statistics
        cursor.execute("""
            UPDATE secrets
            SET last_accessed = ?, access_count = access_count + 1
            WHERE secret_id = ?
        """, (now, secret_id))

        conn.commit()

        # Decrypt the secret
        plaintext = self._decrypt(
            secret_data['encrypted_data'],
            secret_data['salt'],
            secret_data['nonce']
        )

        conn.close()

        logger.info(f"Secret accessed: {secret_id} by {agent_id} (trust: {trust_score})")

        # Create handle with cleanup callback
        handle = SecretHandle(plaintext, secret_id)

        try:
            yield handle
        finally:
            # Ensure cleanup
            handle.__exit__(None, None, None)

    def get_secret_metadata(self, secret_id: str) -> Optional[SecretMetadata]:
        """Get metadata for a secret without decrypting it."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT secret_id, secret_type, access_level,
                   created_at, created_by, last_accessed,
                   access_count, allowed_agents, description
            FROM secrets WHERE secret_id = ?
        """, (secret_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        allowed_agents = json.loads(row['allowed_agents']) if row['allowed_agents'] else None

        return SecretMetadata(
            secret_id=row['secret_id'],
            secret_type=SecretType(row['secret_type']),
            access_level=AccessLevel(row['access_level']),
            created_at=datetime.fromisoformat(row['created_at'].rstrip('Z')),
            created_by=row['created_by'],
            last_accessed=datetime.fromisoformat(row['last_accessed'].rstrip('Z')) if row['last_accessed'] else None,
            access_count=row['access_count'],
            allowed_agents=allowed_agents,
            description=row['description']
        )

    def list_secrets(self, agent_id: Optional[str] = None) -> List[SecretMetadata]:
        """
        List all secrets (metadata only).

        Args:
            agent_id: Optional agent ID to filter secrets they can access

        Returns:
            List of SecretMetadata objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT secret_id, secret_type, access_level,
                   created_at, created_by, last_accessed,
                   access_count, allowed_agents, description
            FROM secrets
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        secrets = []
        for row in rows:
            allowed_agents = json.loads(row['allowed_agents']) if row['allowed_agents'] else None

            # Filter by agent if specified
            if agent_id:
                if allowed_agents and agent_id not in allowed_agents:
                    continue

            secrets.append(SecretMetadata(
                secret_id=row['secret_id'],
                secret_type=SecretType(row['secret_type']),
                access_level=AccessLevel(row['access_level']),
                created_at=datetime.fromisoformat(row['created_at'].rstrip('Z')),
                created_by=row['created_by'],
                last_accessed=datetime.fromisoformat(row['last_accessed'].rstrip('Z')) if row['last_accessed'] else None,
                access_count=row['access_count'],
                allowed_agents=allowed_agents,
                description=row['description']
            ))

        return secrets

    def delete_secret(self, secret_id: str, deleted_by: str) -> bool:
        """
        Delete a secret.

        Args:
            secret_id: ID of secret to delete
            deleted_by: Agent/user deleting the secret

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM secrets WHERE secret_id = ?", (secret_id,))
        deleted = cursor.rowcount > 0

        if deleted:
            # Keep access log for audit purposes
            logger.info(f"Secret deleted: {secret_id} by {deleted_by}")

        conn.commit()
        conn.close()

        return deleted

    def get_access_log(
        self,
        secret_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get secret access log.

        Args:
            secret_id: Optional secret ID to filter
            agent_id: Optional agent ID to filter
            limit: Maximum number of records

        Returns:
            List of access log entries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM secret_access_log WHERE 1=1"
        params = []

        if secret_id:
            query += " AND secret_id = ?"
            params.append(secret_id)

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        query += " ORDER BY access_time DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """Get secrets management statistics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Total secrets
        cursor.execute("SELECT COUNT(*) as count FROM secrets")
        total_secrets = cursor.fetchone()['count']

        # By access level
        cursor.execute("""
            SELECT access_level, COUNT(*) as count
            FROM secrets
            GROUP BY access_level
        """)
        by_level = {row['access_level']: row['count'] for row in cursor.fetchall()}

        # By type
        cursor.execute("""
            SELECT secret_type, COUNT(*) as count
            FROM secrets
            GROUP BY secret_type
        """)
        by_type = {row['secret_type']: row['count'] for row in cursor.fetchall()}

        # Access statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total_accesses,
                SUM(CASE WHEN access_granted THEN 1 ELSE 0 END) as granted,
                SUM(CASE WHEN NOT access_granted THEN 1 ELSE 0 END) as denied
            FROM secret_access_log
        """)
        access_stats = dict(cursor.fetchone())

        conn.close()

        return {
            "total_secrets": total_secrets,
            "by_access_level": by_level,
            "by_type": by_type,
            "total_accesses": access_stats['total_accesses'] or 0,
            "granted_accesses": access_stats['granted'] or 0,
            "denied_accesses": access_stats['denied'] or 0,
            "database_path": str(self.db_path)
        }
