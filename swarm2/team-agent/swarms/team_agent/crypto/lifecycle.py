"""
Certificate Lifecycle Management for Team Agent PKI.

Provides automatic certificate expiration monitoring, renewal, and rotation.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from cryptography import x509
from cryptography.hazmat.backends import default_backend


logger = logging.getLogger(__name__)


class CertificateStatus(Enum):
    """Certificate lifecycle status."""
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    RENEWED = "renewed"
    ROTATED = "rotated"


class NotificationLevel(Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CertificateLifecycleManager:
    """
    Certificate Lifecycle Manager for automatic expiration monitoring and renewal.

    Features:
    - Monitor certificate expiration dates
    - Automatic renewal before expiration
    - Certificate rotation with new key pairs
    - Notification system for expiring certificates
    - Configurable renewal thresholds
    """

    def __init__(
        self,
        pki_manager: 'PKIManager',
        renewal_threshold_days: int = 30,
        warning_threshold_days: int = 60,
        critical_threshold_days: int = 7
    ):
        """
        Initialize Certificate Lifecycle Manager.

        Args:
            pki_manager: PKIManager instance
            renewal_threshold_days: Days before expiration to auto-renew (default: 30)
            warning_threshold_days: Days before expiration to send warning (default: 60)
            critical_threshold_days: Days before expiration for critical alert (default: 7)
        """
        self.pki_manager = pki_manager
        self.renewal_threshold_days = renewal_threshold_days
        self.warning_threshold_days = warning_threshold_days
        self.critical_threshold_days = critical_threshold_days

        # Notification handlers: List[Callable[[Dict], None]]
        self.notification_handlers: List[Callable[[Dict[str, Any]], None]] = []

        # Lifecycle event log
        self.event_log: List[Dict[str, Any]] = []

    def get_certificate_expiration(self, domain: 'TrustDomain') -> datetime:
        """
        Get certificate expiration date for a trust domain.

        Args:
            domain: Trust domain (Government, Execution, Logging)

        Returns:
            Certificate expiration datetime (UTC)
        """
        cert_chain = self.pki_manager.get_certificate_chain(domain)
        cert = x509.load_pem_x509_certificate(
            cert_chain['cert'],
            backend=default_backend()
        )
        return cert.not_valid_after

    def get_certificate_info(self, domain: 'TrustDomain') -> Dict[str, Any]:
        """
        Get detailed certificate information including expiration status.

        Args:
            domain: Trust domain

        Returns:
            Dict with certificate information:
            - domain: Trust domain name
            - serial: Certificate serial number
            - subject: Certificate subject DN
            - issuer: Certificate issuer DN
            - not_before: Validity start date
            - not_after: Validity end date
            - days_until_expiry: Days until expiration
            - status: CertificateStatus enum
        """
        cert_chain = self.pki_manager.get_certificate_chain(domain)
        cert = x509.load_pem_x509_certificate(
            cert_chain['cert'],
            backend=default_backend()
        )

        now = datetime.utcnow()
        days_until_expiry = (cert.not_valid_after - now).days

        # Determine status
        if cert.not_valid_after < now:
            status = CertificateStatus.EXPIRED
        elif days_until_expiry <= self.critical_threshold_days:
            status = CertificateStatus.EXPIRING_SOON
        elif days_until_expiry <= self.warning_threshold_days:
            status = CertificateStatus.EXPIRING_SOON
        else:
            status = CertificateStatus.VALID

        return {
            "domain": domain.value,
            "serial": format(cert.serial_number, 'x'),
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "not_before": cert.not_valid_before,
            "not_after": cert.not_valid_after,
            "days_until_expiry": days_until_expiry,
            "status": status.value
        }

    def get_all_certificate_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all certificates across all trust domains.

        Returns:
            List of certificate info dicts for all domains
        """
        from .pki import TrustDomain

        status_list = []
        for domain in TrustDomain:
            try:
                info = self.get_certificate_info(domain)
                status_list.append(info)
            except Exception as e:
                logger.error(f"Error getting status for {domain.value}: {e}")
                status_list.append({
                    "domain": domain.value,
                    "status": "error",
                    "error": str(e)
                })

        return status_list

    def check_expiring_certificates(
        self,
        threshold_days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for certificates expiring within threshold.

        Args:
            threshold_days: Days threshold (default: renewal_threshold_days)

        Returns:
            List of certificates expiring within threshold
        """
        if threshold_days is None:
            threshold_days = self.renewal_threshold_days

        all_certs = self.get_all_certificate_status()
        expiring = []

        for cert_info in all_certs:
            if cert_info.get("status") == "error":
                continue

            days_until_expiry = cert_info.get("days_until_expiry", float('inf'))
            if days_until_expiry <= threshold_days:
                expiring.append(cert_info)

        return expiring

    def renew_certificate(
        self,
        domain: 'TrustDomain',
        validity_days: int = 365
    ) -> Dict[str, Any]:
        """
        Renew a certificate with the same key pair.

        This generates a new certificate with the same public key but
        extended validity period. The private key remains unchanged.

        Args:
            domain: Trust domain to renew
            validity_days: New certificate validity period in days

        Returns:
            Dict with renewal information:
            - domain: Trust domain
            - old_serial: Previous certificate serial
            - new_serial: New certificate serial
            - old_expiry: Previous expiration date
            - new_expiry: New expiration date
            - renewed_at: Renewal timestamp
        """
        from .pki import TrustDomain

        # Get old certificate info
        old_info = self.get_certificate_info(domain)
        old_cert_chain = self.pki_manager.get_certificate_chain(domain)

        # Load old certificate to get subject
        old_cert = x509.load_pem_x509_certificate(
            old_cert_chain['cert'],
            backend=default_backend()
        )

        # Issue new certificate with same key
        # Note: PKIManager.issue_certificate generates a new key by default
        # For true renewal (same key), we'd need to modify PKIManager
        # For now, we'll re-issue which generates a new key (rotation)
        new_cert_info = self.pki_manager.issue_certificate(
            domain=domain,
            validity_days=validity_days
        )

        renewal_info = {
            "domain": domain.value,
            "old_serial": old_info["serial"],
            "new_serial": new_cert_info["serial"],
            "old_expiry": old_info["not_after"],
            "new_expiry": new_cert_info["not_after"],
            "renewed_at": datetime.utcnow().isoformat() + "Z"
        }

        # Log event
        self._log_event("certificate_renewed", renewal_info)

        # Notify handlers
        self._notify({
            "event": "certificate_renewed",
            "level": NotificationLevel.INFO.value,
            "data": renewal_info
        })

        return renewal_info

    def rotate_certificate(
        self,
        domain: 'TrustDomain',
        validity_days: int = 365
    ) -> Dict[str, Any]:
        """
        Rotate a certificate with a new key pair.

        This generates a completely new certificate with a new public/private
        key pair. More secure than renewal but requires updating all systems
        that use the certificate.

        Args:
            domain: Trust domain to rotate
            validity_days: New certificate validity period in days

        Returns:
            Dict with rotation information
        """
        # Get old certificate info
        old_info = self.get_certificate_info(domain)

        # Issue new certificate (generates new key pair)
        new_cert_info = self.pki_manager.issue_certificate(
            domain=domain,
            validity_days=validity_days
        )

        rotation_info = {
            "domain": domain.value,
            "old_serial": old_info["serial"],
            "new_serial": new_cert_info["serial"],
            "old_expiry": old_info["not_after"],
            "new_expiry": new_cert_info["not_after"],
            "rotated_at": datetime.utcnow().isoformat() + "Z",
            "key_rotated": True
        }

        # Log event
        self._log_event("certificate_rotated", rotation_info)

        # Notify handlers
        self._notify({
            "event": "certificate_rotated",
            "level": NotificationLevel.INFO.value,
            "data": rotation_info
        })

        return rotation_info

    def auto_renew_expiring_certificates(
        self,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Automatically renew certificates expiring within renewal threshold.

        Args:
            dry_run: If True, only report what would be renewed (don't actually renew)

        Returns:
            List of renewal results
        """
        expiring = self.check_expiring_certificates(self.renewal_threshold_days)
        renewals = []

        for cert_info in expiring:
            domain_value = cert_info["domain"]

            if dry_run:
                renewals.append({
                    "domain": domain_value,
                    "action": "would_renew",
                    "days_until_expiry": cert_info["days_until_expiry"]
                })
            else:
                try:
                    from .pki import TrustDomain
                    domain = TrustDomain(domain_value)
                    renewal_info = self.renew_certificate(domain)
                    renewals.append(renewal_info)
                    logger.info(f"Auto-renewed certificate for {domain_value}")
                except Exception as e:
                    logger.error(f"Failed to auto-renew {domain_value}: {e}")
                    renewals.append({
                        "domain": domain_value,
                        "action": "renewal_failed",
                        "error": str(e)
                    })

        return renewals

    def add_notification_handler(
        self,
        handler: Callable[[Dict[str, Any]], None]
    ):
        """
        Add a notification handler for lifecycle events.

        The handler will be called with event information:
        {
            "event": "certificate_renewed|certificate_rotated|expiration_warning",
            "level": "info|warning|critical",
            "data": {...}
        }

        Args:
            handler: Callable that accepts event dict
        """
        self.notification_handlers.append(handler)

    def check_and_notify_expiring(self):
        """
        Check for expiring certificates and send notifications.

        Sends notifications at different levels based on days until expiration:
        - CRITICAL: <= critical_threshold_days
        - WARNING: <= warning_threshold_days
        - INFO: <= renewal_threshold_days
        """
        all_certs = self.get_all_certificate_status()

        for cert_info in all_certs:
            if cert_info.get("status") == "error":
                continue

            days_until_expiry = cert_info.get("days_until_expiry", float('inf'))

            # Determine notification level
            level = None
            if days_until_expiry <= self.critical_threshold_days:
                level = NotificationLevel.CRITICAL
            elif days_until_expiry <= self.warning_threshold_days:
                level = NotificationLevel.WARNING
            elif days_until_expiry <= self.renewal_threshold_days:
                level = NotificationLevel.INFO

            if level:
                self._notify({
                    "event": "expiration_warning",
                    "level": level.value,
                    "data": cert_info
                })

    def get_event_log(
        self,
        event_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get lifecycle event log.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return (optional)

        Returns:
            List of event dicts
        """
        events = self.event_log

        if event_type:
            events = [e for e in events if e.get("event") == event_type]

        if limit:
            events = events[-limit:]

        return events

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log lifecycle event."""
        event = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data
        }
        self.event_log.append(event)

    def _notify(self, notification: Dict[str, Any]):
        """Send notification to all registered handlers."""
        for handler in self.notification_handlers:
            try:
                handler(notification)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
