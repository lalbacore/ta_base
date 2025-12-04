"""
Agent Trust Scoring System for Team Agent PKI.

Tracks agent behavior, calculates reputation scores, and maintains
trust metrics over time.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class EventType(Enum):
    """Agent event types for reputation tracking."""
    OPERATION_SUCCESS = "operation_success"
    OPERATION_FAILURE = "operation_failure"
    OPERATION_ERROR = "operation_error"
    CERTIFICATE_REVOKED = "certificate_revoked"
    POLICY_VIOLATION = "policy_violation"
    SECURITY_INCIDENT = "security_incident"
    UPTIME_START = "uptime_start"
    UPTIME_END = "uptime_end"


@dataclass
class TrustMetrics:
    """Trust metrics for an agent."""
    agent_id: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    error_operations: int
    security_incidents: int
    certificate_revocations: int
    policy_violations: int
    total_uptime_seconds: float
    average_response_time: float
    last_seen: datetime
    trust_score: float

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_operations == 0:
            return 100.0
        return (self.successful_operations / self.total_operations) * 100

    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.error_operations / self.total_operations) * 100

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.failed_operations / self.total_operations) * 100


class AgentReputationTracker:
    """
    Agent Reputation Tracker for PKI trust scoring.

    Features:
    - Track agent operations (success/failure/error)
    - Record security incidents and policy violations
    - Calculate trust scores based on weighted metrics
    - Persist reputation data to SQLite
    - Query historical trust data
    - CLI integration
    """

    # Default weights for trust score calculation
    DEFAULT_WEIGHTS = {
        'success_rate': 0.40,      # 40% weight
        'error_rate': 0.20,        # 20% weight (inverted)
        'security': 0.25,          # 25% weight
        'uptime': 0.15,            # 15% weight
    }

    def __init__(
        self,
        db_path: Optional[Path] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize Agent Reputation Tracker.

        Args:
            db_path: Path to SQLite database (default: .team_agent/trust.db)
            weights: Custom weights for trust score calculation
        """
        if db_path is None:
            db_path = Path.home() / ".team_agent" / "trust.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                total_operations INTEGER DEFAULT 0,
                successful_operations INTEGER DEFAULT 0,
                failed_operations INTEGER DEFAULT 0,
                error_operations INTEGER DEFAULT 0,
                security_incidents INTEGER DEFAULT 0,
                certificate_revocations INTEGER DEFAULT 0,
                policy_violations INTEGER DEFAULT 0,
                total_uptime_seconds REAL DEFAULT 0.0,
                average_response_time REAL DEFAULT 0.0,
                trust_score REAL DEFAULT 100.0
            )
        """)

        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        # Trust score history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trust_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                trust_score REAL NOT NULL,
                success_rate REAL,
                error_rate REAL,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        conn.commit()
        conn.close()

    def register_agent(self, agent_id: str) -> bool:
        """
        Register a new agent for reputation tracking.

        Args:
            agent_id: Unique agent identifier

        Returns:
            True if registered, False if already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            now = datetime.utcnow().isoformat() + "Z"
            cursor.execute("""
                INSERT INTO agents (agent_id, created_at, last_seen)
                VALUES (?, ?, ?)
            """, (agent_id, now, now))
            conn.commit()
            logger.info(f"Registered new agent: {agent_id}")
            return True
        except sqlite3.IntegrityError:
            logger.debug(f"Agent already registered: {agent_id}")
            return False
        finally:
            conn.close()

    def record_event(
        self,
        agent_id: str,
        event_type: EventType,
        metadata: Optional[Dict[str, Any]] = None,
        response_time: Optional[float] = None
    ):
        """
        Record an agent event and update metrics.

        Args:
            agent_id: Agent identifier
            event_type: Type of event (EventType enum)
            metadata: Optional event metadata (JSON)
            response_time: Optional response time in seconds
        """
        # Ensure agent is registered
        self.register_agent(agent_id)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat() + "Z"

        # Record event
        import json
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute("""
            INSERT INTO events (agent_id, event_type, timestamp, metadata)
            VALUES (?, ?, ?, ?)
        """, (agent_id, event_type.value, now, metadata_json))

        # Update agent metrics
        updates = {"last_seen": now}

        if event_type == EventType.OPERATION_SUCCESS:
            updates["total_operations"] = "total_operations + 1"
            updates["successful_operations"] = "successful_operations + 1"
        elif event_type == EventType.OPERATION_FAILURE:
            updates["total_operations"] = "total_operations + 1"
            updates["failed_operations"] = "failed_operations + 1"
        elif event_type == EventType.OPERATION_ERROR:
            updates["total_operations"] = "total_operations + 1"
            updates["error_operations"] = "error_operations + 1"
        elif event_type == EventType.CERTIFICATE_REVOKED:
            updates["certificate_revocations"] = "certificate_revocations + 1"
            updates["security_incidents"] = "security_incidents + 1"
        elif event_type == EventType.POLICY_VIOLATION:
            updates["policy_violations"] = "policy_violations + 1"
            updates["security_incidents"] = "security_incidents + 1"
        elif event_type == EventType.SECURITY_INCIDENT:
            updates["security_incidents"] = "security_incidents + 1"

        # Update average response time if provided
        if response_time is not None:
            cursor.execute("""
                SELECT average_response_time, total_operations
                FROM agents WHERE agent_id = ?
            """, (agent_id,))
            row = cursor.fetchone()
            if row:
                old_avg, total_ops = row
                if total_ops > 0:
                    new_avg = ((old_avg * total_ops) + response_time) / (total_ops + 1)
                else:
                    new_avg = response_time
                updates["average_response_time"] = f"{new_avg}"

        # Build UPDATE query
        set_clauses = []
        params = []
        for key, value in updates.items():
            if key == "last_seen":
                set_clauses.append(f"{key} = ?")
                params.append(value)
            elif key == "average_response_time":
                set_clauses.append(f"{key} = ?")
                params.append(float(value))
            else:
                set_clauses.append(f"{key} = {value}")

        params.append(agent_id)

        cursor.execute(f"""
            UPDATE agents
            SET {', '.join(set_clauses)}
            WHERE agent_id = ?
        """, params)

        conn.commit()
        conn.close()

        # Recalculate trust score
        self._update_trust_score(agent_id)

    def _update_trust_score(self, agent_id: str):
        """
        Calculate and update trust score for an agent.

        Trust score formula (0-100):
        - Success rate: 40% weight
        - Error rate: 20% weight (inverted)
        - Security incidents: 25% weight (penalty)
        - Uptime: 15% weight
        """
        metrics = self.get_agent_metrics(agent_id)
        if not metrics:
            return

        # Calculate component scores (0-100)
        success_score = metrics.success_rate
        error_score = 100.0 - metrics.error_rate

        # Security score: penalize for incidents
        max_incidents = 10  # After 10 incidents, score is 0
        security_score = max(0, 100.0 - (metrics.security_incidents / max_incidents * 100))

        # Uptime score: simplified (always 100 for now, can be enhanced)
        uptime_score = 100.0

        # Weighted average
        trust_score = (
            success_score * self.weights['success_rate'] +
            error_score * self.weights['error_rate'] +
            security_score * self.weights['security'] +
            uptime_score * self.weights['uptime']
        )

        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat() + "Z"

        cursor.execute("""
            UPDATE agents
            SET trust_score = ?
            WHERE agent_id = ?
        """, (trust_score, agent_id))

        # Record in history
        cursor.execute("""
            INSERT INTO trust_history (agent_id, timestamp, trust_score, success_rate, error_rate)
            VALUES (?, ?, ?, ?, ?)
        """, (agent_id, now, trust_score, metrics.success_rate, metrics.error_rate))

        conn.commit()
        conn.close()

    def get_agent_metrics(self, agent_id: str) -> Optional[TrustMetrics]:
        """
        Get current trust metrics for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            TrustMetrics object or None if agent not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agent_id, total_operations, successful_operations,
                   failed_operations, error_operations, security_incidents,
                   certificate_revocations, policy_violations, total_uptime_seconds,
                   average_response_time, last_seen, trust_score
            FROM agents WHERE agent_id = ?
        """, (agent_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return TrustMetrics(
            agent_id=row[0],
            total_operations=row[1],
            successful_operations=row[2],
            failed_operations=row[3],
            error_operations=row[4],
            security_incidents=row[5],
            certificate_revocations=row[6],
            policy_violations=row[7],
            total_uptime_seconds=row[8],
            average_response_time=row[9],
            last_seen=datetime.fromisoformat(row[10].rstrip('Z')),
            trust_score=row[11]
        )

    def list_all_agents(self) -> List[TrustMetrics]:
        """
        List all registered agents with their metrics.

        Returns:
            List of TrustMetrics objects sorted by trust score (descending)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agent_id, total_operations, successful_operations,
                   failed_operations, error_operations, security_incidents,
                   certificate_revocations, policy_violations, total_uptime_seconds,
                   average_response_time, last_seen, trust_score
            FROM agents
            ORDER BY trust_score DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        agents = []
        for row in rows:
            agents.append(TrustMetrics(
                agent_id=row[0],
                total_operations=row[1],
                successful_operations=row[2],
                failed_operations=row[3],
                error_operations=row[4],
                security_incidents=row[5],
                certificate_revocations=row[6],
                policy_violations=row[7],
                total_uptime_seconds=row[8],
                average_response_time=row[9],
                last_seen=datetime.fromisoformat(row[10].rstrip('Z')),
                trust_score=row[11]
            ))

        return agents

    def get_trust_history(
        self,
        agent_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical trust scores for an agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum number of records to return

        Returns:
            List of historical trust score records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT timestamp, trust_score, success_rate, error_rate
            FROM trust_history
            WHERE agent_id = ?
            ORDER BY timestamp DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (agent_id,))
        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                "timestamp": row[0],
                "trust_score": row[1],
                "success_rate": row[2],
                "error_rate": row[3]
            })

        return history

    def get_recent_events(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent events for an agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT event_type, timestamp, metadata
            FROM events
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (agent_id, limit))

        rows = cursor.fetchall()
        conn.close()

        events = []
        import json
        for row in rows:
            metadata = json.loads(row[2]) if row[2] else None
            events.append({
                "event_type": row[0],
                "timestamp": row[1],
                "metadata": metadata
            })

        return events

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent and all associated data.

        Args:
            agent_id: Agent identifier

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete from all tables
        cursor.execute("DELETE FROM events WHERE agent_id = ?", (agent_id,))
        cursor.execute("DELETE FROM trust_history WHERE agent_id = ?", (agent_id,))
        cursor.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            logger.info(f"Deleted agent: {agent_id}")

        return deleted

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall system statistics.

        Returns:
            Dict with system-wide statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_agents,
                AVG(trust_score) as average_trust_score,
                MIN(trust_score) as min_trust_score,
                MAX(trust_score) as max_trust_score,
                SUM(total_operations) as total_operations,
                SUM(security_incidents) as total_security_incidents
            FROM agents
        """)

        row = cursor.fetchone()
        conn.close()

        return {
            "total_agents": row[0] or 0,
            "average_trust_score": row[1] or 0.0,
            "min_trust_score": row[2] or 0.0,
            "max_trust_score": row[3] or 100.0,
            "total_operations": row[4] or 0,
            "total_security_incidents": row[5] or 0
        }
