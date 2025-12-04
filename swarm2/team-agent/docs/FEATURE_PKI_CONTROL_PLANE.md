# Feature Request: PKI Control Plane in Orchestrator

## Overview

Enhance the Orchestrator to act as a local PKI Control Plane with certificate lifecycle management, including certificate revocation, renewal, and comprehensive audit capabilities.

## Motivation

Currently, the Orchestrator initializes PKI and distributes certificates, but lacks operational certificate management. A full PKI Control Plane is needed for:

- **Certificate Revocation**: Revoke compromised or misbehaving agent certificates
- **Certificate Lifecycle Management**: Renewal, rotation, expiration monitoring
- **Audit & Compliance**: Track all certificate operations
- **Security Incidents**: Respond to security breaches by revoking certificates
- **Agent Accountability**: Enforce trust through certificate management

## Proposed Architecture

### PKI Control Plane Components

```
┌─────────────────────────────────────────────────────────┐
│              Orchestrator PKI Control Plane             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌──────────────────┐          │
│  │ Certificate     │    │ Certificate      │          │
│  │ Revocation List │    │ Lifecycle Mgmt   │          │
│  │ (CRL) Manager   │    │ (Renewal/Expire) │          │
│  └─────────────────┘    └──────────────────┘          │
│                                                         │
│  ┌─────────────────┐    ┌──────────────────┐          │
│  │ OCSP Responder  │    │ Certificate      │          │
│  │ (Online Status) │    │ Audit Logger     │          │
│  └─────────────────┘    └──────────────────┘          │
│                                                         │
│  ┌─────────────────┐    ┌──────────────────┐          │
│  │ Agent Trust     │    │ Emergency        │          │
│  │ Scoring System  │    │ Revocation API   │          │
│  └─────────────────┘    └──────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Certificate Revocation List (CRL)

**Implementation:**
- SQLite-based CRL storage in `.team_agent/pki/crl.db`
- CRL generation in PEM/DER formats
- Distribution to all agents at workflow start
- Periodic CRL updates during long-running workflows

**CRL Schema:**
```sql
CREATE TABLE revoked_certificates (
    serial_number TEXT PRIMARY KEY,
    revocation_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    revoked_by TEXT NOT NULL,
    trust_domain TEXT NOT NULL,
    metadata TEXT
);

CREATE TABLE crl_versions (
    version INTEGER PRIMARY KEY,
    issued_at TEXT NOT NULL,
    next_update TEXT NOT NULL,
    signature TEXT NOT NULL,
    cert_count INTEGER
);
```

**Revocation Reasons:**
- `key_compromise`: Private key exposed
- `ca_compromise`: CA compromise (escalate to root)
- `affiliation_changed`: Agent role/ownership changed
- `superseded`: New certificate issued
- `cessation_of_operation`: Agent decommissioned
- `certificate_hold`: Temporary suspension
- `remove_from_crl`: Reinstate certificate

### 2. OCSP (Online Certificate Status Protocol) Responder

**Implementation:**
- REST API endpoint: `http://localhost:8080/ocsp`
- Real-time certificate status checking
- Response caching for performance
- Signed OCSP responses using CA key

**OCSP Responses:**
- `good`: Certificate valid
- `revoked`: Certificate revoked (with reason and date)
- `unknown`: Certificate not found

**API Endpoint:**
```
POST /ocsp
Content-Type: application/ocsp-request

Returns:
- 200 OK: OCSP response (good/revoked/unknown)
- Signed by intermediate CA
```

### 3. Certificate Lifecycle Management

**Features:**
- **Expiration Monitoring**: Daily checks for certificates within 30 days of expiry
- **Automatic Renewal**: Generate new certificates before expiration
- **Rotation Scheduling**: Planned certificate rotations
- **Grace Periods**: Allow old cert + new cert overlap during rotation

**Lifecycle Events:**
```python
class CertificateLifecycle:
    def check_expiration(self) -> List[ExpiringCert]:
        """Check all certs, return those expiring soon."""

    def renew_certificate(self, serial: str) -> Dict:
        """Issue new certificate for renewal."""

    def rotate_certificate(self, serial: str) -> Dict:
        """Rotate cert with grace period."""

    def notify_expiration(self, cert: Certificate):
        """Send expiration notification."""
```

### 4. Agent Trust Scoring

**Trust Score Calculation:**
- Base score: 100
- Deductions:
  - Signature verification failures: -10 per failure
  - Tampered outputs detected: -25 per incident
  - Policy violations: -15 per violation
  - Expired certificate usage: -50
  - Revoked certificate usage: -100 (immediate revocation)

**Trust Thresholds:**
- 90-100: Trusted
- 70-89: Monitored
- 50-69: Restricted
- 0-49: Suspended (certificate revoked)

**Trust Tracking:**
```sql
CREATE TABLE agent_trust_scores (
    agent_id TEXT PRIMARY KEY,
    serial_number TEXT,
    current_score INTEGER DEFAULT 100,
    incidents TEXT, -- JSON array
    last_incident TEXT,
    last_updated TEXT,
    status TEXT -- trusted/monitored/restricted/suspended
);
```

### 5. Certificate Audit Logger

**Audit Events:**
- Certificate issued
- Certificate renewed
- Certificate revoked
- Certificate expired
- Verification failure
- Trust score change
- CRL published
- OCSP query

**Audit Schema:**
```sql
CREATE TABLE pki_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    serial_number TEXT,
    agent_id TEXT,
    trust_domain TEXT,
    details TEXT,
    operator TEXT,
    signature TEXT
);
```

### 6. Emergency Revocation API

**Orchestrator Methods:**
```python
class Orchestrator:
    def revoke_certificate(
        self,
        serial_number: str,
        reason: str,
        immediate: bool = False
    ) -> Dict:
        """Revoke a certificate immediately."""

    def revoke_agent_certificates(
        self,
        agent_id: str,
        reason: str
    ) -> Dict:
        """Revoke all certificates for an agent."""

    def revoke_trust_domain(
        self,
        domain: TrustDomain,
        reason: str
    ) -> Dict:
        """Emergency: Revoke entire trust domain."""

    def suspend_certificate(
        self,
        serial_number: str,
        duration: int
    ) -> Dict:
        """Temporarily suspend certificate."""

    def reinstate_certificate(
        self,
        serial_number: str
    ) -> Dict:
        """Remove from CRL (certificate hold only)."""
```

## Integration with Roles

### Agent Startup
```python
# Each agent checks certificate status on init
class Architect:
    def __init__(self, workflow_id, cert_chain):
        # Extract serial number from certificate
        self.serial = self._get_serial_from_cert(cert_chain['cert'])

        # Check revocation status
        if orchestrator.is_revoked(self.serial):
            raise CertificateRevokedException(
                f"Certificate {self.serial} has been revoked"
            )

        # Check expiration
        if orchestrator.is_expired(self.serial):
            raise CertificateExpiredException(
                f"Certificate {self.serial} has expired"
            )

        # Initialize signer as before
        self.signer = Signer(...)
```

### Signature Verification
```python
class Verifier:
    def verify_dict(self, data: Dict) -> bool:
        # Extract cert serial from signature
        serial = self._extract_serial(data['_signature'])

        # Check CRL before verifying
        if self.crl_manager.is_revoked(serial):
            return False

        # Check OCSP (optional, for real-time)
        if self.use_ocsp:
            status = self.ocsp_client.check(serial)
            if status != "good":
                return False

        # Verify signature as before
        return self._verify_signature(data)
```

## CLI Commands

### Certificate Management
```bash
# Revoke certificate
python -m team_agent.pki revoke \
    --serial ABC123 \
    --reason key_compromise \
    --immediate

# List certificates
python -m team_agent.pki list \
    --domain execution \
    --status all

# Check certificate status
python -m team_agent.pki status --serial ABC123

# Generate CRL
python -m team_agent.pki crl generate

# View CRL
python -m team_agent.pki crl view

# Renew certificate
python -m team_agent.pki renew --serial ABC123

# Check expiring certificates
python -m team_agent.pki check-expiry --days 30

# View agent trust score
python -m team_agent.pki trust-score --agent architect

# View audit log
python -m team_agent.pki audit --since "2025-12-01"
```

## API Endpoints

### REST API for PKI Operations
```
POST   /api/pki/revoke           - Revoke certificate
POST   /api/pki/renew            - Renew certificate
GET    /api/pki/status/:serial   - Check cert status
GET    /api/pki/crl              - Download CRL
POST   /api/pki/ocsp             - OCSP status check
GET    /api/pki/certificates     - List certificates
GET    /api/pki/trust/:agent     - Get trust score
GET    /api/pki/audit            - Audit log query
POST   /api/pki/suspend          - Suspend certificate
POST   /api/pki/reinstate        - Reinstate certificate
```

## Configuration

### PKI Control Plane Config
```yaml
# .team_agent/pki_config.yaml
pki_control_plane:
  crl:
    enabled: true
    update_interval: 3600  # seconds
    storage: ".team_agent/pki/crl.db"
    format: ["pem", "der"]

  ocsp:
    enabled: true
    port: 8080
    cache_duration: 300  # seconds
    require_nonce: true

  lifecycle:
    expiration_warning_days: 30
    auto_renew: true
    grace_period_days: 7

  trust_scoring:
    enabled: true
    base_score: 100
    revocation_threshold: 50
    monitoring_threshold: 70

  audit:
    enabled: true
    log_location: ".team_agent/pki/audit.jsonl"
    retention_days: 365
    sign_entries: true
```

## Security Considerations

### Access Control
- Only orchestrator can revoke certificates
- Revocation operations require authentication (future: HSM integration)
- CRL and OCSP responses are signed by CA
- Audit log is cryptographically signed

### Performance
- CRL caching with configurable TTL
- OCSP response caching
- Async certificate status checks
- Batch CRL updates

### High Availability
- CRL mirrors for distributed systems (future)
- OCSP responder clustering (future)
- Failover to CRL if OCSP unavailable

## Testing Strategy

### Unit Tests
- CRL generation and parsing
- OCSP request/response handling
- Certificate revocation logic
- Trust score calculation
- Expiration checking

### Integration Tests
- End-to-end revocation workflow
- Agent initialization with revoked cert (should fail)
- Signature verification with revoked cert (should fail)
- Certificate renewal workflow
- Trust score updates

### Security Tests
- Tampered CRL detection
- Invalid OCSP signatures
- Expired certificate handling
- Revoked certificate usage attempts

## Implementation Phases

### Phase 1: Core Revocation (Milestone 1)
- CRL database and storage
- Basic revocation API
- CRL generation
- Agent startup CRL checks

### Phase 2: OCSP Support (Milestone 2)
- OCSP responder implementation
- Real-time status checks
- OCSP response caching
- Integration with verifier

### Phase 3: Lifecycle Management (Milestone 3)
- Expiration monitoring
- Renewal workflows
- Rotation scheduling
- Notification system

### Phase 4: Trust Scoring (Milestone 4)
- Trust score calculation
- Incident tracking
- Automatic revocation triggers
- Trust-based policy enforcement

### Phase 5: Management Tools (Milestone 5)
- CLI commands
- REST API
- Web dashboard (optional)
- Monitoring integration

## Dependencies

- `cryptography`: Already included
- `sqlite3`: Already included (Python stdlib)
- `asn1crypto`: For CRL/OCSP encoding
- `flask` or `fastapi`: For REST API (optional)

## Metrics & Monitoring

### Key Metrics
- Certificates issued/revoked per day
- CRL size and update frequency
- OCSP query rate and response times
- Trust score distribution
- Certificate expiration timeline
- Revocation reasons distribution

### Alerts
- Certificate expiring within 7 days
- Trust score below threshold
- High OCSP query failure rate
- CRL update failures
- Unauthorized revocation attempts

## Documentation

### Administrator Guide
- PKI setup and configuration
- Certificate revocation procedures
- Emergency response playbook
- Backup and recovery procedures

### Developer Guide
- Integrating with PKI control plane
- Custom trust scoring rules
- Extending revocation reasons
- OCSP client implementation

## Success Criteria

1. ✅ Orchestrator can revoke any certificate immediately
2. ✅ Agents with revoked certificates cannot operate
3. ✅ CRL is generated and distributed automatically
4. ✅ OCSP provides real-time status checks
5. ✅ Certificate lifecycle is fully managed
6. ✅ Trust scores influence agent behavior
7. ✅ All PKI operations are audited and signed
8. ✅ CLI and API provide complete management

## Future Enhancements

- Hardware Security Module (HSM) integration
- Distributed CRL with blockchain anchoring
- Advanced trust models (reputation systems)
- Integration with external PKI (X.509 CAs)
- Certificate pinning for critical operations
- Multi-factor authentication for revocations

---

**Status**: Feature Request
**Priority**: High
**Estimated Effort**: 4-6 weeks
**Dependencies**: Existing PKI infrastructure (completed)
