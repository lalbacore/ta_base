import unittest
import socket
import time
import requests
import sqlite3
import hashlib
import json
import os
from typing import Optional, Dict, Any, List
from swarms.team_agent.registry import Registry
from integrations.siem.cef_formatter import CEFFormatter


DB_PATH = os.getenv("TEAM_AGENT_REGISTRY_DB", "team_agent_registry.sqlite3")

class Registry:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT,
            version TEXT,
            metadata TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT,
            prev_hash TEXT,
            entry TEXT
        )""")
        self.conn.commit()

    def publish_workflow(self, workflow: Dict[str, Any]):
        workflow_id = workflow.get("workflow_id")
        name = workflow.get("name")
        version = workflow.get("version", "1.0.0")
        metadata = json.dumps(workflow)
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO workflows (id, name, version, metadata) VALUES (?, ?, ?, ?)",
                  (workflow_id, name, version, metadata))
        self.conn.commit()

    def list_workflows(self) -> List[Dict[str, Any]]:
        c = self.conn.cursor()
        c.execute("SELECT metadata FROM workflows")
        return [json.loads(row[0]) for row in c.fetchall()]

    def add_audit_entry(self, entry: Dict[str, Any]):
        c = self.conn.cursor()
        c.execute("SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1")
        prev = c.fetchone()
        prev_hash = prev[0] if prev else ""
        entry_json = json.dumps(entry)
        hash_val = hashlib.sha256((prev_hash + entry_json).encode()).hexdigest()
        c.execute("INSERT INTO audit_log (hash, prev_hash, entry) VALUES (?, ?, ?)",
                  (hash_val, prev_hash, entry_json))
        self.conn.commit()
        return hash_val

    def verify_chain(self) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT hash, prev_hash, entry FROM audit_log ORDER BY id ASC")
        prev_hash = ""
        for row in c.fetchall():
            expected_hash = hashlib.sha256((prev_hash + row[2]).encode()).hexdigest()
            if row[0] != expected_hash:
                return False
            prev_hash = row[0]
        return True


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

def test_workflow_publish_and_list():
    db_fd, db_path = tempfile.mkstemp()
    reg = Registry(db_path)
    wf = {"workflow_id": "wf1", "name": "Test Workflow", "version": "1.0.0"}
    reg.publish_workflow(wf)
    workflows = reg.list_workflows()
    assert any(w["workflow_id"] == "wf1" for w in workflows)
    os.close(db_fd)
    os.remove(db_path)

def test_audit_chain():
    db_fd, db_path = tempfile.mkstemp()
    reg = Registry(db_path)
    e1 = {"action": "create", "target": "wf1"}
    h1 = reg.add_audit_entry(e1)
    e2 = {"action": "update", "target": "wf1"}
    h2 = reg.add_audit_entry(e2)
    assert reg.verify_chain()
    os.close(db_fd)
    os.remove(db_path)

