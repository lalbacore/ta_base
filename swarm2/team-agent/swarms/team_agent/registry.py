import sqlite3
import hashlib
import json
import os
from typing import Optional, Dict, Any, List

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
