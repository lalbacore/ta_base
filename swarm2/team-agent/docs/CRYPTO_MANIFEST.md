# Crypto Manifest - PKI Mesh Journey Tracker

**Date:** December 6, 2025
**Version:** 1.0.0
**Status:** Implementation Complete

---

## Overview

The **Crypto Manifest** system provides complete cryptographic traceability for Team Agent workflows by tracking their journey through the PKI mesh. Using the Turing Tape as the immutable source of truth, it shows:

- **Which trust domains signed each stage** (GOVERNMENT, EXECUTION, LOGGING)
- **Complete chain of custody** from mission creation to artifact publishing
- **Signature verification status** for every workflow transition
- **PKI mesh topology** and trust relationships
- **Weak links or breaks** in the cryptographic chain
- **Displayable/loggable format** for audit and compliance

This replaces static PKI diagrams with a **live, verifiable audit trail** that can be queried at any time.

---

## Architecture

### Source of Truth: Turing Tape

All workflow state transitions are recorded in the Turing Tape (`.team_agent/tape/{workflow_id}.jsonl`):

```json
{
  "ts": "2025-12-06T12:00:00Z",
  "agent": "architect",
  "workflow_id": "wf_20251206_120000",
  "event": "architect_complete",
  "state": { "architecture": {...} },
  "_signature": {
    "algorithm": "RSA-PSS-SHA256",
    "timestamp": "2025-12-06T12:00:01Z",
    "signer_id": "execution_plane",
    "signature": "base64_encoded_signature..."
  }
}
```

### Trust Domains → Agent Roles Mapping

| Agent Role | Trust Domain | Certificate Chain | Purpose |
|------------|--------------|-------------------|---------|
| **Orchestrator** | GOVERNMENT | `government-ca.chain.pem` | Policy enforcement |
| **Architect** | EXECUTION | `execution-ca.chain.pem` | Design work |
| **Builder** | EXECUTION | `execution-ca.chain.pem` | Implementation |
| **Critic** | EXECUTION | `execution-ca.chain.pem` | Code review |
| **Recorder** | LOGGING | `logging-ca.chain.pem` | Artifact publishing |
| **Governance** | GOVERNMENT | `government-ca.chain.pem` | Compliance |

### Workflow PKI Journey

```
Mission Start
     ↓  [GOVERNMENT] Orchestrator signs
Orchestrator Stage ✓
     ↓  [EXECUTION] Architect signs
Architect Stage ✓
     ↓  [EXECUTION] Builder signs
Builder Stage ✓
     ↓  [EXECUTION] Critic signs
Critic Stage ✓
     ↓  [LOGGING] Recorder signs
Recorder Stage ✓
     ↓  [LOGGING] Artifacts signed
Artifacts Published ✓
```

Each stage:
1. **Verifies** the previous stage's signature
2. **Performs** its work
3. **Signs** the updated state with its trust domain certificate
4. **Appends** to the Turing Tape

---

## API Endpoints

### 1. Get Complete Crypto Manifest

**GET** `/api/crypto-chain/workflow/<workflow_id>/manifest`

**Response:**
```json
{
  "workflow_id": "wf_20251206_120000",
  "generated_at": "2025-12-06T12:30:00Z",
  "total_entries": 7,
  "timeline": [
    {
      "index": 0,
      "timestamp": "2025-12-06T12:00:00Z",
      "agent": "orchestrator",
      "event": "mission_start",
      "trust_domain": "government",
      "signed": true,
      "signature_valid": true,
      "signature_metadata": {
        "algorithm": "RSA-PSS-SHA256",
        "signer_id": "government_plane"
      },
      "state_summary": {
        "mission": "Build a REST API for user authentication"
      }
    },
    {
      "index": 1,
      "timestamp": "2025-12-06T12:01:30Z",
      "agent": "architect",
      "event": "architect_complete",
      "trust_domain": "execution",
      "signed": true,
      "signature_valid": true,
      "signature_metadata": {
        "algorithm": "RSA-PSS-SHA256",
        "signer_id": "execution_plane"
      }
    }
    // ... more entries
  ],
  "trust_flow": [
    {
      "trust_domain": "government",
      "timestamp": "2025-12-06T12:00:00Z",
      "agent": "orchestrator",
      "event": "mission_start",
      "signed": true,
      "signature_valid": true
    },
    {
      "trust_domain": "execution",
      "timestamp": "2025-12-06T12:01:30Z",
      "agent": "architect",
      "event": "architect_complete",
      "signed": true,
      "signature_valid": true
    }
    // ... more trust domain transitions
  ],
  "pki_mesh": {
    "nodes": [
      {
        "id": "government",
        "label": "GOVERNMENT",
        "type": "trust_domain",
        "statistics": {
          "total_entries": 2,
          "signed_entries": 2,
          "verified_entries": 2,
          "invalid_signatures": 0,
          "unsigned_entries": 0
        },
        "integrity_score": 100.0
      },
      {
        "id": "execution",
        "label": "EXECUTION",
        "type": "trust_domain",
        "statistics": {
          "total_entries": 3,
          "signed_entries": 3,
          "verified_entries": 3,
          "invalid_signatures": 0,
          "unsigned_entries": 0
        },
        "integrity_score": 100.0
      },
      {
        "id": "logging",
        "label": "LOGGING",
        "type": "trust_domain",
        "statistics": {
          "total_entries": 2,
          "signed_entries": 2,
          "verified_entries": 2,
          "invalid_signatures": 0,
          "unsigned_entries": 0
        },
        "integrity_score": 100.0
      }
    ],
    "edges": [
      {
        "from": "government",
        "to": "execution",
        "timestamp": "2025-12-06T12:01:30Z",
        "verified": true
      },
      {
        "from": "execution",
        "to": "logging",
        "timestamp": "2025-12-06T12:05:00Z",
        "verified": true
      }
    ]
  },
  "integrity": {
    "status": "verified",
    "status_message": "All stages present and cryptographically verified",
    "integrity_score": 100.0,
    "chain_complete": true,
    "all_signatures_valid": true,
    "statistics": {
      "total_entries": 7,
      "signed_entries": 7,
      "verified_entries": 7,
      "invalid_entries": 0,
      "unsigned_entries": 0
    },
    "missing_stages": []
  },
  "weak_links": [],
  "displayable_chain": [
    "================================================================================",
    "CRYPTOGRAPHIC CHAIN MANIFEST",
    "================================================================================",
    "",
    "Trust Domain Flow:",
    "--------------------------------------------------------------------------------",
    "1. [GOVERNMENT] orchestrator - mission_start",
    "   ✓ SIGNED ✓ VERIFIED",
    "   Timestamp: 2025-12-06T12:00:00Z",
    "",
    "2. [EXECUTION] architect - architect_complete",
    "   ✓ SIGNED ✓ VERIFIED",
    "   Timestamp: 2025-12-06T12:01:30Z",
    ""
    // ... more displayable entries
  ]
}
```

### 2. Get Displayable Text Format

**GET** `/api/crypto-chain/workflow/<workflow_id>/manifest/text`

**Response:** (text/plain)
```
================================================================================
CRYPTOGRAPHIC CHAIN MANIFEST
================================================================================

Trust Domain Flow:
--------------------------------------------------------------------------------
1. [GOVERNMENT] orchestrator - mission_start
   ✓ SIGNED ✓ VERIFIED
   Timestamp: 2025-12-06T12:00:00Z

2. [EXECUTION] architect - architect_complete
   ✓ SIGNED ✓ VERIFIED
   Timestamp: 2025-12-06T12:01:30Z

3. [EXECUTION] builder - builder_complete
   ✓ SIGNED ✓ VERIFIED
   Timestamp: 2025-12-06T12:03:00Z

4. [EXECUTION] critic - critic_complete
   ✓ SIGNED ✓ VERIFIED
   Timestamp: 2025-12-06T12:04:00Z

5. [LOGGING] recorder - recorder_complete
   ✓ SIGNED ✓ VERIFIED
   Timestamp: 2025-12-06T12:05:00Z

================================================================================
Detailed Timeline:
--------------------------------------------------------------------------------
[2025-12-06T12:00:00Z] orchestrator (GOVERNMENT)
  Event: mission_start
  Signed: True
  Verified: True
  Signature: RSA-PSS-SHA256

[2025-12-06T12:01:30Z] architect (EXECUTION)
  Event: architect_complete
  Signed: True
  Verified: True
  Signature: RSA-PSS-SHA256

================================================================================
```

### 3. Get Trust Flow Only

**GET** `/api/crypto-chain/workflow/<workflow_id>/trust-flow`

**Response:**
```json
{
  "workflow_id": "wf_20251206_120000",
  "trust_flow": [
    {
      "trust_domain": "government",
      "timestamp": "2025-12-06T12:00:00Z",
      "agent": "orchestrator",
      "event": "mission_start",
      "signed": true,
      "signature_valid": null
    }
    // ... more trust domain transitions
  ],
  "pki_mesh": {
    "nodes": [...],
    "edges": [...]
  }
}
```

### 4. Get Integrity Status

**GET** `/api/crypto-chain/workflow/<workflow_id>/integrity`

**Response:**
```json
{
  "workflow_id": "wf_20251206_120000",
  "integrity": {
    "status": "verified",
    "integrity_score": 100.0,
    "chain_complete": true,
    "all_signatures_valid": true,
    "statistics": {
      "total_entries": 7,
      "signed_entries": 7,
      "verified_entries": 7,
      "invalid_entries": 0,
      "unsigned_entries": 0
    }
  },
  "weak_links": []
}
```

---

## Integrity Status Values

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **verified** | All stages present, all signatures valid | ✅ None - workflow is cryptographically sound |
| **partial** | All stages present, some signatures valid | ⚠️ Investigate unsigned/invalid entries |
| **incomplete_signatures** | All stages present, no valid signatures | ❌ Review PKI configuration and signing |
| **incomplete_chain** | Missing workflow stages | ❌ Workflow did not complete all stages |

---

## Weak Link Types

### 1. Unsigned Entry

**Severity:** High

**Example:**
```json
{
  "type": "unsigned_entry",
  "severity": "high",
  "timestamp": "2025-12-06T12:03:00Z",
  "agent": "builder",
  "event": "builder_complete",
  "message": "Entry not cryptographically signed",
  "remediation": "Ensure Signer is configured for this agent's trust domain"
}
```

**Causes:**
- Signer not initialized for agent's trust domain
- Certificate chain not available
- PKI system not initialized

**Remediation:**
```python
# Ensure agents have signers configured
from swarms.team_agent.crypto import Signer, TrustDomain

signer = Signer(trust_domain=TrustDomain.EXECUTION)
tape = TuringTape(workflow_id="wf_xxx", signer=signer)
```

### 2. Invalid Signature

**Severity:** Critical

**Example:**
```json
{
  "type": "invalid_signature",
  "severity": "critical",
  "timestamp": "2025-12-06T12:03:00Z",
  "agent": "builder",
  "event": "builder_complete",
  "message": "Signature verification failed - entry may be tampered",
  "remediation": "Investigate entry integrity and certificate chain"
}
```

**Causes:**
- Entry was tampered with after signing
- Wrong certificate chain used for verification
- Certificate expired or revoked
- Signature algorithm mismatch

**Remediation:**
1. Check certificate validity: `openssl x509 -in cert.pem -noout -text`
2. Verify certificate chain matches trust domain
3. Check for file corruption in Turing Tape
4. Review PKI certificate expiration dates

### 3. Missing Stage

**Severity:** Medium

**Example:**
```json
{
  "type": "missing_stage",
  "severity": "medium",
  "stage": "critic",
  "message": "Expected workflow stage 'critic' not found in tape",
  "remediation": "Verify workflow completed all stages successfully"
}
```

**Causes:**
- Workflow failed before completing all stages
- Agent crashed or timed out
- Turing Tape not properly initialized
- Event name mismatch

**Remediation:**
1. Review workflow logs for errors
2. Check orchestrator execution
3. Verify all agents ran successfully
4. Ensure event names match expected stages

### 4. Missing Trust Domain

**Severity:** Low

**Example:**
```json
{
  "type": "missing_trust_domain",
  "severity": "low",
  "trust_domain": "logging",
  "message": "No entries from logging trust domain",
  "remediation": "Verify workflow uses agents from logging trust domain"
}
```

**Causes:**
- Workflow doesn't use all trust domains (e.g., no governance checks)
- Recorder stage skipped
- Artifacts not published

**Remediation:**
- Review workflow design
- Ensure recorder stage executes
- Check if governance layer is required

---

## Usage Examples

### Example 1: View Crypto Manifest in Terminal

```bash
curl http://localhost:5001/api/crypto-chain/workflow/wf_20251206_120000/manifest/text
```

**Output:**
```
================================================================================
CRYPTOGRAPHIC CHAIN MANIFEST
================================================================================

Trust Domain Flow:
--------------------------------------------------------------------------------
1. [GOVERNMENT] orchestrator - mission_start
   ✓ SIGNED ✓ VERIFIED
   Timestamp: 2025-12-06T12:00:00Z

2. [EXECUTION] architect - architect_complete
   ✓ SIGNED ✓ VERIFIED
   Timestamp: 2025-12-06T12:01:30Z

...
```

### Example 2: Check Workflow Integrity

```bash
curl http://localhost:5001/api/crypto-chain/workflow/wf_20251206_120000/integrity | jq
```

**Output:**
```json
{
  "workflow_id": "wf_20251206_120000",
  "integrity": {
    "status": "verified",
    "integrity_score": 100.0,
    "chain_complete": true,
    "all_signatures_valid": true
  },
  "weak_links": []
}
```

### Example 3: View Trust Domain Flow

```bash
curl http://localhost:5001/api/crypto-chain/workflow/wf_20251206_120000/trust-flow | jq '.trust_flow'
```

**Output:**
```json
[
  {
    "trust_domain": "government",
    "timestamp": "2025-12-06T12:00:00Z",
    "agent": "orchestrator",
    "event": "mission_start",
    "signed": true,
    "signature_valid": true
  },
  {
    "trust_domain": "execution",
    "timestamp": "2025-12-06T12:01:30Z",
    "agent": "architect",
    "event": "architect_complete",
    "signed": true,
    "signature_valid": true
  }
]
```

### Example 4: Programmatic Access

```python
import requests

# Get crypto manifest
response = requests.get('http://localhost:5001/api/crypto-chain/workflow/wf_20251206_120000/manifest')
manifest = response.json()

# Check integrity
if manifest['integrity']['status'] == 'verified':
    print(f"✅ Workflow cryptographically verified - Score: {manifest['integrity']['integrity_score']}")
else:
    print(f"❌ Workflow integrity compromised: {manifest['integrity']['status_message']}")
    for weak_link in manifest['weak_links']:
        print(f"  - {weak_link['type']}: {weak_link['message']}")

# Display trust flow
print("\nTrust Domain Flow:")
for flow in manifest['trust_flow']:
    status = "✓" if flow['signature_valid'] else "✗"
    print(f"  {status} [{flow['trust_domain'].upper()}] {flow['agent']} - {flow['event']}")
```

---

## Compliance and Audit

The Crypto Manifest provides complete audit trails for compliance requirements:

### SOC 2 Compliance
- **Control:** Access logs and monitoring
- **Evidence:** Complete cryptographic chain of custody for all workflows
- **Verification:** Signature verification confirms data integrity

### GDPR Compliance
- **Control:** Data processing records
- **Evidence:** Timestamped record of which agents processed data
- **Verification:** Trust domain assignments show compliance controls

### HIPAA Compliance
- **Control:** Audit controls and integrity controls
- **Evidence:** Cryptographic proof of data integrity and access
- **Verification:** Signature verification confirms no tampering

### ISO 27001 Compliance
- **Control:** A.12.4.1 Event logging, A.12.4.3 Administrator logs
- **Evidence:** Complete audit trail with cryptographic signatures
- **Verification:** Trust domain mesh shows proper separation of duties

---

## Frontend Integration

The Crypto Manifest can be visualized in the frontend with:

### 1. Timeline View
- Chronological display of all workflow stages
- Color-coded by trust domain (Government = blue, Execution = green, Logging = orange)
- Icons showing signature status (✓ verified, ✗ invalid, ○ unsigned)

### 2. Trust Flow Diagram
- Visual graph showing trust domain transitions
- Nodes = trust domains with integrity scores
- Edges = transitions with verification status
- Highlight weak links in red

### 3. Integrity Dashboard
- Overall integrity score (0-100) with gauge visualization
- Chain completeness indicator
- Weak links panel with remediation suggestions
- Export button for audit reports

### 4. Detailed Inspector
- Expandable entries showing full Turing Tape records
- Signature metadata with algorithm and timestamp
- State summaries for each stage
- Raw JSON view for debugging

---

## Future Enhancements

### 1. Real-Time Monitoring
- WebSocket updates for live crypto manifest tracking
- Alert notifications for integrity violations
- Dashboard showing active workflows' integrity status

### 2. Compliance Reports
- Automated compliance report generation (SOC 2, HIPAA, ISO 27001)
- PDF export with cryptographic proof
- Third-party auditor access portal

### 3. Advanced Verification
- Multi-party signature verification
- Merkle tree for batch verification
- Hardware Security Module (HSM) integration

### 4. Analytics
- Trust domain usage statistics
- Signature verification performance metrics
- Weak link trends over time
- Agent reliability scores

---

## Summary

The Crypto Manifest system provides:

✅ **Complete Traceability** - Every workflow stage tracked through PKI mesh
✅ **Immutable Audit Trail** - Turing Tape as tamper-evident source of truth
✅ **Real-Time Verification** - Signature validation at any time
✅ **Compliance Ready** - SOC 2, GDPR, HIPAA, ISO 27001 evidence
✅ **Displayable/Loggable** - Text format for console and logs
✅ **Weak Link Detection** - Automated identification of integrity issues
✅ **Trust Domain Topology** - Visual PKI mesh relationships

**Replaces:** Static PKI diagrams with live, verifiable crypto journey tracking.

**Files:**
- ✅ `backend/app/services/crypto_manifest_service.py` - Core service
- ✅ `backend/app/api/crypto_chain.py` - API endpoints (enhanced)
- ✅ `swarms/team_agent/state/turing_tape.py` - Signing infrastructure (existing)
- ✅ `docs/CRYPTO_MANIFEST.md` - This documentation

For questions or issues, see GitHub issues or contact the Team Agent development team.
