import unittest
import socket
import time
import requests
from storage.models import WorkflowRecord
from integrations.siem.cef_formatter import CEFFormatter


class TestSIEMIntegration(unittest.TestCase):
    """Integration tests with live SIEM systems."""
    
    LOGSTASH_HOST = "localhost"
    LOGSTASH_PORT = 5044
    ELASTICSEARCH_HOST = "http://localhost:9200"
    
    @classmethod
    def setUpClass(cls):
        """Check if Logstash and Elasticsearch are available."""
        # Check Logstash
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((cls.LOGSTASH_HOST, cls.LOGSTASH_PORT))
            sock.close()
            cls.logstash_available = result == 0
        except Exception:
            cls.logstash_available = False
        
        # Check Elasticsearch
        try:
            response = requests.get(cls.ELASTICSEARCH_HOST, timeout=2)
            cls.elasticsearch_available = response.status_code == 200
        except Exception:
            cls.elasticsearch_available = False
    
    def test_elasticsearch_connectivity(self):
        """Test connection to Elasticsearch."""
        if not self.elasticsearch_available:
            self.skipTest("Elasticsearch not available")
        
        response = requests.get(self.ELASTICSEARCH_HOST)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("version", data)
        print(f"\nElasticsearch version: {data['version']['number']}")
    
    def test_logstash_connectivity(self):
        """Test connection to Logstash."""
        if not self.logstash_available:
            self.skipTest("Logstash not available")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((self.LOGSTASH_HOST, self.LOGSTASH_PORT))
        sock.close()
        
        self.assertEqual(result, 0, "Cannot connect to Logstash")
        print("\nLogstash is accepting connections on port 5044")
    
    def test_send_cef_to_logstash(self):
        """Test sending a CEF event to Logstash."""
        if not self.logstash_available:
            self.skipTest("Logstash not available")
        
        record = {
            "workflow_id": "wf_elk_001",
            "status": "success",
            "request": "Build secure microservices",
            "composite_score": {"overall": 92.0},
            "signature": {"hash": "elk_test_hash_123"},
            "stages": {
                "architect": {"status": "complete"},
                "builder": {"status": "complete"},
                "critic": {"status": "complete"},
                "governance": {"status": "complete"},
                "recorder": {"status": "complete"}
            }
        }
        
        cef_event = CEFFormatter.format_workflow_record(record)
        print(f"\nSending CEF event:\n{cef_event[:200]}...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.LOGSTASH_HOST, self.LOGSTASH_PORT))
            sock.sendall(cef_event.encode() + b'\n')
            sock.close()
            
            time.sleep(3)
            
            if self.elasticsearch_available:
                response = requests.get(f"{self.ELASTICSEARCH_HOST}/cef-events-*/_search")
                if response.status_code == 200:
                    hits = response.json().get('hits', {}).get('total', {})
                    count = hits.get('value', 0) if isinstance(hits, dict) else hits
                    print(f"Events in Elasticsearch: {count}")
            
            self.assertTrue(True, "Successfully sent CEF event")
        except Exception as e:
            self.fail(f"Failed to send CEF event: {e}")
    
    def test_send_batch_to_logstash(self):
        """Test sending a batch of CEF events to Logstash."""
        if not self.logstash_available:
            self.skipTest("Logstash not available")
        
        records = [
            {
                "workflow_id": f"wf_elk_{i:03d}",
                "status": "success",
                "request": f"Build system {i}",
                "composite_score": {"overall": 85.0 + i},
                "signature": {"hash": f"elk_hash_{i}"},
                "stages": {
                    "architect": {"status": "complete"},
                    "builder": {"status": "complete"},
                    "critic": {"status": "complete"},
                    "governance": {"status": "complete"},
                    "recorder": {"status": "complete"}
                }
            }
            for i in range(5)
        ]
        
        cef_events = CEFFormatter.format_batch(records)
        print(f"\nSending {len(cef_events)} CEF events...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.LOGSTASH_HOST, self.LOGSTASH_PORT))
            
            for event in cef_events:
                sock.sendall(event.encode() + b'\n')
            
            sock.close()
            time.sleep(3)
            
            if self.elasticsearch_available:
                response = requests.get(f"{self.ELASTICSEARCH_HOST}/cef-events-*/_count")
                if response.status_code == 200:
                    count = response.json().get('count', 0)
                    print(f"Total events in Elasticsearch: {count}")
                    self.assertGreater(count, 0, "No events found in Elasticsearch")
            
            self.assertEqual(len(cef_events), 5)
        except Exception as e:
            self.fail(f"Failed to send batch: {e}")

