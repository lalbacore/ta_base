"""
Certificate Lifecycle Manager - Automated expiration monitoring and renewal.

Monitors certificate expiration across all trust domains and provides
automated renewal capabilities with configurable thresholds.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .pki_service import pki_service


class CertificateLifecycleService:
    """
    Manages certificate lifecycle including expiration monitoring,
    automated renewals, and alerting.

    Features:
    - Expiration monitoring with 4-tier alert system
    - Automated renewal workflows
    - Configurable thresholds
    - Alert generation
    """

    def __init__(
        self,
        renewal_threshold_days: int = 30,
        warning_threshold_days: int = 90,
        critical_threshold_days: int = 7
    ):
        """
        Initialize lifecycle service.

        Args:
            renewal_threshold_days: Auto-renew when < N days left (default: 30)
            warning_threshold_days: Warning alert when < N days left (default: 90)
            critical_threshold_days: Critical alert when < N days left (default: 7)
        """
        self.renewal_threshold = renewal_threshold_days
        self.warning_threshold = warning_threshold_days
        self.critical_threshold = critical_threshold_days

    def check_expirations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check all certificates for expiration.

        Returns:
            Dict categorizing certificates by status:
            - expired: Already expired certificates
            - critical: < 7 days remaining
            - expiring_soon: < 30 days remaining
            - warning: < 90 days remaining
            - valid: > 90 days remaining
        """
        results = {
            'expired': [],
            'critical': [],
            'expiring_soon': [],
            'warning': [],
            'valid': []
        }

        # Get all certificates from PKI service
        certificates = pki_service.get_all_certificates()

        for cert in certificates:
            days_left = cert.get('days_until_expiry', 0)
            status = cert.get('status', 'unknown')

            cert_summary = {
                'domain': cert.get('domain'),
                'serial': cert.get('serial'),
                'subject': cert.get('subject'),
                'not_after': cert.get('not_after'),
                'days_until_expiry': days_left,
                'provider': cert.get('provider'),
                'provider_type': cert.get('provider_type')
            }

            # Categorize by calculated status
            if status == 'expired':
                results['expired'].append(cert_summary)
            elif status == 'critical':
                results['critical'].append(cert_summary)
            elif status == 'expiring_soon':
                results['expiring_soon'].append(cert_summary)
            elif days_left < self.warning_threshold:
                results['warning'].append(cert_summary)
            else:
                results['valid'].append(cert_summary)

        return results

    def auto_renew_expiring(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """
        Automatically renew certificates within renewal threshold.

        Args:
            dry_run: If True, only simulate renewal without actual changes

        Returns:
            List of renewal results with status and details
        """
        expiration_status = self.check_expirations()
        renewal_results = []

        # Renew critical and expiring_soon certificates
        for cert_list_name in ['critical', 'expiring_soon']:
            for cert in expiration_status[cert_list_name]:
                domain = cert['domain']

                if dry_run:
                    renewal_results.append({
                        'domain': domain,
                        'old_serial': cert['serial'],
                        'status': 'dry_run',
                        'would_renew': True,
                        'reason': f"{cert['days_until_expiry']} days until expiry"
                    })
                    continue

                try:
                    # Rotate certificate (new key pair)
                    result = pki_service.rotate_certificate(domain)

                    renewal_results.append({
                        'domain': domain,
                        'old_serial': cert['serial'],
                        'new_serial': result.get('new_serial'),
                        'renewed_at': result.get('rotated_at'),
                        'status': 'success',
                        'reason': f"Auto-renewed ({cert['days_until_expiry']} days left)"
                    })

                except Exception as e:
                    renewal_results.append({
                        'domain': domain,
                        'old_serial': cert['serial'],
                        'status': 'failed',
                        'error': str(e),
                        'reason': f"Renewal failed ({cert['days_until_expiry']} days left)"
                    })

        return renewal_results

    def get_expiration_alerts(self) -> List[Dict[str, Any]]:
        """
        Get list of certificates requiring attention.

        Returns:
            List of alerts sorted by severity (critical first)
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
                'action_required': 'immediate_renewal',
                'days_left': cert['days_until_expiry']
            })

        # Critical - High severity
        for cert in expiration_status['critical']:
            alerts.append({
                'severity': 'high',
                'domain': cert['domain'],
                'message': f"Certificate expires in {cert['days_until_expiry']} days",
                'serial': cert['serial'],
                'action_required': 'renew_now',
                'days_left': cert['days_until_expiry']
            })

        # Expiring soon - Medium severity
        for cert in expiration_status['expiring_soon']:
            alerts.append({
                'severity': 'medium',
                'domain': cert['domain'],
                'message': f"Certificate expires in {cert['days_until_expiry']} days",
                'serial': cert['serial'],
                'action_required': 'schedule_renewal',
                'days_left': cert['days_until_expiry']
            })

        # Warning - Low severity
        for cert in expiration_status['warning']:
            alerts.append({
                'severity': 'low',
                'domain': cert['domain'],
                'message': f"Certificate expires in {cert['days_until_expiry']} days",
                'serial': cert['serial'],
                'action_required': 'monitor',
                'days_left': cert['days_until_expiry']
            })

        return alerts

    def get_lifecycle_summary(self) -> Dict[str, Any]:
        """
        Get summary of certificate lifecycle status.

        Returns:
            Dict with counts and alerts
        """
        expiration_status = self.check_expirations()
        alerts = self.get_expiration_alerts()

        return {
            'summary': {
                'expired': len(expiration_status['expired']),
                'critical': len(expiration_status['critical']),
                'expiring_soon': len(expiration_status['expiring_soon']),
                'warning': len(expiration_status['warning']),
                'valid': len(expiration_status['valid'])
            },
            'alerts': alerts,
            'certificates_by_status': expiration_status,
            'total_certificates': sum(len(v) for v in expiration_status.values()),
            'requires_action': len(expiration_status['expired']) +
                             len(expiration_status['critical']) +
                             len(expiration_status['expiring_soon'])
        }

    def simulate_renewal(self) -> Dict[str, Any]:
        """
        Simulate auto-renewal without making changes.

        Returns:
            Dict with simulation results
        """
        results = self.auto_renew_expiring(dry_run=True)

        would_renew = [r for r in results if r.get('would_renew', False)]

        return {
            'dry_run': True,
            'would_renew_count': len(would_renew),
            'certificates': would_renew,
            'message': f"Would automatically renew {len(would_renew)} certificate(s)"
        }


# Singleton instance with default thresholds
cert_lifecycle_service = CertificateLifecycleService(
    renewal_threshold_days=30,
    warning_threshold_days=90,
    critical_threshold_days=7
)
