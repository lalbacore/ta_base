import unittest
from storage.models import WorkflowRecord, SIEMConnector
from integrations.siem.cef_formatter import CEFFormatter, CEFValidator
from integrations.siem.connector import SIEMExporter


class TestCEFFormatter(unittest.TestCase):
    """Test CEF formatting."""
    
    def setUp(self):
        """Create a sample workflow record."""
        self.record = {
            "workflow_id": "wf_001",
            "status": "success",
            "request": "Build a system",
            "composite_score": {"overall": 85.0},
            "signature": {"hash": "abc123def456"},
            "stages": {
                "architect": {"status": "complete"},
                "builder": {"status": "complete"},
                "critic": {"status": "complete"},
                "governance": {"status": "complete"},
                "recorder": {"status": "complete"}
            }
        }
    
    def test_cef_formatter_creates_valid_event(self):
        """Test that CEF formatter creates valid CEF events."""
        cef_event = CEFFormatter.format_workflow_record(self.record)
        self.assertTrue(cef_event.startswith("CEF:"))
        self.assertIn("TeamAgent", cef_event)
        self.assertIn("wf_001", cef_event)
        self.assertIn("Build a system", cef_event)
    
    def test_cef_formatter_includes_severity(self):
        """Test that CEF event includes severity level."""
        cef_event = CEFFormatter.format_workflow_record(self.record)
        parts = cef_event.split("|")
        severity = parts[6]
        self.assertTrue(severity.isdigit())
        self.assertGreaterEqual(int(severity), 0)
        self.assertLessEqual(int(severity), 10)
    
    def test_cef_severity_calculation_success(self):
        """Test severity calculation for successful workflows."""
        record_success = {
            "status": "success",
            "composite_score": {"overall": 85.0},
            "stages": {}
        }
        severity = CEFFormatter._calculate_severity(record_success)
        self.assertEqual(severity, 3)
    
    def test_cef_severity_calculation_partial_success(self):
        """Test severity calculation for partial success."""
        record_partial = {
            "status": "success",
            "composite_score": {"overall": 60.0},
            "stages": {}
        }
        severity = CEFFormatter._calculate_severity(record_partial)
        self.assertEqual(severity, 5)
    
    def test_cef_severity_calculation_rejected(self):
        """Test severity calculation for rejected workflows."""
        record_rejected = {
            "status": "rejected",
            "composite_score": {"overall": 0},
            "stages": {}
        }
        severity = CEFFormatter._calculate_severity(record_rejected)
        self.assertEqual(severity, 7)
    
    def test_cef_severity_calculation_failed(self):
        """Test severity calculation for failed workflows."""
        record_failed = {
            "status": "failed",
            "composite_score": {"overall": 0},
            "stages": {}
        }
        severity = CEFFormatter._calculate_severity(record_failed)
        self.assertEqual(severity, 9)
    
    def test_cef_formatter_batch(self):
        """Test formatting multiple records."""
        records = [self.record, self.record, self.record]
        cef_events = CEFFormatter.format_batch(records)
        self.assertEqual(len(cef_events), 3)
        for event in cef_events:
            self.assertTrue(event.startswith("CEF:"))
    
    def test_cef_escapes_special_characters(self):
        """Test that CEF formatter escapes special characters."""
        record_with_equals = {
            "workflow_id": "wf_001",
            "status": "success",
            "request": "Build a=b system",
            "composite_score": {"overall": 85.0},
            "signature": {"hash": "abc123"},
            "stages": {}
        }
        cef_event = CEFFormatter.format_workflow_record(record_with_equals)
        self.assertIn("Build a\\=b system", cef_event)


class TestCEFValidator(unittest.TestCase):
    """Test CEF format validation."""
    
    def test_validator_accepts_valid_cef(self):
        """Test that validator accepts valid CEF events."""
        valid_cef = "CEF:0|TeamAgent|WorkflowOrchestration|1.0|WORKFLOW|WorkflowExecution|5|msg=test"
        self.assertTrue(CEFValidator.validate(valid_cef))
    
    def test_validator_rejects_invalid_header(self):
        """Test that validator rejects events without CEF header."""
        invalid_cef = "LOG:0|vendor|product|version|event_id|name|5|msg=test"
        self.assertFalse(CEFValidator.validate(invalid_cef))
    
    def test_validator_rejects_incomplete_event(self):
        """Test that validator rejects incomplete events."""
        incomplete_cef = "CEF:0|vendor"
        self.assertFalse(CEFValidator.validate(incomplete_cef))
    
    def test_validator_batch(self):
        """Test batch validation."""
        events = [
            "CEF:0|vendor|product|version|id|name|5|msg=test",
            "CEF:0|vendor|product|version|id|name|5|msg=test",
            "INVALID",
            "CEF:0|vendor|product|version|id|name|5|msg=test"
        ]
        results = CEFValidator.validate_batch(events)
        self.assertEqual(results["total"], 4)
        self.assertEqual(results["valid"], 3)
        self.assertEqual(results["invalid"], 1)


class TestSIEMExporter(unittest.TestCase):
    """Test SIEM export functionality."""
    
    def setUp(self):
        """Initialize SIEM exporter."""
        self.exporter = SIEMExporter()
    
    def test_siem_exporter_initialization(self):
        """Test that SIEM exporter initializes properly."""
        self.assertIsNotNone(self.exporter.storage)
        self.assertEqual(self.exporter.batch_size, 100)
    
    def test_siem_exporter_get_connectors(self):
        """Test getting SIEM connectors."""
        connectors = self.exporter.get_connectors(enabled_only=False)
        self.assertIsInstance(connectors, list)
    
    def test_siem_exporter_export_single_record(self):
        """Test exporting a single workflow record."""
        record = WorkflowRecord(
            workflow_id="wf_001",
            team_id="team_001",
            request="Build a system",
            status="success",
            result={},
            stages={"architect": {"status": "complete"}},
            composite_score={"overall": 85.0},
            signature={"algorithm": "SHA256", "hash": "abc123"}
        )
        result = self.exporter.export_workflow_record(record)
        self.assertIn("workflow_id", result)
        self.assertEqual(result["workflow_id"], "wf_001")
        self.assertIn("connectors", result)
    
    def test_siem_exporter_export_batch(self):
        """Test exporting multiple records."""
        records = [
            WorkflowRecord(
                workflow_id=f"wf_{i:03d}",
                team_id="team_001",
                request="Build a system",
                status="success",
                result={},
                stages={},
                composite_score={"overall": 85.0},
                signature={"hash": f"hash_{i}"}
            )
            for i in range(5)
        ]
        result = self.exporter.export_batch(records)
        self.assertEqual(result["total_records"], 5)
        self.assertIn("validation", result)
        self.assertIn("connectors", result)
    
    def test_siem_exporter_sends_to_connector(self):
        """Test sending data to a SIEM connector."""
        connector = SIEMConnector(
            id="siem_001",
            name="Splunk",
            enabled=True,
            connector_type="splunk",
            endpoint="https://splunk.example.com:8088",
            credentials={"token": "secret"}
        )
        cef_event = "CEF:0|vendor|product|version|id|name|5|msg=test"
        result = self.exporter._send_to_connector(connector, cef_event)
        self.assertEqual(result["status"], "queued")
        self.assertEqual(result["connector_type"], "splunk")
        self.assertEqual(result["format"], "CEF")


if __name__ == '__main__':
    unittest.main()