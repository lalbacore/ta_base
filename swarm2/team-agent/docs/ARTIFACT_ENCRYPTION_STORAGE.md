# Artifact Encryption, Signing, and Storage System

**Date:** December 6, 2025
**Version:** 1.0.0
**Status:** Implementation Complete

---

## Overview

Team Agent now supports **encrypted and signed artifact publishing** to multiple storage backends, including:

- **Local Filesystem** (default)
- **IPFS** (InterPlanetary File System)
- **Filecoin** (archival storage on IPFS)

This enhancement addresses the need for:
1. **Cryptographic integrity** - PKI-based signing ensures artifacts haven't been tampered with
2. **Confidentiality** - AES-256-GCM encryption protects sensitive artifacts
3. **Multi-backend storage** - Flexibility to store artifacts on local, distributed, or blockchain-based storage
4. **Future A2A integration** - Foundation for Agent-to-Agent artifact delivery via MCP

---

## Architecture

### Layer 1: Storage Abstraction

**Location:** `backend/app/storage/`

Pluggable storage provider architecture with abstract base class:

```python
class StorageProvider(ABC):
    @abstractmethod
    def store(content: bytes, metadata: ArtifactMetadata, **kwargs) -> StorageResult

    @abstractmethod
    def retrieve(identifier: str, **kwargs) -> Optional[bytes]

    @abstractmethod
    def delete(identifier: str, **kwargs) -> bool

    @abstractmethod
    def exists(identifier: str, **kwargs) -> bool

    @abstractmethod
    def list_artifacts(workflow_id: Optional[str], **kwargs) -> List[Dict[str, Any]]
```

**Implemented Providers:**
- `LocalStorageProvider` - Filesystem storage in `team_output/`
- `IPFSStorageProvider` - IPFS distributed storage (requires IPFS daemon)
- Filecoin support (via IPFS provider with `use_filecoin=True`)

### Layer 2: Cryptography

**Location:** `backend/app/services/artifact_crypto.py`

Provides encryption and signing capabilities:

```python
class ArtifactCrypto:
    def encrypt(content: bytes, encryption_key: Optional[bytes] = None) -> Tuple[bytes, Dict]
    def decrypt(encrypted_content: bytes, encryption_key: bytes, nonce: bytes) -> bytes
    def sign(content: bytes, metadata: Optional[Dict] = None) -> str
    def verify(content: bytes, signature: str, chain_pem: str) -> Tuple[bool, Optional[Dict]]
```

**Encryption:**
- Algorithm: **AES-256-GCM** (Authenticated Encryption with Associated Data)
- Key length: 256 bits (32 bytes)
- Nonce: 96 bits (12 bytes, randomly generated)
- Key derivation: **PBKDF2-HMAC-SHA256** (100,000 iterations) for password-based keys

**Signing:**
- Algorithm: **RSA-PSS with SHA-256**
- Integration: Uses existing PKI infrastructure (`TrustDomain.LOGGING`)
- Signature format: Base64-encoded
- Payload: SHA-256 hash of content + metadata

### Layer 3: Enhanced Artifacts Service

**Location:** `backend/app/services/enhanced_artifacts_service.py`

Orchestrates storage providers and cryptography:

```python
class EnhancedArtifactsService:
    def publish_artifact(
        workflow_id: str,
        artifact_name: str,
        content: bytes,
        storage_backend: str = "local",
        options: PublishOptions = PublishOptions.SIGN,
        encryption_password: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]
```

**Publishing Options:**
- `PublishOptions.NONE` - No encryption or signing (not recommended)
- `PublishOptions.SIGN` - Sign only (default, recommended for public artifacts)
- `PublishOptions.ENCRYPT` - Encrypt only (no signature)
- `PublishOptions.ENCRYPT_AND_SIGN` - Both (recommended for sensitive artifacts)

---

## API Endpoints

### 1. List Available Storage Backends

**GET** `/api/storage/backends`

**Response:**
```json
[
  {
    "storage_type": "local",
    "available": true,
    "info": {
      "name": "LocalStorageProvider",
      "description": "Local filesystem storage provider."
    }
  },
  {
    "storage_type": "ipfs",
    "available": true,
    "info": {
      "name": "IPFSStorageProvider",
      "node_id": "QmXxx...",
      "connected": true
    }
  }
]
```

### 2. Publish Single Artifact (Enhanced)

**POST** `/api/workflow/<workflow_id>/artifact/<artifact_name>/publish-enhanced`

**Request Body:**
```json
{
  "storage_backend": "ipfs",
  "options": "encrypt_and_sign",
  "encryption_password": "secure_password_123",
  "metadata": {
    "project": "Team Agent",
    "classification": "confidential"
  }
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "wf_20251206_120000",
  "artifact_name": "api_implementation.py",
  "storage_backend": "ipfs",
  "storage_identifier": "QmYwAPJzv5CZsnA8M9vFKLxhE5BFdE2qP7Q8K4F5J6Y7Xz",
  "size": 8192,
  "sha256_checksum": "a3f2b1c...",
  "encrypted": true,
  "signed": true,
  "encryption_key": "dGVzdF9lbmNyeXB0aW9uX2tleQ==",
  "warning": "⚠️  SAVE THIS ENCRYPTION KEY! It cannot be recovered if lost.",
  "crypto_metadata": {
    "encryption": {
      "algorithm": "AES-256-GCM",
      "nonce": "cmFuZG9tX25vbmNl",
      "key_id": "e3b0c44298fc1c14",
      "encrypted_size": 8192
    },
    "signature": {
      "algorithm": "RSA-PSS-SHA256",
      "trust_domain": "logging",
      "signature": "eyJhbGc..."
    }
  },
  "storage_metadata": {
    "cid": "QmYwAPJzv5CZsnA8M9vFKLxhE5BFdE2qP7Q8K4F5J6Y7Xz",
    "gateway_url": "http://127.0.0.1:8080/ipfs/QmYwAPJzv...",
    "pinned": true
  }
}
```

**⚠️ CRITICAL:** Save the `encryption_key` value! You'll need it to decrypt the artifact later.

### 3. Publish All Workflow Artifacts

**POST** `/api/workflow/<workflow_id>/publish-all`

**Request Body:**
```json
{
  "storage_backend": "local",
  "options": "sign",
  "encryption_password": null
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "wf_20251206_120000",
  "storage_backend": "local",
  "artifacts_published": 3,
  "results": [
    {
      "success": true,
      "artifact_name": "main.py",
      "storage_identifier": "/path/to/team_output/wf_20251206_120000/main.py",
      "signed": true,
      "encrypted": false
    },
    {
      "success": true,
      "artifact_name": "README.md",
      "storage_identifier": "/path/to/team_output/wf_20251206_120000/README.md",
      "signed": true,
      "encrypted": false
    }
  ],
  "errors": []
}
```

### 4. Retrieve Artifact (with Decryption/Verification)

**POST** `/api/artifact/retrieve`

**Request Body:**
```json
{
  "storage_identifier": "QmYwAPJzv5CZsnA8M9vFKLxhE5BFdE2qP7Q8K4F5J6Y7Xz",
  "storage_backend": "ipfs",
  "encryption_key": "dGVzdF9lbmNyeXB0aW9uX2tleQ==",
  "verify_signature": true,
  "chain_pem": "-----BEGIN CERTIFICATE-----\n..."
}
```

**Response:**
```json
{
  "success": true,
  "storage_identifier": "QmYwAPJzv...",
  "storage_backend": "ipfs",
  "size": 5120,
  "encrypted": true,
  "signed": true,
  "decrypted": true,
  "signature_valid": true,
  "content": "def main():\n    print('Hello, World!')\n",
  "content_encoding": "utf-8",
  "metadata": {
    "workflow_id": "wf_20251206_120000",
    "artifact_name": "api_implementation.py",
    "encrypted": true,
    "signed": true
  }
}
```

### 5. List Workflow Artifacts (Enhanced)

**GET** `/api/workflow/<workflow_id>/artifacts-enhanced?storage_backend=ipfs`

**Response:**
```json
[
  {
    "workflow_id": "wf_20251206_120000",
    "artifact_name": "main.py",
    "storage_type": "ipfs",
    "cid": "QmYwAPJzv...",
    "gateway_url": "http://127.0.0.1:8080/ipfs/QmYwAPJzv...",
    "encrypted": true,
    "signed": true,
    "size": 8192,
    "sha256_checksum": "a3f2b1c..."
  }
]
```

---

## Usage Examples

### Example 1: Publish Signed Artifact to IPFS

```bash
curl -X POST http://localhost:5001/api/workflow/wf_20251206_120000/artifact/main.py/publish-enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "storage_backend": "ipfs",
    "options": "sign",
    "metadata": {
      "project": "Team Agent",
      "version": "1.0.0"
    }
  }'
```

### Example 2: Publish Encrypted Artifact with Password

```bash
curl -X POST http://localhost:5001/api/workflow/wf_20251206_120000/artifact/config.json/publish-enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "storage_backend": "local",
    "options": "encrypt_and_sign",
    "encryption_password": "my_secure_password_123"
  }'
```

**Response includes encryption key:**
```json
{
  "success": true,
  "encryption_key": "kX9zF2mP...",
  "warning": "⚠️  SAVE THIS ENCRYPTION KEY! It cannot be recovered if lost."
}
```

### Example 3: Retrieve and Decrypt Artifact

```bash
curl -X POST http://localhost:5001/api/artifact/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "storage_identifier": "/path/to/team_output/wf_20251206_120000/config.json",
    "storage_backend": "local",
    "encryption_key": "kX9zF2mP...",
    "verify_signature": true
  }'
```

### Example 4: Publish All Workflow Artifacts to Filecoin

```bash
curl -X POST http://localhost:5001/api/workflow/wf_20251206_120000/publish-all \
  -H "Content-Type: application/json" \
  -d '{
    "storage_backend": "filecoin",
    "options": "encrypt_and_sign",
    "encryption_password": "project_password"
  }'
```

---

## Storage Backends

### Local Filesystem

**Status:** ✅ Available (default)

**Configuration:** None required

**Storage Structure:**
```
team_output/
├── wf_20251206_120000/
│   ├── main.py
│   ├── README.md
│   └── .metadata/
│       ├── main.py.json
│       └── README.md.json
```

**Metadata Location:** `team_output/{workflow_id}/.metadata/{artifact_name}.json`

**Identifier Format:** File path (e.g., `/path/to/team_output/wf_20251206_120000/main.py`)

### IPFS (InterPlanetary File System)

**Status:** ⚠️ Requires IPFS daemon

**Prerequisites:**
1. Install IPFS: `brew install ipfs` (macOS) or see [ipfs.io](https://ipfs.io)
2. Initialize IPFS: `ipfs init`
3. Start daemon: `ipfs daemon`
4. Install Python client: `pip install ipfshttpclient`

**Configuration:**
- API endpoint: `/ip4/127.0.0.1/tcp/5001` (default)
- Gateway URL: `http://127.0.0.1:8080/ipfs/` (default)

**Storage Format:**
- Content stored as IPFS object
- Returns **CID** (Content Identifier): `QmYwAPJzv5CZsnA8M9vFKLxhE5BFdE2qP7Q8K4F5J6Y7Xz`
- Metadata stored in in-memory index (can be persisted)

**Identifier Format:** CID (e.g., `QmYwAPJzv5CZsnA8M9vFKLxhE5BFdE2qP7Q8K4F5J6Y7Xz`)

**Advantages:**
- **Content-addressed** - CID is deterministic hash of content
- **Distributed** - Content replicated across IPFS network
- **Immutable** - Content cannot be changed without changing CID
- **Censorship-resistant** - No central server

**Pinning:** Artifacts are automatically pinned to prevent garbage collection.

### Filecoin

**Status:** 🚧 Partial Support (IPFS backend ready, Filecoin deals pending)

**Prerequisites:**
- IPFS daemon (same as IPFS)
- Filecoin storage provider integration (future)

**Storage Flow:**
1. Content stored to IPFS (returns CID)
2. CID submitted to Filecoin storage provider
3. Storage deal created on Filecoin blockchain
4. Content archived on Filecoin network

**Current Implementation:**
- Uses `IPFSStorageProvider` with `use_filecoin=True`
- IPFS storage works immediately
- Filecoin deal creation is placeholder (returns stub response)

**Future Integration:**
- Web3.Storage API integration
- Estuary storage provider
- Lotus client for direct Filecoin deals

---

## Security Considerations

### Encryption Keys

**⚠️ CRITICAL:** Encryption keys are **NOT stored** by Team Agent. You must save them securely!

**Best Practices:**
1. **Save immediately** - Copy the `encryption_key` from the response
2. **Secure storage** - Use password manager or secrets vault (e.g., 1Password, Vault)
3. **Backup** - Store keys in multiple secure locations
4. **Rotation** - Re-encrypt artifacts periodically with new keys
5. **Access control** - Limit who can access encryption keys

**Key Derivation from Passwords:**
- If you provide `encryption_password`, the key is derived using PBKDF2
- You can decrypt later using the same password
- Password strength matters! Use strong, unique passwords

### Signature Verification

**Trust Domains:**
- Artifacts are signed using `TrustDomain.LOGGING` PKI certificates
- Signatures verify both **content integrity** and **origin authenticity**

**Verification Process:**
1. Get certificate chain PEM from PKI manager
2. Pass `chain_pem` to retrieve endpoint
3. Verifier checks signature against certificate chain
4. Returns `signature_valid: true/false`

**Example:**
```python
from swarms.team_agent.crypto import PKIManager, TrustDomain

pki = PKIManager()
chain = pki.get_chain(TrustDomain.LOGGING)
chain_pem = chain['chain']

# Use chain_pem in retrieve request
```

### Content-Addressed Storage (IPFS/Filecoin)

**Advantages:**
- **Tamper-evident** - Any change to content changes the CID
- **Verifiable** - Can re-hash content to verify CID matches
- **Deduplication** - Identical content has same CID (automatic deduplication)

**Limitations:**
- **Public by default** - IPFS content is publicly accessible via gateways
- **Use encryption** - Always encrypt sensitive content before IPFS storage
- **Gateway trust** - When retrieving via gateway, verify signature

---

## Performance Considerations

### Local Storage
- **Speed:** ⚡ Fastest (direct filesystem I/O)
- **Scalability:** Limited by disk space
- **Redundancy:** None (single point of failure)

### IPFS
- **Speed:** 🐢 Slower (network I/O, DHT lookups)
- **First publish:** ~1-3 seconds
- **Retrieval:** Variable (depends on peers, content popularity)
- **Scalability:** Excellent (distributed)
- **Redundancy:** High (replicated across peers)

### Filecoin
- **Speed:** 🐢 Slowest (blockchain storage deals)
- **Deal creation:** Minutes to hours
- **Retrieval:** Fast (via IPFS gateway)
- **Scalability:** Excellent (blockchain-backed)
- **Redundancy:** Very high (storage proofs, redundancy built-in)

### Encryption Overhead
- **AES-256-GCM:** Negligible (<1% CPU overhead for typical artifacts)
- **Key derivation (PBKDF2):** ~100ms (100,000 iterations)
- **Signing (RSA-PSS):** ~10-50ms per artifact

**Recommendation:** Use encryption for all sensitive artifacts; performance impact is minimal.

---

## Future Enhancements

### Phase 3: MCP Server Integration

**Goal:** Expose artifact storage operations as MCP tools for A2A delivery

**Planned Tools:**
1. `publish_artifact` - Publish artifact to any backend
2. `retrieve_artifact` - Retrieve and decrypt artifact
3. `verify_artifact` - Verify signature
4. `list_storage_backends` - Query available backends
5. `transfer_artifact` - Copy artifact between backends

**A2A Use Cases:**
- Agent A publishes artifact to IPFS, sends CID to Agent B
- Agent B retrieves artifact from IPFS using CID
- Agent B verifies signature using Agent A's certificate chain
- Agent B decrypts artifact using shared key

**Example MCP Tool Definition:**
```json
{
  "name": "publish_artifact",
  "description": "Publish artifact with encryption and signing",
  "parameters": {
    "workflow_id": "string",
    "artifact_name": "string",
    "storage_backend": "local|ipfs|filecoin",
    "options": "none|sign|encrypt|encrypt_and_sign"
  },
  "returns": {
    "storage_identifier": "string",
    "encryption_key": "string (if encrypted)",
    "signature": "string (if signed)"
  }
}
```

### Additional Storage Providers

**Potential Integrations:**
- **AWS S3** - Enterprise cloud storage
- **Arweave** - Permanent storage blockchain
- **Google Cloud Storage** - Multi-cloud support
- **Azure Blob Storage** - Microsoft cloud integration

### Advanced Features

1. **Key Management Service (KMS):**
   - Integration with cloud KMS (AWS KMS, Google Cloud KMS)
   - Hardware Security Module (HSM) support
   - Key rotation automation

2. **Multi-recipient Encryption:**
   - Encrypt artifact once, allow multiple recipients to decrypt
   - Use hybrid encryption (RSA + AES)
   - Certificate-based access control

3. **Audit Logging:**
   - Log all publish/retrieve operations
   - Track who accessed which artifacts when
   - Integration with SIEM (ELK stack)

4. **Content Deduplication:**
   - Detect duplicate artifacts before publishing
   - Reference existing CIDs instead of re-uploading
   - Save storage space and bandwidth

---

## Testing

### Manual Testing

**1. Test Local Storage with Signing:**
```bash
# Publish artifact
curl -X POST http://localhost:5001/api/workflow/wf_test/artifact/test.py/publish-enhanced \
  -H "Content-Type: application/json" \
  -d '{"storage_backend": "local", "options": "sign"}'

# Expected: success=true, signed=true, storage_identifier=file path
```

**2. Test Encryption:**
```bash
# Publish encrypted artifact
curl -X POST http://localhost:5001/api/workflow/wf_test/artifact/secret.txt/publish-enhanced \
  -H "Content-Type: application/json" \
  -d '{"storage_backend": "local", "options": "encrypt", "encryption_password": "test123"}'

# Expected: success=true, encrypted=true, encryption_key returned

# Retrieve and decrypt
curl -X POST http://localhost:5001/api/artifact/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "storage_identifier": "<path from publish response>",
    "storage_backend": "local",
    "encryption_key": "<key from publish response>"
  }'

# Expected: success=true, decrypted=true, content returned
```

**3. Test IPFS (requires IPFS daemon):**
```bash
# Check IPFS availability
curl http://localhost:5001/api/storage/backends

# Publish to IPFS
curl -X POST http://localhost:5001/api/workflow/wf_test/artifact/hello.txt/publish-enhanced \
  -H "Content-Type: application/json" \
  -d '{"storage_backend": "ipfs", "options": "sign"}'

# Expected: success=true, storage_identifier=CID, gateway_url provided
```

### Automated Testing

**Create test suite:** `utils/tests/test_enhanced_artifacts.py`

```python
import pytest
from backend.app.services.enhanced_artifacts_service import EnhancedArtifactsService, PublishOptions

def test_publish_signed_artifact():
    service = EnhancedArtifactsService()
    result = service.publish_artifact(
        workflow_id="wf_test",
        artifact_name="test.py",
        content=b"print('Hello')",
        storage_backend="local",
        options=PublishOptions.SIGN
    )
    assert result['success'] == True
    assert result['signed'] == True
    assert result['encrypted'] == False

def test_publish_encrypted_artifact():
    service = EnhancedArtifactsService()
    result = service.publish_artifact(
        workflow_id="wf_test",
        artifact_name="secret.txt",
        content=b"secret content",
        storage_backend="local",
        options=PublishOptions.ENCRYPT
    )
    assert result['success'] == True
    assert result['encrypted'] == True
    assert 'encryption_key' in result

def test_encrypt_decrypt_roundtrip():
    service = EnhancedArtifactsService()

    # Publish encrypted
    publish_result = service.publish_artifact(
        workflow_id="wf_test",
        artifact_name="roundtrip.txt",
        content=b"test content",
        storage_backend="local",
        options=PublishOptions.ENCRYPT
    )

    # Retrieve and decrypt
    retrieve_result = service.retrieve_artifact(
        storage_identifier=publish_result['storage_identifier'],
        storage_backend="local",
        encryption_key=publish_result['encryption_key']
    )

    assert retrieve_result['success'] == True
    assert retrieve_result['content'] == b"test content"
```

---

## Troubleshooting

### Issue: IPFS provider unavailable

**Symptoms:**
```json
{
  "success": false,
  "error": "Storage backend ipfs not available"
}
```

**Solution:**
1. Check IPFS daemon is running: `ipfs daemon`
2. Verify IPFS API is accessible: `curl http://127.0.0.1:5001/api/v0/id`
3. Install Python client: `pip install ipfshttpclient`
4. Restart backend: `cd backend && python app.py`

### Issue: Decryption failed

**Symptoms:**
```json
{
  "success": false,
  "error": "Decryption failed: Invalid key or corrupted data"
}
```

**Solution:**
1. Verify you're using the correct encryption key (from publish response)
2. Check that the artifact was actually encrypted (metadata shows `encrypted: true`)
3. Ensure encryption key is valid base64
4. Verify artifact hasn't been corrupted (check checksum)

### Issue: Signature verification failed

**Symptoms:**
```json
{
  "success": true,
  "signature_valid": false,
  "warning": "⚠️  Signature verification failed!"
}
```

**Solution:**
1. Verify you're using the correct certificate chain PEM
2. Check that the certificate is from the correct trust domain (`TrustDomain.LOGGING`)
3. Ensure artifact content hasn't been modified (re-hash and compare)
4. Verify PKI certificates are still valid (not expired)

---

## Summary

Team Agent's artifact encryption, signing, and storage system provides:

✅ **Cryptographic Integrity** - PKI-based signing ensures artifacts are authentic
✅ **Confidentiality** - AES-256-GCM encryption protects sensitive data
✅ **Flexibility** - Pluggable storage backends (local, IPFS, Filecoin)
✅ **Future-Ready** - Foundation for A2A delivery via MCP
✅ **Production-Grade** - Industry-standard algorithms and best practices

**Next Steps:**
1. Test enhanced artifact publishing with different backends
2. Implement frontend UI for storage backend selection
3. Add encryption toggle to publish dialogs
4. Plan Phase 3: MCP server integration for A2A delivery

**Files Modified/Created:**
- ✅ `backend/app/storage/base.py` - Storage provider interface
- ✅ `backend/app/storage/local.py` - Local filesystem provider
- ✅ `backend/app/storage/ipfs.py` - IPFS provider
- ✅ `backend/app/services/artifact_crypto.py` - Encryption/signing utilities
- ✅ `backend/app/services/enhanced_artifacts_service.py` - Enhanced service
- ✅ `backend/app/api/artifacts.py` - Enhanced API endpoints
- ✅ `docs/ARTIFACT_ENCRYPTION_STORAGE.md` - This documentation

For questions or issues, see GitHub issues or contact the Team Agent development team.
