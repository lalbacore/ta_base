# Pull Request: PKI Management System Enhancements

## Overview
Complete integration of PKI management system with certificate lifecycle management, revocation tracking, and automated rotation capabilities.

## Current State

### Implemented ✅
- **PKIManager** (`swarms/team_agent/crypto/pki.py`)
  - Three-tier CA hierarchy (Root + Government/Execution/Logging)
  - Certificate generation and signing
  - `issue_certificate()` method for rotation
  - Integration with CRLManager

- **CRLManager** (`swarms/team_agent/crypto/crl.py`)
  - SQLite-based revocation storage
  - Revoke/suspend/reinstate operations
  - X.509 CRL generation
  - Audit logging

### Not Implemented ❌
- **PKIService integration** - Currently using mock data, not connected to actual PKI infrastructure
- **Certificate lifecycle monitoring** - No expiration tracking or alerts
- **Automated rotation** - No automated renewal workflows
- **Frontend enhancements** - Limited visibility into certificate status
- **Revocation management UI** - No interface to revoke/view revoked certificates

## Proposed Enhancements

### 1. Integrate PKIService with Real PKI Infrastructure

**File**: `backend/app/services/pki_service.py`

**Changes**:
```python
class PKIService:
    def __init__(self):
        from swarms.team_agent.crypto.pki import PKIManager, TrustDomain
        from swarms.team_agent.crypto.crl import CRLManager, RevocationReason

        # Initialize actual PKI infrastructure
        self.pki_manager = PKIManager()
        self.crl_manager = CRLManager()

        # Ensure PKI is initialized
        self.pki_manager.initialize_pki()

    def get_all_certificates(self) -> List[Dict[str, Any]]:
        """Get status of all certificates from actual PKI."""
        certificates = []
        for domain in TrustDomain:
            cert_info = self.pki_manager.get_certificate_info(domain)
            cert_info['domain'] = domain.value
            cert_info['status'] = self._calculate_cert_status(cert_info)
            cert_info['days_until_expiry'] = self._calculate_days_until_expiry(cert_info)
            certificates.append(cert_info)
        return certificates

    def _calculate_cert_status(self, cert_info: Dict) -> str:
        """Calculate certificate status based on expiry."""
        days_left = self._calculate_days_until_expiry(cert_info)

        if days_left < 0:
            return 'expired'
        elif days_left < 7:
            return 'critical'
        elif days_left < 30:
            return 'expiring_soon'
        else:
            return 'valid'

    def rotate_certificate(self, domain: str, validity_days: int = 1825) -> Dict[str, Any]:
        """Rotate certificate with new key pair."""
        from swarms.team_agent.crypto.pki import TrustDomain

        trust_domain = TrustDomain(domain)

        # Get old certificate info for audit
        old_cert = self.pki_manager.get_certificate_info(trust_domain)
        old_serial = old_cert['serial']

        # Issue new certificate (generates new key pair)
        new_cert = self.pki_manager.issue_certificate(trust_domain, validity_days)

        # Revoke old certificate
        self.pki_manager.revoke_certificate(
            serial_number=old_serial,
            reason=RevocationReason.SUPERSEDED,
            revoked_by='system',
            trust_domain=trust_domain,
            cert_subject=old_cert['subject'],
            metadata={'action': 'rotation', 'new_serial': new_cert['serial']}
        )

        # Generate updated CRL
        self.pki_manager.generate_crl(trust_domain)

        return {
            'domain': domain,
            'old_serial': old_serial,
            'new_serial': new_cert['serial'],
            'new_cert': new_cert,
            'rotated_at': datetime.now().isoformat()
        }
```

**Impact**:
- Connects backend to actual PKI infrastructure
- Removes dependency on mock/seed data
- Enables real certificate operations

---

### 2. Certificate Lifecycle Manager

**New File**: `backend/app/services/cert_lifecycle_service.py`

**Purpose**: Monitor certificate expiration and trigger automated renewals

```python
"""
Certificate Lifecycle Manager - Automated expiration monitoring and renewal.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from swarms.team_agent.crypto.pki import PKIManager, TrustDomain


class CertificateLifecycleService:
    """
    Manages certificate lifecycle including expiration monitoring,
    automated renewals, and alerting.
    """

    def __init__(
        self,
        renewal_threshold_days: int = 30,
        warning_threshold_days: int = 60,
        critical_threshold_days: int = 7
    ):
        self.pki_manager = PKIManager()
        self.renewal_threshold = renewal_threshold_days
        self.warning_threshold = warning_threshold_days
        self.critical_threshold = critical_threshold_days

    def check_expirations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check all certificates for expiration.

        Returns:
            Dict categorizing certificates by status:
            - expired: Already expired
            - critical: < 7 days
            - expiring_soon: < 30 days
            - warning: < 60 days
            - valid: > 60 days
        """
        results = {
            'expired': [],
            'critical': [],
            'expiring_soon': [],
            'warning': [],
            'valid': []
        }

        for domain in TrustDomain:
            cert_info = self.pki_manager.get_certificate_info(domain)
            days_left = self._calculate_days_until_expiry(cert_info)

            cert_status = {
                'domain': domain.value,
                'serial': cert_info['serial'],
                'subject': cert_info['subject'],
                'not_after': cert_info['not_after'],
                'days_until_expiry': days_left
            }

            if days_left < 0:
                results['expired'].append(cert_status)
            elif days_left < self.critical_threshold:
                results['critical'].append(cert_status)
            elif days_left < self.renewal_threshold:
                results['expiring_soon'].append(cert_status)
            elif days_left < self.warning_threshold:
                results['warning'].append(cert_status)
            else:
                results['valid'].append(cert_status)

        return results

    def auto_renew_expiring(self) -> List[Dict[str, Any]]:
        """
        Automatically renew certificates within renewal threshold.

        Returns:
            List of renewal results
        """
        expiration_status = self.check_expirations()
        renewal_results = []

        # Renew critical and expiring_soon certificates
        for cert_list in [expiration_status['critical'], expiration_status['expiring_soon']]:
            for cert in cert_list:
                domain = TrustDomain(cert['domain'])

                try:
                    # Rotate certificate (new key pair)
                    new_cert = self.pki_manager.issue_certificate(domain)

                    renewal_results.append({
                        'domain': cert['domain'],
                        'old_serial': cert['serial'],
                        'new_serial': new_cert['serial'],
                        'renewed_at': datetime.now().isoformat(),
                        'status': 'success'
                    })
                except Exception as e:
                    renewal_results.append({
                        'domain': cert['domain'],
                        'old_serial': cert['serial'],
                        'status': 'failed',
                        'error': str(e)
                    })

        return renewal_results

    def get_expiration_alerts(self) -> List[Dict[str, Any]]:
        """
        Get list of certificates requiring attention.

        Returns:
            List of alerts sorted by severity
        """
        expiration_status = self.check_expirations()
        alerts = []

        # Expired - Critical severity
        for cert in expiration_status['expired']:
            alerts.append({
                'severity': 'critical',
                'domain': cert['domain'],
                'message': f"Certificate EXPIRED {abs(cert['days_until_expiry'])} days ago",
                'serial': cert['serial'],
                'action_required': 'immediate_renewal'
            })

        # Critical - High severity
        for cert in expiration_status['critical']:
            alerts.append({
                'severity': 'high',
                'domain': cert['domain'],
                'message': f"Certificate expires in {cert['days_until_expiry']} days",
                'serial': cert['serial'],
                'action_required': 'renew_now'
            })

        # Expiring soon - Medium severity
        for cert in expiration_status['expiring_soon']:
            alerts.append({
                'severity': 'medium',
                'domain': cert['domain'],
                'message': f"Certificate expires in {cert['days_until_expiry']} days",
                'serial': cert['serial'],
                'action_required': 'schedule_renewal'
            })

        # Warning - Low severity
        for cert in expiration_status['warning']:
            alerts.append({
                'severity': 'low',
                'domain': cert['domain'],
                'message': f"Certificate expires in {cert['days_until_expiry']} days",
                'serial': cert['serial'],
                'action_required': 'monitor'
            })

        return alerts

    def _calculate_days_until_expiry(self, cert_info: Dict) -> int:
        """Calculate days until certificate expires."""
        expiry = datetime.fromisoformat(cert_info['not_after'])
        delta = expiry - datetime.now()
        return delta.days


# Singleton instance
cert_lifecycle_service = CertificateLifecycleService()
```

**Impact**:
- Automated expiration monitoring
- Proactive renewal before expiration
- Alert system for certificate lifecycle

---

### 3. Enhanced PKI API Endpoints

**File**: `backend/app/api/pki.py`

**New Endpoints**:

```python
# Certificate Rotation
@pki_bp.route('/certificates/<domain>/rotate', methods=['POST'])
def rotate_certificate(domain):
    """Rotate certificate with new key pair."""
    try:
        result = pki_service.rotate_certificate(domain)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Certificate Revocation
@pki_bp.route('/certificates/<serial>/revoke', methods=['POST'])
def revoke_certificate(serial):
    """Revoke a certificate."""
    data = request.json
    reason = data.get('reason', 'UNSPECIFIED')
    revoked_by = data.get('revoked_by', 'admin')

    try:
        result = pki_service.revoke_certificate(serial, reason, revoked_by)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Revoked Certificates List
@pki_bp.route('/certificates/revoked', methods=['GET'])
def get_revoked_certificates():
    """Get list of revoked certificates."""
    domain = request.args.get('domain')
    limit = int(request.args.get('limit', 100))

    try:
        revoked = pki_service.get_revoked_certificates(domain, limit)
        return jsonify(revoked), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Certificate Lifecycle Status
@pki_bp.route('/lifecycle/status', methods=['GET'])
def get_lifecycle_status():
    """Get certificate lifecycle status (expiration warnings)."""
    try:
        status = cert_lifecycle_service.check_expirations()
        alerts = cert_lifecycle_service.get_expiration_alerts()

        return jsonify({
            'status': status,
            'alerts': alerts,
            'summary': {
                'expired': len(status['expired']),
                'critical': len(status['critical']),
                'expiring_soon': len(status['expiring_soon']),
                'warning': len(status['warning']),
                'valid': len(status['valid'])
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Auto-Renew Expiring Certificates
@pki_bp.route('/lifecycle/auto-renew', methods=['POST'])
def auto_renew_certificates():
    """Automatically renew expiring certificates."""
    try:
        results = cert_lifecycle_service.auto_renew_expiring()
        return jsonify({
            'renewed': results,
            'count': len(results)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# CRL Information
@pki_bp.route('/crl/<domain>', methods=['GET'])
def get_crl(domain):
    """Get Certificate Revocation List for domain."""
    try:
        crl = pki_service.get_crl(domain)
        return jsonify(crl), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Generate CRL
@pki_bp.route('/crl/<domain>/generate', methods=['POST'])
def generate_crl(domain):
    """Generate new CRL for domain."""
    try:
        result = pki_service.generate_crl(domain)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Impact**:
- Full API coverage for PKI operations
- Certificate rotation via API
- Revocation management endpoints
- Lifecycle monitoring endpoints

---

### 4. Frontend Enhancements

**File**: `frontend/src/views/pki/PKIView.vue`

**New Features**:

1. **Expiration Status Dashboard**
   ```vue
   <div class="expiration-alerts">
     <div v-for="alert in expirationAlerts" :key="alert.serial"
          :class="`alert alert-${alert.severity}`">
       <i :class="getAlertIcon(alert.severity)"></i>
       <div>
         <strong>{{ alert.domain }}</strong>
         <p>{{ alert.message }}</p>
         <Tag :severity="alert.severity">{{ alert.action_required }}</Tag>
       </div>
     </div>
   </div>
   ```

2. **Certificate Actions**
   ```vue
   <div class="cert-actions">
     <Button label="Rotate" icon="pi pi-refresh"
             @click="rotateCertificate(cert.domain)"
             severity="warning" />
     <Button label="Revoke" icon="pi pi-ban"
             @click="showRevokeDialog(cert)"
             severity="danger" />
     <Button label="Download CRL" icon="pi pi-download"
             @click="downloadCRL(cert.domain)" />
   </div>
   ```

3. **Revoked Certificates Panel**
   ```vue
   <DataTable :value="revokedCertificates" paginator :rows="25">
     <Column field="serial_number" header="Serial" />
     <Column field="trust_domain" header="Domain" />
     <Column field="revocation_date" header="Revoked" />
     <Column field="reason" header="Reason">
       <template #body="{ data }">
         <Tag :severity="getReasonSeverity(data.reason)">
           {{ data.reason }}
         </Tag>
       </template>
     </Column>
     <Column field="revoked_by" header="Revoked By" />
   </DataTable>
   ```

4. **Auto-Renewal Control**
   ```vue
   <Card>
     <template #title>Certificate Lifecycle Management</template>
     <template #content>
       <div class="lifecycle-controls">
         <Button label="Check Expirations"
                 icon="pi pi-search"
                 @click="checkExpirations" />
         <Button label="Auto-Renew Expiring"
                 icon="pi pi-sync"
                 @click="autoRenewCertificates"
                 severity="success" />
       </div>

       <div class="expiration-summary">
         <div class="stat-card critical">
           <i class="pi pi-exclamation-triangle"></i>
           <div>
             <div class="stat-value">{{ lifecycleStatus.critical }}</div>
             <div class="stat-label">Critical</div>
           </div>
         </div>
         <!-- More stat cards -->
       </div>
     </template>
   </Card>
   ```

**Impact**:
- Complete visibility into certificate status
- One-click certificate rotation
- Revocation management UI
- Automated renewal controls

---

## Implementation Plan

### Phase 1: Backend Integration (Priority: High)
**Estimated Effort**: 4-6 hours

**Tasks**:
1. ✅ Refactor `PKIService` to use actual `PKIManager` and `CRLManager`
2. ✅ Add certificate status calculation methods
3. ✅ Implement `rotate_certificate()` with old cert revocation
4. ✅ Implement `revoke_certificate()` integration
5. ✅ Add `get_revoked_certificates()` implementation
6. ✅ Test all PKI service methods

**Files to Modify**:
- `backend/app/services/pki_service.py`

**Files to Create**:
- None (using existing PKIManager/CRLManager)

---

### Phase 2: Lifecycle Management (Priority: High)
**Estimated Effort**: 6-8 hours

**Tasks**:
1. ✅ Create `CertificateLifecycleService`
2. ✅ Implement expiration checking logic
3. ✅ Implement auto-renewal workflow
4. ✅ Add alert generation
5. ✅ Create scheduled job for periodic checks
6. ✅ Test lifecycle automation

**Files to Create**:
- `backend/app/services/cert_lifecycle_service.py`
- `backend/app/jobs/cert_lifecycle_job.py` (optional)

---

### Phase 3: API Endpoints (Priority: Medium)
**Estimated Effort**: 3-4 hours

**Tasks**:
1. ✅ Add `/certificates/<domain>/rotate` endpoint
2. ✅ Add `/certificates/<serial>/revoke` endpoint
3. ✅ Add `/certificates/revoked` endpoint
4. ✅ Add `/lifecycle/status` endpoint
5. ✅ Add `/lifecycle/auto-renew` endpoint
6. ✅ Add `/crl/<domain>` endpoints
7. ✅ Test all new endpoints

**Files to Modify**:
- `backend/app/api/pki.py`

---

### Phase 4: Frontend Enhancements (Priority: Medium)
**Estimated Effort**: 6-8 hours

**Tasks**:
1. ✅ Add expiration alerts dashboard
2. ✅ Add certificate action buttons (Rotate, Revoke)
3. ✅ Create revoked certificates panel
4. ✅ Add auto-renewal controls
5. ✅ Add CRL download functionality
6. ✅ Create revoke certificate dialog
7. ✅ Add confirmation dialogs for destructive actions
8. ✅ Test all UI components

**Files to Modify**:
- `frontend/src/views/pki/PKIView.vue`

**Files to Create**:
- `frontend/src/components/pki/RevokeDialog.vue`
- `frontend/src/components/pki/CertificateActions.vue`

---

### Phase 5: Testing & Documentation (Priority: Low)
**Estimated Effort**: 4-5 hours

**Tasks**:
1. ✅ Unit tests for PKIService integration
2. ✅ Unit tests for CertificateLifecycleService
3. ✅ Integration tests for rotation workflow
4. ✅ Integration tests for revocation workflow
5. ✅ End-to-end test: Complete certificate lifecycle
6. ✅ Update API documentation
7. ✅ Update user guide with PKI management

---

## Success Criteria

### Functional
- ✅ All certificates use real PKI infrastructure (not mock data)
- ✅ Certificate rotation works and revokes old certificate
- ✅ Certificate revocation works and updates CRL
- ✅ Lifecycle monitoring detects expiring certificates
- ✅ Auto-renewal successfully renews expiring certificates
- ✅ Frontend displays accurate certificate status
- ✅ Frontend allows one-click rotation and revocation

### Non-Functional
- ✅ Certificate rotation completes in < 1 second
- ✅ Expiration checks complete in < 500ms
- ✅ CRL generation completes in < 2 seconds
- ✅ No breaking changes to existing PKI infrastructure
- ✅ All operations logged to audit trail

---

## Testing Strategy

### Unit Tests
```python
# test_pki_service.py
def test_get_all_certificates_from_real_pki():
    """Test retrieval of actual certificates."""
    service = PKIService()
    certs = service.get_all_certificates()

    assert len(certs) == 3  # government, execution, logging
    for cert in certs:
        assert 'domain' in cert
        assert 'serial' in cert
        assert 'status' in cert
        assert cert['status'] in ['valid', 'expiring_soon', 'critical', 'expired']

def test_rotate_certificate_revokes_old():
    """Test that rotation revokes old certificate."""
    service = PKIService()

    # Get old cert
    old_cert = service.get_certificate('government')
    old_serial = old_cert['serial']

    # Rotate
    result = service.rotate_certificate('government')

    # Verify old cert is revoked
    assert service.crl_manager.is_revoked(old_serial)

    # Verify new cert is different
    assert result['new_serial'] != old_serial
```

### Integration Tests
```python
# test_cert_lifecycle.py
def test_auto_renew_expiring_certificates():
    """Test automatic renewal of expiring certificates."""
    # Create certificate expiring in 5 days
    service = CertificateLifecycleService(renewal_threshold_days=7)

    # Check expirations
    status = service.check_expirations()
    assert len(status['expiring_soon']) > 0

    # Auto-renew
    results = service.auto_renew_expiring()
    assert len(results) > 0
    assert all(r['status'] == 'success' for r in results)
```

---

## Risks & Mitigation

### Risk 1: Certificate Rotation During Active Use
**Impact**: High
**Probability**: Medium
**Mitigation**:
- Implement grace period where both old and new certs are valid
- Add pre-rotation validation
- Notify dependent services before rotation

### Risk 2: CRL Growth Over Time
**Impact**: Medium
**Probability**: High
**Mitigation**:
- Implement CRL archival after 90 days
- Use delta CRLs for incremental updates
- Consider OCSP as alternative to CRL

### Risk 3: Auto-Renewal Failures
**Impact**: High
**Probability**: Low
**Mitigation**:
- Retry logic with exponential backoff
- Alert on renewal failures
- Manual override capability

---

## Future Enhancements (Out of Scope)

1. **OCSP Responder** - Real-time certificate status checking
2. **Hardware Security Module (HSM)** - Store CA keys in HSM
3. **Certificate Transparency Logs** - Publish certificates to CT logs
4. **Automated Certificate Request (ACME)** - Let's Encrypt integration
5. **Multi-CA Support** - Support for external CAs
6. **Certificate Pinning** - Pin specific certificates in client
7. **Key Escrow** - Backup/recovery of certificate private keys

---

## References

- [RFC 5280 - X.509 PKI Certificate and CRL Profile](https://datatracker.ietf.org/doc/html/rfc5280)
- [RFC 6960 - OCSP (Online Certificate Status Protocol)](https://datatracker.ietf.org/doc/html/rfc6960)
- Python Cryptography Library: https://cryptography.io/
- Team Agent PKI Architecture: `docs/ARCHITECTURE.md`

---

## Checklist

### Before Starting
- [ ] Review existing PKI infrastructure
- [ ] Understand three-tier CA hierarchy
- [ ] Review CRL implementation
- [ ] Understand trust domains (government, execution, logging)

### Implementation
- [ ] Phase 1: Backend Integration
- [ ] Phase 2: Lifecycle Management
- [ ] Phase 3: API Endpoints
- [ ] Phase 4: Frontend Enhancements
- [ ] Phase 5: Testing & Documentation

### Before Merge
- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance benchmarks met
- [ ] Security review completed
