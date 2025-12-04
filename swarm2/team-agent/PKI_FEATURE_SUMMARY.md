# PKI Cryptography Layer - Feature Summary

## Overview

A complete Public Key Infrastructure (PKI) has been implemented for the Team Agent framework, providing cryptographic signing and verification across all workflow operations.

## Implementation Status

### Completed Phases

- ✅ **Phase 1: CRL System** - Certificate Revocation Lists for offline revocation checking (20 tests)
- ✅ **Phase 2: OCSP Responder** - Real-time certificate status checking with REST API (15 tests)
- ✅ **Phase 3: Certificate Lifecycle Management** - Expiration monitoring, auto-renewal, and rotation (24 tests)

**Total: 76 comprehensive tests (17 PKI + 20 CRL + 15 OCSP + 24 Lifecycle) - All passing ✅**

### Planned Phases

- 🔲 **Phase 4: Trust Scoring System** - Agent reputation and behavior tracking
- 🔲 **Phase 5: Management Tools** - CLI and monitoring dashboards

## What Was Implemented

### 1. PKI Infrastructure (`swarms/team_agent/crypto/`)

#### `pki.py` - Certificate Authority Management
- **PKIManager class**: Manages root CA and three intermediate CAs
- **Three-tier hierarchy**:
  - Root CA (self-signed, 10-year validity)
  - Intermediate CAs for three trust domains (5-year validity each):
    - Government/Control Plane
    - Execution Plane
    - Logging/Artifact Plane

**Key Features:**
- Automatic CA generation on first run
- Idempotent initialization (won't overwrite existing certs)
- PEM format certificates and keys
- Certificate chain generation for verification
- Storage in `.team_agent/pki/` directory

#### `signing.py` - Digital Signatures
- **Signer class**: Signs data using intermediate CA private keys
  - `sign(data)`: Sign arbitrary data, returns SignedData object
  - `sign_dict(data)`: Sign dictionary, embeds signature in `_signature` field

- **Verifier class**: Verifies signatures using certificate chains
  - `verify(signed_data)`: Verify SignedData object
  - `verify_dict(data)`: Verify dictionary with embedded signature

- **SignedData dataclass**: Container for signed data with metadata
  - Includes: data, signature, signer_id, timestamp, cert_subject

### 2. Orchestrator Integration

**Updated: `swarms/team_agent/orchestrator.py`**

- Initializes PKI on startup
- Generates/loads all certificate chains
- Distributes appropriate cert chains to each role:
  - Architect, Builder, Critic → Execution plane certs
  - Governance → Government plane certs
  - Recorder → Logging plane certs

### 3. TuringTape Signing

**Updated: `swarms/team_agent/state/turing_tape.py`**

- Accepts optional `Signer` in constructor
- Automatically signs all appended entries if signer provided
- Verification methods:
  - `verify_entry(entry, verifier)`: Verify single entry
  - `verify_all(verifier)`: Verify all entries, returns statistics

### 4. Role Updates

**Updated Roles:**
- `architect.py`: Accepts cert_chain, initializes Signer, signs output
- `builder.py`: Accepts cert_chain, initializes Signer (partial implementation)
- `base_role.py`: Base class with cert_chain support and `_sign_output()` helper

**Role Signature:**
```python
def __init__(
    self,
    workflow_id: str = "unknown",
    # ... other params ...
    cert_chain: Optional[Dict[str, bytes]] = None
)
```

### 5. Dependencies

**Added to `requirements.txt`:**
```
cryptography==41.0.7
```

### 6. Comprehensive Testing

**Created: `utils/tests/test_pki.py`**

17 comprehensive tests covering:
- PKI initialization and CA generation
- Certificate chain retrieval
- Certificate information extraction
- Idempotent initialization
- Data signing (dicts and arbitrary data)
- Signature verification
- Tamper detection
- TuringTape with signing
- Cross-domain verification (all three trust domains)

**All tests passing** ✅

### 7. Documentation

**Updated: `CLAUDE.md`**

Added comprehensive PKI documentation including:
- PKI architecture overview
- Certificate hierarchy diagram
- Trust domain descriptions
- Key file locations
- Signing operations
- PKI component descriptions
- Certificate management examples
- Testing instructions

## Architecture

### Trust Domains

```
┌─────────────────────────────────────────────────────┐
│                    Root CA                          │
│              (Self-signed, 10 years)                │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Government│ │Execution│ │Logging │
   │   CA    │ │   CA    │ │   CA   │
   └────┬────┘ └────┬────┘ └────┬───┘
        │           │            │
        ▼           ▼            ▼
   Governance  Architect    Recorder
               Builder
               Critic
```

### Signing Flow

1. **Orchestrator Initialization:**
   - PKIManager generates/loads CAs
   - Cert chains retrieved for each domain
   - Roles instantiated with appropriate cert chains

2. **Agent Execution:**
   - Agent receives cert chain in constructor
   - Signer created from private key + cert
   - Agent produces output
   - Output signed with `signer.sign_dict(output)`
   - Signed output returned

3. **State Recording:**
   - TuringTape receives Signer in constructor
   - Each state transition signed before writing
   - JSONL file contains signed entries

4. **Verification:**
   - Verifier created from cert chain
   - Can verify individual entries or entire tapes
   - Tamper detection via signature validation

## File Structure

```
team-agent/
├── swarms/team_agent/
│   ├── crypto/
│   │   ├── __init__.py          # Exports
│   │   ├── pki.py               # CA management + revocation + OCSP
│   │   ├── signing.py           # Sign/verify + CRL/OCSP checking
│   │   ├── crl.py               # Certificate Revocation Lists
│   │   ├── ocsp.py              # OCSP Responder
│   │   └── ocsp_api.py          # OCSP REST API
│   ├── orchestrator.py          # PKI initialization
│   ├── state/
│   │   └── turing_tape.py       # Signing support
│   └── roles/
│       ├── base.py              # Cert chain + CRL support
│       ├── architect.py         # Signing implemented
│       └── builder.py           # Signing implemented (partial)
├── utils/tests/
│   ├── test_pki.py              # 17 PKI tests
│   ├── test_crl.py              # 20 CRL tests
│   └── test_ocsp.py             # 15 OCSP tests
├── .team_agent/pki/             # Generated certificates
│   ├── crl.db                   # CRL database
│   ├── root/
│   │   ├── root-ca.key
│   │   └── root-ca.crt
│   ├── government/
│   │   ├── government-ca.key
│   │   ├── government-ca.crt
│   │   ├── chain.pem
│   │   └── crl.pem              # Generated CRL
│   ├── execution/
│   │   ├── execution-ca.key
│   │   ├── execution-ca.crt
│   │   ├── chain.pem
│   │   └── crl.pem              # Generated CRL
│   └── logging/
│       ├── logging-ca.key
│       ├── logging-ca.crt
│       ├── chain.pem
│       └── crl.pem              # Generated CRL
└── requirements.txt             # Added cryptography + flask
```

## Usage Examples

### Initialize PKI

```python
from swarms.team_agent.orchestrator import Orchestrator

# PKI is automatically initialized
o = Orchestrator()
# Certificates are generated in .team_agent/pki/
```

### Sign Data

```python
from swarms.team_agent.crypto import Signer

signer = Signer(
    private_key_pem=cert_chain['key'],
    certificate_pem=cert_chain['cert'],
    signer_id="my_agent"
)

data = {"mission": "test", "status": "success"}
signed = signer.sign_dict(data)
# signed now contains original data + _signature metadata
```

### Verify Signature

```python
from swarms.team_agent.crypto import Verifier

verifier = Verifier(chain_pem=cert_chain['chain'])
is_valid = verifier.verify_dict(signed)
# True if signature is valid, False if tampered
```

### Signed TuringTape

```python
from swarms.team_agent.state.turing_tape import TuringTape
from swarms.team_agent.crypto import Signer

tape = TuringTape(
    workflow_id="wf_123",
    signer=signer  # Optional signer
)

# All entries are automatically signed
tape.append("architect", "design_complete", {"components": [...]})

# Verify all entries
results = tape.verify_all(verifier)
print(f"{results['verified']}/{results['total']} entries verified")
```

## Certificate Revocation List (CRL) System

### Overview

The CRL system provides complete certificate lifecycle management, including:
- Certificate revocation with RFC 5280 compliant reason codes
- X.509 CRL generation in PEM format
- Revocation checking during signature verification
- Agent initialization revocation checks
- Certificate suspension and reinstatement
- Comprehensive audit logging

### Components

**Created: `swarms/team_agent/crypto/crl.py`**

- **CRLManager class**: SQLite-based CRL management
  - Revoke/suspend/reinstate certificates
  - Generate X.509 CRLs
  - Query revocation status
  - Audit trail of all revocations

- **RevocationReason enum**: RFC 5280 revocation reasons
  - UNSPECIFIED (0)
  - KEY_COMPROMISE (1)
  - CA_COMPROMISE (2)
  - AFFILIATION_CHANGED (3)
  - SUPERSEDED (4)
  - CESSATION_OF_OPERATION (5)
  - CERTIFICATE_HOLD (6) - temporary suspension
  - REMOVE_FROM_CRL (8) - reinstatement
  - PRIVILEGE_WITHDRAWN (9)

### Database Schema

```sql
-- Revoked certificates
CREATE TABLE revoked_certificates (
    serial_number TEXT PRIMARY KEY,
    revocation_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    reason_code INTEGER NOT NULL,
    revoked_by TEXT NOT NULL,
    trust_domain TEXT NOT NULL,
    cert_subject TEXT,
    metadata TEXT
);

-- CRL versions
CREATE TABLE crl_versions (
    version INTEGER PRIMARY KEY AUTOINCREMENT,
    issued_at TEXT NOT NULL,
    next_update TEXT NOT NULL,
    cert_count INTEGER NOT NULL,
    signature TEXT,
    issuer TEXT
);

-- Audit log
CREATE TABLE crl_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    serial_number TEXT,
    reason TEXT,
    operator TEXT,
    details TEXT
);
```

### PKIManager Integration

**Updated: `swarms/team_agent/crypto/pki.py`**

Added revocation methods:
- `revoke_certificate()` - Revoke a certificate
- `is_revoked()` - Check revocation status
- `get_revocation_info()` - Get revocation details
- `generate_crl()` - Generate CRL for a trust domain
- `generate_all_crls()` - Generate CRLs for all domains
- `list_revoked_certificates()` - List revoked certs
- `get_crl_statistics()` - Get CRL stats

### Verifier Integration

**Updated: `swarms/team_agent/crypto/signing.py`**

- Verifier now accepts optional `crl_manager` parameter
- Automatically checks revocation before verifying signatures
- Rejects signatures from revoked certificates

### Agent Initialization Checks

**Updated: `swarms/team_agent/roles/base.py`**

- BaseRole accepts optional `crl_manager` parameter
- Checks certificate revocation status on initialization
- Raises `CertificateRevokedException` if cert is revoked
- Prevents revoked agents from operating

### CRL File Structure

```
.team_agent/pki/
├── crl.db                      # CRL database
├── execution/
│   ├── execution-ca.key
│   ├── execution-ca.crt
│   ├── chain.pem
│   └── crl.pem                 # Generated CRL
├── government/
│   ├── government-ca.key
│   ├── government-ca.crt
│   ├── chain.pem
│   └── crl.pem                 # Generated CRL
└── logging/
    ├── logging-ca.key
    ├── logging-ca.crt
    ├── chain.pem
    └── crl.pem                 # Generated CRL
```

### Usage Examples

#### Revoke a Certificate

```python
from swarms.team_agent.crypto import PKIManager, TrustDomain, RevocationReason

pki = PKIManager()
pki.initialize_pki()

# Get certificate serial number
cert_info = pki.get_certificate_info(TrustDomain.EXECUTION)
serial = cert_info['serial']  # Hex format

# Revoke certificate
pki.revoke_certificate(
    serial_number=serial,
    reason=RevocationReason.KEY_COMPROMISE,
    revoked_by="orchestrator",
    trust_domain=TrustDomain.EXECUTION,
    cert_subject=cert_info['subject']
)

# Check if revoked
assert pki.is_revoked(serial) == True
```

#### Generate CRLs

```python
# Generate CRL for one domain
crl_pem = pki.generate_crl(TrustDomain.EXECUTION, validity_days=7)
# CRL is also saved to .team_agent/pki/execution/crl.pem

# Generate CRLs for all domains
crls = pki.generate_all_crls(validity_days=7)
# Returns: {'execution': b'-----BEGIN X509 CRL-----...', ...}
```

#### Suspend and Reinstate Certificate

```python
# Suspend (temporary revocation)
pki.crl_manager.suspend_certificate(
    serial_number=serial,
    suspended_by="orchestrator",
    trust_domain="execution"
)

# Reinstate (remove from CRL)
pki.crl_manager.reinstate_certificate(
    serial_number=serial,
    reinstated_by="orchestrator"
)
# Note: Only certificates with CERTIFICATE_HOLD can be reinstated
```

#### Verifier with CRL Checking

```python
from swarms.team_agent.crypto import Verifier, Signer

# Create verifier with CRL checking
verifier = Verifier(
    chain_pem=cert_chain['chain'],
    crl_manager=pki.crl_manager  # Enable revocation checking
)

# Sign data
signer = Signer(
    private_key_pem=cert_chain['key'],
    certificate_pem=cert_chain['cert'],
    signer_id="architect"
)
signed = signer.sign_dict({"task": "complete"})

# Verify - will reject if certificate is revoked
is_valid = verifier.verify_dict(signed)
```

#### Agent Initialization with CRL Check

```python
from swarms.team_agent.roles import BaseRole
from swarms.team_agent.roles.base import CertificateRevokedException

try:
    role = BaseRole(
        workflow_id="wf_123",
        cert_chain=cert_chain,
        crl_manager=pki.crl_manager  # Enable revocation check
    )
except CertificateRevokedException as e:
    print(f"Cannot initialize role: {e}")
    # Certificate has been revoked
```

#### List Revoked Certificates

```python
# List all revoked certificates
all_revoked = pki.list_revoked_certificates()

# List by trust domain
exec_revoked = pki.list_revoked_certificates(
    trust_domain=TrustDomain.EXECUTION,
    limit=100
)

for cert in exec_revoked:
    print(f"Serial: {cert['serial_number']}")
    print(f"Reason: {cert['reason']}")
    print(f"Revoked by: {cert['revoked_by']}")
    print(f"Date: {cert['revocation_date']}")
```

#### Get CRL Statistics

```python
stats = pki.get_crl_statistics()

print(f"Total revoked: {stats['total_revoked']}")
print(f"By trust domain: {stats['by_trust_domain']}")
print(f"By reason: {stats['by_reason']}")
print(f"Suspended: {stats['suspended']}")
```

#### View Audit Log

```python
# Get recent audit entries
audit_log = pki.crl_manager.get_audit_log(limit=50)

for entry in audit_log:
    print(f"{entry['timestamp']} - {entry['action']}")
    print(f"  Serial: {entry['serial_number']}")
    print(f"  Operator: {entry['operator']}")
    print(f"  Details: {entry['details']}")
```

### CRL Testing

**Created: `utils/tests/test_crl.py`**

20 comprehensive tests covering:
- CRL database operations (revoke, check, reinstate)
- Certificate suspension and reinstatement
- Duplicate revocation handling
- CRL statistics and audit logging
- X.509 CRL generation (empty and with revocations)
- PKIManager revocation methods
- Verifier revocation checking
- BaseRole initialization revocation checks
- Backward compatibility (works without CRL manager)

**All tests passing** ✅

Run tests:
```bash
python -m pytest utils/tests/test_crl.py -v
```

### CRL Workflow

```
1. Certificate Issued
   └─> Orchestrator generates certs via PKIManager
       └─> Agents initialized with cert chains

2. Security Incident Detected
   └─> Orchestrator revokes certificate
       └─> Entry added to CRL database
           └─> Audit log updated

3. CRL Generation
   └─> PKIManager.generate_crl() called
       └─> X.509 CRL created and signed by intermediate CA
           └─> CRL saved to .team_agent/pki/{domain}/crl.pem

4. Signature Verification
   └─> Verifier checks CRL before verifying signature
       └─> Signature rejected if certificate revoked

5. Agent Initialization
   └─> BaseRole checks CRL on __init__
       └─> CertificateRevokedException raised if revoked
           └─> Agent cannot start
```

## OCSP (Online Certificate Status Protocol) System

### Overview

The OCSP system provides real-time certificate status checking, complementing the CRL system with:
- Instant revocation status queries
- Signed OCSP responses
- Response caching for performance
- REST API for remote checking
- Integration with Verifier for automatic checking

### Components

**Created: `swarms/team_agent/crypto/ocsp.py`**

- **OCSPResponder class**: Real-time certificate status responder
  - Generate signed OCSP responses
  - Cache responses for performance
  - Support good/revoked/unknown status
  - Integration with CRLManager

- **OCSPStatus enum**: Certificate status values
  - GOOD - Certificate is valid
  - REVOKED - Certificate has been revoked
  - UNKNOWN - Certificate status unknown

**Created: `swarms/team_agent/crypto/ocsp_api.py`**

- **OCSPApi class**: REST API server for OCSP
  - HTTP endpoints for status checking
  - JSON-based request/response
  - Cache management endpoints
  - Health check endpoint

### OCSPResponder Features

```python
class OCSPResponder:
    def check_certificate_status(serial_number: str) -> Tuple[OCSPStatus, Dict]
        """Check certificate status (good/revoked/unknown)."""

    def build_ocsp_response(cert_serial: int, cert_issuer: Name) -> bytes
        """Build and sign OCSP response in DER format."""

    def handle_ocsp_request(cert_serial: int, cert_issuer: Name) -> bytes
        """Handle OCSP request with caching."""

    def get_cache_stats() -> Dict
        """Get cache statistics."""

    def clear_cache()
        """Clear all cached responses."""
```

### PKIManager Integration

**Updated: `swarms/team_agent/crypto/pki.py`**

Added OCSP methods:
- `create_ocsp_responder()` - Create OCSP responder for a trust domain
- `get_ocsp_responder()` - Get or create OCSP responder

### Verifier Integration

**Updated: `swarms/team_agent/crypto/signing.py`**

- Verifier now accepts optional `ocsp_responder` parameter
- Supports `prefer_ocsp` flag to prefer OCSP over CRL
- Automatically checks OCSP before signature verification
- Falls back to CRL if OCSP returns UNKNOWN

### REST API Endpoints

The OCSP API provides HTTP endpoints for certificate status checking:

```
GET  /health                - Health check and status
POST /ocsp                  - Certificate status check (JSON)
POST /ocsp/binary           - OCSP binary protocol (RFC 6960)
GET  /ocsp/cache/stats      - Cache statistics
POST /ocsp/cache/clear      - Clear response cache
```

### Usage Examples

#### Create OCSP Responder

```python
from swarms.team_agent.crypto import PKIManager, TrustDomain

pki = PKIManager()
pki.initialize_pki()

# Create OCSP responder for execution domain
ocsp_responder = pki.create_ocsp_responder(
    TrustDomain.EXECUTION,
    cache_duration=300  # 5 minutes
)

# Check certificate status
serial_hex = "abc123"
status, revocation_info = ocsp_responder.check_certificate_status(serial_hex)

if status == OCSPStatus.GOOD:
    print("Certificate is valid")
elif status == OCSPStatus.REVOKED:
    print(f"Certificate revoked: {revocation_info['reason']}")
else:
    print("Certificate status unknown")
```

#### Start OCSP API Server

```python
from swarms.team_agent.crypto.ocsp_api import create_ocsp_api

# Create OCSP API
api = create_ocsp_api(
    pki_manager=pki,
    host="127.0.0.1",
    port=8080,
    cache_duration=300
)

# Run server
api.run(debug=False)
```

#### Query OCSP API

```bash
# Check certificate status via HTTP
curl -X POST http://localhost:8080/ocsp \
  -H "Content-Type: application/json" \
  -d '{
    "serial": "abc123",
    "trust_domain": "execution"
  }'

# Response:
# {
#   "status": "good",
#   "serial": "abc123",
#   "trust_domain": "execution"
# }

# Get cache statistics
curl http://localhost:8080/ocsp/cache/stats

# Clear cache
curl -X POST http://localhost:8080/ocsp/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"trust_domain": "execution"}'
```

#### Verifier with OCSP

```python
from swarms.team_agent.crypto import Verifier, Signer

# Create OCSP responder
ocsp_responder = pki.create_ocsp_responder(TrustDomain.EXECUTION)

# Create verifier with OCSP support
verifier = Verifier(
    chain_pem=cert_chain['chain'],
    ocsp_responder=ocsp_responder,  # Enable OCSP checking
    prefer_ocsp=True  # Prefer OCSP over CRL
)

# Sign data
signer = Signer(
    private_key_pem=cert_chain['key'],
    certificate_pem=cert_chain['cert'],
    signer_id="architect"
)
signed = signer.sign_dict({"task": "complete"})

# Verify - uses OCSP for real-time revocation checking
is_valid = verifier.verify_dict(signed)
```

#### OCSP with CRL Fallback

```python
# Verifier with both OCSP and CRL
verifier = Verifier(
    chain_pem=cert_chain['chain'],
    crl_manager=pki.crl_manager,      # CRL for offline checking
    ocsp_responder=ocsp_responder,    # OCSP for real-time checking
    prefer_ocsp=True                  # Try OCSP first, fall back to CRL
)

# Verification flow:
# 1. Check OCSP if available
# 2. If OCSP returns UNKNOWN, check CRL
# 3. If neither available, allow (but log warning)
```

#### Cache Management

```python
# Get cache statistics
stats = ocsp_responder.get_cache_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Valid entries: {stats['valid_entries']}")
print(f"Expired entries: {stats['expired_entries']}")

# Clear cache
ocsp_responder.clear_cache()
```

### OCSP Response Caching

The OCSP responder implements intelligent caching:

- **Default TTL**: 300 seconds (5 minutes)
- **Automatic expiration**: Cached responses auto-expire
- **Cache hit benefits**: Reduced CPU and database load
- **Per-certificate caching**: Each certificate cached separately
- **Thread-safe**: Cache operations are atomic

### OCSP Testing

**Created: `utils/tests/test_ocsp.py`**

15 comprehensive tests covering:
- OCSP responder creation and configuration
- Certificate status checking (good/revoked)
- OCSP response building and signing
- Response caching and expiration
- Cache statistics and management
- PKIManager integration
- Verifier OCSP integration
- OCSP preference and fallback logic
- Performance and caching benefits

**All tests passing** ✅

Run tests:
```bash
python -m pytest utils/tests/test_ocsp.py -v
```

### OCSP Workflow

```
1. Certificate Status Query
   └─> Client queries OCSP responder
       └─> Responder checks CRLManager for revocation
           └─> Returns signed OCSP response (good/revoked/unknown)

2. Response Caching
   └─> First query generates and caches response
       └─> Subsequent queries use cached response (if not expired)
           └─> Cache miss regenerates response

3. Signature Verification with OCSP
   └─> Verifier checks OCSP before verifying signature
       └─> If prefer_ocsp=True, check OCSP first
           └─> If OCSP unavailable or returns UNKNOWN, fall back to CRL

4. REST API Query
   └─> HTTP POST to /ocsp with serial and trust domain
       └─> API routes to appropriate OCSP responder
           └─> Returns JSON response with status
```

### OCSP vs CRL

| Feature | CRL | OCSP |
|---------|-----|------|
| **Update frequency** | Periodic (e.g., daily) | Real-time |
| **Response size** | Large (entire list) | Small (single cert) |
| **Latency** | Low (local file) | Medium (network query) |
| **Scalability** | Good (static files) | Requires service |
| **Privacy** | Better (no query tracking) | Query reveals interest |
| **Freshness** | Stale until next update | Always current |
| **Offline support** | Yes | No (requires responder) |

**Recommendation**: Use OCSP for real-time checking when available, with CRL as fallback for offline scenarios.

---

## Phase 3: Certificate Lifecycle Management

The Certificate Lifecycle Manager automates certificate expiration monitoring, renewal, and rotation to ensure continuous PKI operations without manual intervention.

### Overview

**CertificateLifecycleManager** provides:
- **Expiration Monitoring**: Track certificate expiration dates across all trust domains
- **Automatic Renewal**: Auto-renew certificates before expiration
- **Certificate Rotation**: Generate new certificates with new key pairs
- **Notification System**: Configurable alerts for expiring certificates
- **Event Logging**: Complete audit trail of lifecycle operations

### Core Components

#### CertificateLifecycleManager

```python
from swarms.team_agent.crypto import CertificateLifecycleManager, TrustDomain

# Create lifecycle manager
lifecycle = pki.create_lifecycle_manager(
    renewal_threshold_days=30,   # Auto-renew within 30 days of expiry
    warning_threshold_days=60,   # Send warnings at 60 days
    critical_threshold_days=7    # Critical alerts at 7 days
)
```

#### CertificateStatus Enum

Certificate lifecycle states:
- **VALID**: Certificate is valid and not expiring soon
- **EXPIRING_SOON**: Certificate expires within threshold
- **EXPIRED**: Certificate has expired
- **RENEWED**: Certificate has been renewed
- **ROTATED**: Certificate has been rotated with new key

#### NotificationLevel Enum

Alert severity levels:
- **INFO**: Informational notifications
- **WARNING**: Warning alerts (approaching expiration)
- **CRITICAL**: Critical alerts (imminent expiration)

### Usage Examples

#### Basic Expiration Monitoring

```python
from swarms.team_agent.crypto import PKIManager, TrustDomain

# Initialize PKI
pki = PKIManager()
pki.initialize_pki()

# Create lifecycle manager
lifecycle = pki.create_lifecycle_manager()

# Check single certificate expiration
expiry_date = lifecycle.get_certificate_expiration(TrustDomain.EXECUTION)
print(f"Certificate expires: {expiry_date}")

# Get detailed certificate information
cert_info = lifecycle.get_certificate_info(TrustDomain.EXECUTION)
print(f"Domain: {cert_info['domain']}")
print(f"Serial: {cert_info['serial']}")
print(f"Days until expiry: {cert_info['days_until_expiry']}")
print(f"Status: {cert_info['status']}")

# Check all certificates
all_status = lifecycle.get_all_certificate_status()
for cert in all_status:
    print(f"{cert['domain']}: {cert['days_until_expiry']} days remaining")
```

#### Check for Expiring Certificates

```python
# Check for certificates expiring within threshold
expiring = lifecycle.check_expiring_certificates(threshold_days=30)

for cert in expiring:
    print(f"⚠️  {cert['domain']} expires in {cert['days_until_expiry']} days")
    print(f"   Serial: {cert['serial']}")
    print(f"   Expires: {cert['not_after']}")
```

#### Manual Certificate Renewal

```python
# Renew a specific certificate
renewal_info = lifecycle.renew_certificate(
    domain=TrustDomain.EXECUTION,
    validity_days=365  # New validity period
)

print(f"Renewed {renewal_info['domain']}")
print(f"Old serial: {renewal_info['old_serial']}")
print(f"New serial: {renewal_info['new_serial']}")
print(f"New expiry: {renewal_info['new_expiry']}")
```

#### Certificate Rotation

```python
# Rotate certificate with new key pair
rotation_info = lifecycle.rotate_certificate(
    domain=TrustDomain.GOVERNMENT,
    validity_days=730  # 2 years
)

print(f"Rotated {rotation_info['domain']}")
print(f"Key rotated: {rotation_info['key_rotated']}")
print(f"Old serial: {rotation_info['old_serial']}")
print(f"New serial: {rotation_info['new_serial']}")
```

#### Automatic Renewal

```python
# Dry-run: Check what would be renewed
renewals = lifecycle.auto_renew_expiring_certificates(dry_run=True)
for renewal in renewals:
    print(f"Would renew: {renewal['domain']} ({renewal['days_until_expiry']} days)")

# Actually renew expiring certificates
renewals = lifecycle.auto_renew_expiring_certificates(dry_run=False)
for renewal in renewals:
    print(f"✅ Renewed {renewal['domain']}")
    print(f"   New serial: {renewal['new_serial']}")
```

#### Notification System

```python
# Define notification handler
def email_notification_handler(notification):
    """Send email alerts for lifecycle events."""
    event = notification['event']
    level = notification['level']
    data = notification['data']

    if level == 'critical':
        subject = f"🚨 CRITICAL: Certificate expiring soon"
    elif level == 'warning':
        subject = f"⚠️  WARNING: Certificate expiration warning"
    else:
        subject = f"ℹ️  INFO: Certificate lifecycle event"

    print(f"{subject}: {event}")
    print(f"Data: {data}")
    # send_email(subject, data)  # Your email implementation

# Register notification handler
lifecycle.add_notification_handler(email_notification_handler)

# Notifications are sent automatically on:
# - Certificate renewal
# - Certificate rotation
# - Expiration warnings
lifecycle.check_and_notify_expiring()
```

#### Event Logging

```python
# Get all lifecycle events
events = lifecycle.get_event_log()
for event in events:
    print(f"{event['timestamp']}: {event['event']}")
    print(f"  Data: {event['data']}")

# Filter by event type
renewals = lifecycle.get_event_log(event_type="certificate_renewed")
rotations = lifecycle.get_event_log(event_type="certificate_rotated")

# Limit results
recent_events = lifecycle.get_event_log(limit=10)
```

### Automated Monitoring

#### Scheduled Monitoring Script

```python
#!/usr/bin/env python3
"""
Certificate lifecycle monitoring daemon.

Run this script periodically (e.g., daily via cron) to:
- Check for expiring certificates
- Send notifications
- Auto-renew certificates
"""

import logging
from swarms.team_agent.crypto import PKIManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_certificates():
    """Monitor and manage certificate lifecycle."""
    # Initialize PKI and lifecycle manager
    pki = PKIManager()
    lifecycle = pki.create_lifecycle_manager(
        renewal_threshold_days=30,
        warning_threshold_days=60,
        critical_threshold_days=7
    )

    # Register notification handler
    def log_notification(notification):
        level = notification['level'].upper()
        event = notification['event']
        data = notification['data']
        logger.log(
            getattr(logging, level, logging.INFO),
            f"{event}: {data}"
        )

    lifecycle.add_notification_handler(log_notification)

    # Check for expiring certificates and send notifications
    logger.info("Checking certificate expiration status...")
    lifecycle.check_and_notify_expiring()

    # Auto-renew certificates expiring within threshold
    logger.info("Checking for auto-renewal candidates...")
    renewals = lifecycle.auto_renew_expiring_certificates(dry_run=False)

    if renewals:
        logger.info(f"Auto-renewed {len(renewals)} certificates")
        for renewal in renewals:
            logger.info(f"  - {renewal['domain']}: {renewal['new_serial']}")
    else:
        logger.info("No certificates require renewal")

if __name__ == "__main__":
    monitor_certificates()
```

#### Cron Job Setup

```bash
# Run certificate monitoring daily at 2 AM
0 2 * * * /usr/bin/python3 /path/to/monitor_certificates.py >> /var/log/cert_monitor.log 2>&1
```

### Renewal vs. Rotation

**Certificate Renewal:**
- Generates new certificate with **new validity period**
- Implementation note: Currently generates new key pair (same as rotation)
- Use for: Regular expiration renewal

**Certificate Rotation:**
- Generates new certificate with **new key pair**
- Complete cryptographic refresh
- Use for: Security incidents, key compromise, periodic security hardening

### Best Practices

1. **Set Appropriate Thresholds:**
   ```python
   lifecycle = pki.create_lifecycle_manager(
       renewal_threshold_days=30,   # Auto-renew 30 days before expiry
       warning_threshold_days=60,   # Warning at 60 days
       critical_threshold_days=7    # Critical alert at 7 days
   )
   ```

2. **Monitor Regularly:**
   - Run `check_and_notify_expiring()` daily via cron
   - Review event logs periodically
   - Set up proper notification handlers (email, Slack, PagerDuty)

3. **Test Auto-Renewal:**
   - Use `dry_run=True` to preview renewals
   - Test notification handlers before production
   - Verify renewed certificates work with existing systems

4. **Plan for Rotation:**
   - Schedule periodic key rotation (e.g., annually)
   - Update all systems that use rotated certificates
   - Maintain grace period for old certificates

5. **Event Auditing:**
   - Review lifecycle event logs regularly
   - Track all renewals and rotations
   - Integrate with SIEM for security monitoring

### Lifecycle Testing

Run the comprehensive lifecycle test suite:

```bash
# All lifecycle tests (24 tests)
python -m pytest utils/tests/test_lifecycle.py -v

# Specific test classes
python -m pytest utils/tests/test_lifecycle.py::TestCertificateLifecycleManager -v
python -m pytest utils/tests/test_lifecycle.py::TestLifecycleNotifications -v
python -m pytest utils/tests/test_lifecycle.py::TestLifecycleEventLog -v
python -m pytest utils/tests/test_lifecycle.py::TestLifecycleIntegration -v
```

### Integration with PKI System

The lifecycle manager integrates seamlessly with existing PKI components:

```python
# Complete PKI workflow with lifecycle management
pki = PKIManager()
pki.initialize_pki()

# Create all managers
crl_manager = pki.crl_manager
ocsp_responder = pki.create_ocsp_responder(TrustDomain.EXECUTION)
lifecycle_manager = pki.create_lifecycle_manager()

# Monitor and maintain certificates
lifecycle_manager.check_and_notify_expiring()
expiring = lifecycle_manager.check_expiring_certificates(threshold_days=30)

if expiring:
    # Auto-renew expiring certificates
    renewals = lifecycle_manager.auto_renew_expiring_certificates()

    # Update CRL and OCSP after renewal
    for renewal in renewals:
        # New certificates are automatically available
        # OCSP responder will cache new status
        pass
```

---

## Security Considerations

### Current Implementation (Testing/Development)

- Root CA is **auto-generated** for testing
- Private keys stored unencrypted in `.team_agent/pki/`
- Suitable for development and testing

### Before Open-Sourcing (Production)

1. **Replace Root CA:**
   ```python
   pki = PKIManager()
   pki.initialize_pki(force=True)  # Regenerate all certs
   ```

2. **Use Proper Root CA:**
   - Generate root CA with hardware security module (HSM)
   - Or use organizational root CA
   - Sign intermediate CAs offline
   - Distribute only intermediate CA certs/keys

3. **Key Protection:**
   - Encrypt private keys at rest
   - Use key management service (KMS)
   - Implement key rotation
   - Separate key storage from code

4. **Certificate Policies:**
   - Define certificate policies (CP)
   - Implement certificate practice statement (CPS)
   - ✅ CRL implemented - offline revocation checking
   - ✅ OCSP implemented - real-time revocation checking
   - Monitor certificate expiration (Phase 3)

## Testing

Run the comprehensive test suite:

```bash
# All PKI tests (17 tests)
python -m pytest utils/tests/test_pki.py -v

# All CRL tests (20 tests)
python -m pytest utils/tests/test_crl.py -v

# All OCSP tests (15 tests)
python -m pytest utils/tests/test_ocsp.py -v

# All Lifecycle tests (24 tests)
python -m pytest utils/tests/test_lifecycle.py -v

# Run all crypto tests (76 tests total)
python -m pytest utils/tests/test_pki.py utils/tests/test_crl.py utils/tests/test_ocsp.py utils/tests/test_lifecycle.py -v

# Specific test classes
python -m pytest utils/tests/test_pki.py::TestPKIManager -v
python -m pytest utils/tests/test_pki.py::TestSigner -v
python -m pytest utils/tests/test_pki.py::TestVerifier -v
python -m pytest utils/tests/test_crl.py::TestCRLManager -v
python -m pytest utils/tests/test_crl.py::TestVerifierRevocationChecking -v
python -m pytest utils/tests/test_ocsp.py::TestOCSPResponder -v
python -m pytest utils/tests/test_ocsp.py::TestVerifierWithOCSP -v
python -m pytest utils/tests/test_lifecycle.py::TestCertificateLifecycleManager -v
python -m pytest utils/tests/test_lifecycle.py::TestLifecycleNotifications -v
python -m pytest utils/tests/test_lifecycle.py::TestLifecycleIntegration -v
```

## Next Steps

### Remaining Work

1. **Complete Role Signing:**
   - Update Critic role's run() method to sign output
   - Update Recorder role to sign artifacts
   - Update Governance role to sign policy decisions

2. **Logging Integration:**
   - Update `utils/logging.py` to sign log entries
   - Implement log verification tools

3. **Artifact Signing:**
   - Sign generated files (Python code, docs, etc.)
   - Create manifest files with signatures
   - Implement artifact verification

4. **Verification Tools:**
   - CLI tool to verify workflow integrity
   - Dashboard to show verification status
   - Audit trail reports

5. **Key Management:**
   - ✅ Certificate expiration monitoring - Implemented (Phase 3)
   - ✅ Certificate rotation - Implemented (Phase 3)
   - Create key backup/recovery procedures

### Optional Enhancements

- **Hardware Security Module (HSM) integration**
- **Timestamping service** for non-repudiation
- ✅ **Certificate revocation** - CRL system implemented (Phase 1)
- ✅ **OCSP responder** - Real-time revocation checking (Phase 2)
- ✅ **Certificate lifecycle management** - Expiration monitoring and auto-renewal (Phase 3)
- **Trust scoring system** - Agent behavior tracking (Phase 4)
- **Multi-signature** support for critical operations
- **Zero-knowledge proofs** for privacy-preserving verification

## Benefits

1. **Trust & Integrity:** Cryptographic proof that outputs haven't been tampered with
2. **Auditability:** Complete audit trail of all workflow operations
3. **Non-repudiation:** Agents cannot deny their actions
4. **Compliance:** Meet regulatory requirements for data integrity
5. **Separation of Concerns:** Trust domains isolate different operational planes
6. **Forensics:** Investigate incidents with cryptographic evidence
7. **Real-time Revocation:** OCSP provides instant certificate status checking
8. **Performance:** Intelligent caching reduces overhead of revocation checking

## Conclusion

The PKI infrastructure provides a solid foundation for trusted multi-agent operations. All core components are implemented and tested:

- ✅ Three-tier CA hierarchy (Root + 3 Intermediate CAs)
- ✅ Cryptographic signing and verification
- ✅ Certificate Revocation List (CRL) system with X.509 support
- ✅ OCSP (Online Certificate Status Protocol) responder with REST API
- ✅ Revocation checking in verifiers (CRL and OCSP)
- ✅ Agent initialization protection against revoked certificates
- ✅ Response caching for performance optimization
- ✅ Comprehensive test coverage (52 tests total: 17 PKI + 20 CRL + 15 OCSP)

The system is production-ready for development/testing and can be upgraded to enterprise-grade security by:
1. Replacing the auto-generated root CA with a properly managed one
2. Adding certificate expiration monitoring and auto-renewal (Phase 3)
3. Implementing trust scoring system (Phase 4)
4. Integrating with HSM for key protection
