"""
Tests for Certificate Lifecycle Management system.

Tests lifecycle manager, expiration monitoring, auto-renewal, rotation,
and notification system.
"""

import os
import sys
import unittest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from swarms.team_agent.crypto import (
    PKIManager,
    TrustDomain,
    CertificateLifecycleManager,
    CertificateStatus,
    NotificationLevel
)


class TestCertificateLifecycleManager(unittest.TestCase):
    """Test Certificate Lifecycle Manager core functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

        # Create lifecycle manager
        self.lifecycle = self.pki.create_lifecycle_manager(
            renewal_threshold_days=30,
            warning_threshold_days=60,
            critical_threshold_days=7
        )

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_lifecycle_manager(self):
        """Test creating lifecycle manager."""
        self.assertIsNotNone(self.lifecycle)
        self.assertEqual(self.lifecycle.renewal_threshold_days, 30)
        self.assertEqual(self.lifecycle.warning_threshold_days, 60)
        self.assertEqual(self.lifecycle.critical_threshold_days, 7)

    def test_get_certificate_expiration(self):
        """Test getting certificate expiration date."""
        expiry = self.lifecycle.get_certificate_expiration(TrustDomain.EXECUTION)

        self.assertIsInstance(expiry, datetime)
        # Default certificate is 1825 days (5 years), should expire in ~1825 days
        now = datetime.utcnow()
        days_until_expiry = (expiry - now).days
        self.assertGreater(days_until_expiry, 1800)
        self.assertLess(days_until_expiry, 1830)

    def test_get_certificate_info(self):
        """Test getting detailed certificate information."""
        info = self.lifecycle.get_certificate_info(TrustDomain.EXECUTION)

        self.assertEqual(info["domain"], "execution")
        self.assertIn("serial", info)
        self.assertIn("subject", info)
        self.assertIn("issuer", info)
        self.assertIn("not_before", info)
        self.assertIn("not_after", info)
        self.assertIn("days_until_expiry", info)
        self.assertIn("status", info)

        # Fresh certificate should be VALID (5-year default validity)
        self.assertEqual(info["status"], CertificateStatus.VALID.value)
        self.assertGreater(info["days_until_expiry"], 1800)

    def test_get_all_certificate_status(self):
        """Test getting status of all certificates."""
        all_status = self.lifecycle.get_all_certificate_status()

        # Should have status for all 3 trust domains
        self.assertEqual(len(all_status), 3)

        domains = [s["domain"] for s in all_status]
        self.assertIn("government", domains)
        self.assertIn("execution", domains)
        self.assertIn("logging", domains)

        # All should be VALID (freshly created)
        for status in all_status:
            self.assertEqual(status["status"], CertificateStatus.VALID.value)

    def test_check_expiring_certificates(self):
        """Test checking for expiring certificates."""
        # With fresh certificates (5-year validity), none should be expiring with 30-day threshold
        expiring = self.lifecycle.check_expiring_certificates(threshold_days=30)
        self.assertEqual(len(expiring), 0)

        # With very high threshold (2000 days > 5 years), all should be expiring
        expiring = self.lifecycle.check_expiring_certificates(threshold_days=2000)
        self.assertEqual(len(expiring), 3)

    def test_check_expiring_certificates_with_custom_threshold(self):
        """Test expiring check with different thresholds."""
        # 2000 days threshold - all certs should be expiring (>5 year validity)
        expiring_2000 = self.lifecycle.check_expiring_certificates(2000)
        self.assertEqual(len(expiring_2000), 3)

        # 1 day threshold - no certs should be expiring
        expiring_1 = self.lifecycle.check_expiring_certificates(1)
        self.assertEqual(len(expiring_1), 0)

    def test_renew_certificate(self):
        """Test certificate renewal."""
        # Get old certificate info
        old_info = self.lifecycle.get_certificate_info(TrustDomain.EXECUTION)
        old_serial = old_info["serial"]
        old_expiry = old_info["not_after"]

        # Renew certificate
        renewal_info = self.lifecycle.renew_certificate(
            TrustDomain.EXECUTION,
            validity_days=365
        )

        self.assertEqual(renewal_info["domain"], "execution")
        self.assertEqual(renewal_info["old_serial"], old_serial)
        self.assertNotEqual(renewal_info["new_serial"], old_serial)
        self.assertIn("renewed_at", renewal_info)

        # New certificate should have later expiry
        new_info = self.lifecycle.get_certificate_info(TrustDomain.EXECUTION)
        self.assertNotEqual(new_info["serial"], old_serial)

    def test_renew_certificate_with_custom_validity(self):
        """Test renewal with custom validity period."""
        renewal_info = self.lifecycle.renew_certificate(
            TrustDomain.GOVERNMENT,
            validity_days=730  # 2 years
        )

        self.assertIn("new_expiry", renewal_info)

        # Check new certificate has ~730 days validity
        new_info = self.lifecycle.get_certificate_info(TrustDomain.GOVERNMENT)
        self.assertGreater(new_info["days_until_expiry"], 720)

    def test_rotate_certificate(self):
        """Test certificate rotation."""
        # Get old certificate info
        old_info = self.lifecycle.get_certificate_info(TrustDomain.LOGGING)
        old_serial = old_info["serial"]

        # Rotate certificate
        rotation_info = self.lifecycle.rotate_certificate(
            TrustDomain.LOGGING,
            validity_days=365
        )

        self.assertEqual(rotation_info["domain"], "logging")
        self.assertEqual(rotation_info["old_serial"], old_serial)
        self.assertNotEqual(rotation_info["new_serial"], old_serial)
        self.assertTrue(rotation_info["key_rotated"])
        self.assertIn("rotated_at", rotation_info)

        # New certificate should exist
        new_info = self.lifecycle.get_certificate_info(TrustDomain.LOGGING)
        self.assertNotEqual(new_info["serial"], old_serial)

    def test_auto_renew_dry_run(self):
        """Test auto-renewal in dry-run mode."""
        # No certs expiring soon with default threshold
        results = self.lifecycle.auto_renew_expiring_certificates(dry_run=True)
        self.assertEqual(len(results), 0)

        # Set very high threshold to simulate expiring certs (> 5 years)
        self.lifecycle.renewal_threshold_days = 2000
        results = self.lifecycle.auto_renew_expiring_certificates(dry_run=True)

        # All 3 certs should be flagged for renewal
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertEqual(result["action"], "would_renew")
            self.assertIn("days_until_expiry", result)

    def test_auto_renew_actual(self):
        """Test actual auto-renewal."""
        # Set very high threshold to simulate expiring certs (> 5 years)
        self.lifecycle.renewal_threshold_days = 2000

        # Get old serials
        old_serials = {}
        for domain in TrustDomain:
            info = self.lifecycle.get_certificate_info(domain)
            old_serials[domain.value] = info["serial"]

        # Auto-renew
        results = self.lifecycle.auto_renew_expiring_certificates(dry_run=False)

        # All 3 certs should be renewed
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn("domain", result)
            domain_value = result["domain"]
            self.assertEqual(result["old_serial"], old_serials[domain_value])
            self.assertNotEqual(result["new_serial"], old_serials[domain_value])


class TestLifecycleNotifications(unittest.TestCase):
    """Test lifecycle notification system."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

        self.lifecycle = self.pki.create_lifecycle_manager(
            renewal_threshold_days=30,
            warning_threshold_days=60,
            critical_threshold_days=7
        )

        # Track notifications
        self.notifications = []

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def notification_handler(self, notification):
        """Test notification handler."""
        self.notifications.append(notification)

    def test_add_notification_handler(self):
        """Test adding notification handler."""
        self.lifecycle.add_notification_handler(self.notification_handler)
        self.assertEqual(len(self.lifecycle.notification_handlers), 1)

    def test_renewal_notification(self):
        """Test notification on certificate renewal."""
        self.lifecycle.add_notification_handler(self.notification_handler)

        # Renew certificate
        self.lifecycle.renew_certificate(TrustDomain.EXECUTION)

        # Should have received notification
        self.assertEqual(len(self.notifications), 1)
        notification = self.notifications[0]

        self.assertEqual(notification["event"], "certificate_renewed")
        self.assertEqual(notification["level"], NotificationLevel.INFO.value)
        self.assertIn("data", notification)

    def test_rotation_notification(self):
        """Test notification on certificate rotation."""
        self.lifecycle.add_notification_handler(self.notification_handler)

        # Rotate certificate
        self.lifecycle.rotate_certificate(TrustDomain.GOVERNMENT)

        # Should have received notification
        self.assertEqual(len(self.notifications), 1)
        notification = self.notifications[0]

        self.assertEqual(notification["event"], "certificate_rotated")
        self.assertEqual(notification["level"], NotificationLevel.INFO.value)
        self.assertTrue(notification["data"]["key_rotated"])

    def test_multiple_handlers(self):
        """Test multiple notification handlers."""
        notifications2 = []

        def handler2(notification):
            notifications2.append(notification)

        self.lifecycle.add_notification_handler(self.notification_handler)
        self.lifecycle.add_notification_handler(handler2)

        # Trigger event
        self.lifecycle.renew_certificate(TrustDomain.LOGGING)

        # Both handlers should receive notification
        self.assertEqual(len(self.notifications), 1)
        self.assertEqual(len(notifications2), 1)

    def test_expiration_warnings(self):
        """Test expiration warning notifications."""
        self.lifecycle.add_notification_handler(self.notification_handler)

        # Temporarily set thresholds very high to trigger warnings (> 5 years)
        self.lifecycle.warning_threshold_days = 2000
        self.lifecycle.critical_threshold_days = 1900

        # Check and notify
        self.lifecycle.check_and_notify_expiring()

        # Should have notifications for all 3 domains
        self.assertGreaterEqual(len(self.notifications), 3)

        # Check that warnings were sent
        events = [n["event"] for n in self.notifications]
        self.assertTrue(all(e == "expiration_warning" for e in events))


class TestLifecycleEventLog(unittest.TestCase):
    """Test lifecycle event logging."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

        self.lifecycle = self.pki.create_lifecycle_manager()

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_event_log_renewal(self):
        """Test event logging for renewal."""
        # Initially empty
        events = self.lifecycle.get_event_log()
        initial_count = len(events)

        # Renew certificate
        self.lifecycle.renew_certificate(TrustDomain.EXECUTION)

        # Should have logged event
        events = self.lifecycle.get_event_log()
        self.assertEqual(len(events), initial_count + 1)

        event = events[-1]
        self.assertEqual(event["event"], "certificate_renewed")
        self.assertIn("timestamp", event)
        self.assertIn("data", event)

    def test_event_log_rotation(self):
        """Test event logging for rotation."""
        # Rotate certificate
        self.lifecycle.rotate_certificate(TrustDomain.GOVERNMENT)

        # Should have logged event
        events = self.lifecycle.get_event_log(event_type="certificate_rotated")
        self.assertGreaterEqual(len(events), 1)

        event = events[-1]
        self.assertEqual(event["event"], "certificate_rotated")

    def test_event_log_filtering(self):
        """Test filtering event log."""
        # Generate different events
        self.lifecycle.renew_certificate(TrustDomain.EXECUTION)
        self.lifecycle.rotate_certificate(TrustDomain.GOVERNMENT)
        self.lifecycle.renew_certificate(TrustDomain.LOGGING)

        # Filter by type
        renewals = self.lifecycle.get_event_log(event_type="certificate_renewed")
        rotations = self.lifecycle.get_event_log(event_type="certificate_rotated")

        self.assertEqual(len(renewals), 2)
        self.assertEqual(len(rotations), 1)

    def test_event_log_limit(self):
        """Test limiting event log results."""
        # Generate multiple events
        for domain in TrustDomain:
            self.lifecycle.renew_certificate(domain)

        # Get limited results
        events = self.lifecycle.get_event_log(limit=2)
        self.assertEqual(len(events), 2)

        # Should be most recent events
        for event in events:
            self.assertEqual(event["event"], "certificate_renewed")


class TestLifecycleIntegration(unittest.TestCase):
    """Test lifecycle manager integration with PKI system."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pki = PKIManager(base_dir=self.temp_dir / "pki")
        self.pki.initialize_pki()

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_lifecycle_manager_creation_via_pki(self):
        """Test creating lifecycle manager through PKIManager."""
        manager = self.pki.create_lifecycle_manager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager, CertificateLifecycleManager)

    def test_lifecycle_manager_with_custom_thresholds(self):
        """Test creating manager with custom thresholds."""
        manager = self.pki.create_lifecycle_manager(
            renewal_threshold_days=14,
            warning_threshold_days=28,
            critical_threshold_days=3
        )

        self.assertEqual(manager.renewal_threshold_days, 14)
        self.assertEqual(manager.warning_threshold_days, 28)
        self.assertEqual(manager.critical_threshold_days, 3)

    def test_get_lifecycle_manager_alias(self):
        """Test get_lifecycle_manager alias method."""
        manager = self.pki.get_lifecycle_manager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager, CertificateLifecycleManager)

    def test_full_lifecycle_workflow(self):
        """Test complete lifecycle workflow."""
        # Create lifecycle manager with very high threshold (> 5 years)
        lifecycle = self.pki.create_lifecycle_manager(renewal_threshold_days=2000)

        # Check status of all certificates
        all_status = lifecycle.get_all_certificate_status()
        self.assertEqual(len(all_status), 3)

        # Check for expiring certificates
        expiring = lifecycle.check_expiring_certificates()
        self.assertEqual(len(expiring), 3)  # All expiring with 2000-day threshold

        # Auto-renew expiring certificates
        renewals = lifecycle.auto_renew_expiring_certificates()
        self.assertEqual(len(renewals), 3)

        # Verify all certificates were renewed
        for renewal in renewals:
            self.assertIn("new_serial", renewal)
            self.assertNotEqual(renewal["new_serial"], renewal["old_serial"])


if __name__ == "__main__":
    unittest.main()
