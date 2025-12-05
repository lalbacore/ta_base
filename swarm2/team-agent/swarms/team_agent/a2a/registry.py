"""
Capability Registry for Agent-to-Agent (A2A) discovery and matching.

This module provides a decentralized capability registry where agents can:
- Publish their capabilities (code generation, data analysis, etc.)
- Discover capabilities offered by other agents
- Match requirements against available capabilities with trust-based scoring
- Track capability reputation and pricing

The registry integrates with:
- PKI system for provider authentication
- Trust scoring for reputation-based ranking
- Smart contracts for decentralized capability marketplace (future)
"""

import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4

from ..crypto import PKIManager, TrustDomain, AgentReputationTracker


class CapabilityType(Enum):
    """Types of capabilities that can be registered."""
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    WEB_SCRAPING = "web_scraping"
    API_INTEGRATION = "api_integration"
    DATABASE_OPERATIONS = "database_operations"
    FILE_PROCESSING = "file_processing"
    NATURAL_LANGUAGE = "natural_language"
    IMAGE_PROCESSING = "image_processing"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    MACHINE_LEARNING = "machine_learning"
    SECURITY_AUDIT = "security_audit"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    CUSTOM = "custom"


class CapabilityStatus(Enum):
    """Status of a registered capability."""
    ACTIVE = "active"           # Available for use
    INACTIVE = "inactive"       # Temporarily unavailable
    REVOKED = "revoked"         # Permanently disabled (trust issue)
    DEPRECATED = "deprecated"   # Being phased out


@dataclass
class Provider:
    """Information about a capability provider (agent or service)."""
    provider_id: str
    provider_type: str  # "agent", "service", "human"
    trust_domain: TrustDomain
    certificate_serial: Optional[str] = None
    trust_score: float = 0.0
    total_operations: int = 0
    success_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Capability:
    """A capability offered by a provider."""
    capability_id: str
    provider_id: str
    capability_type: CapabilityType
    name: str
    description: str
    version: str
    status: CapabilityStatus = CapabilityStatus.ACTIVE

    # Capability metadata
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)  # e.g., {"language": "python"}

    # Pricing and performance
    price: float = 0.0  # Cost per invocation (in tokens or currency)
    estimated_duration: float = 0.0  # Seconds
    max_concurrent: int = 1

    # Reputation metrics
    reputation: float = 100.0  # 0-100 score based on usage history
    total_invocations: int = 0
    successful_invocations: int = 0
    average_rating: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    # Tags and categories
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

    # Contract information (for on-chain capabilities)
    contract_address: Optional[str] = None
    contract_abi: Optional[Dict[str, Any]] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityRequirement:
    """A requirement for a capability match."""
    capability_type: CapabilityType
    required_version: Optional[str] = None
    min_reputation: float = 75.0
    max_price: Optional[float] = None
    max_duration: Optional[float] = None
    required_tags: List[str] = field(default_factory=list)
    required_features: Dict[str, Any] = field(default_factory=dict)
    min_trust_score: float = 75.0


@dataclass
class CapabilityMatch:
    """A capability that matches a requirement with scoring."""
    capability: Capability
    provider: Provider
    match_score: float  # 0-100 (how well it matches)
    trust_score: float  # 0-100 (provider trust)
    reputation_score: float  # 0-100 (capability reputation)
    cost_score: float  # 0-100 (lower cost = higher score)
    overall_score: float  # Weighted average of all scores

    match_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class CapabilityRegistry:
    """
    SQLite-backed capability registry for A2A discovery.

    The registry maintains:
    - Providers (agents/services offering capabilities)
    - Capabilities (specific functions/tools offered)
    - Invocation history (for reputation tracking)
    - Smart contract mappings (for on-chain capabilities)

    Trust Integration:
    - Uses AgentReputationTracker for provider trust scores
    - Filters capabilities based on minimum trust requirements
    - Ranks matches using trust-weighted scoring

    Future: Will integrate with smart contracts for decentralized marketplace.
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        trust_tracker: Optional[AgentReputationTracker] = None,
        pki_manager: Optional[PKIManager] = None
    ):
        """
        Initialize the capability registry.

        Args:
            db_path: Path to SQLite database (default: ~/.team_agent/registry.db)
            trust_tracker: Agent reputation tracker for trust scoring
            pki_manager: PKI manager for certificate verification
        """
        if db_path is None:
            home = Path.home()
            db_path = home / ".team_agent" / "registry.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.trust_tracker = trust_tracker
        self.pki_manager = pki_manager

        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS providers (
                    provider_id TEXT PRIMARY KEY,
                    provider_type TEXT NOT NULL,
                    trust_domain TEXT NOT NULL,
                    certificate_serial TEXT,
                    trust_score REAL DEFAULT 0.0,
                    total_operations INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS capabilities (
                    capability_id TEXT PRIMARY KEY,
                    provider_id TEXT NOT NULL,
                    capability_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT DEFAULT 'active',

                    input_schema TEXT,
                    output_schema TEXT,
                    requirements TEXT,

                    price REAL DEFAULT 0.0,
                    estimated_duration REAL DEFAULT 0.0,
                    max_concurrent INTEGER DEFAULT 1,

                    reputation REAL DEFAULT 100.0,
                    total_invocations INTEGER DEFAULT 0,
                    successful_invocations INTEGER DEFAULT 0,
                    average_rating REAL DEFAULT 0.0,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT,

                    tags TEXT,
                    categories TEXT,

                    contract_address TEXT,
                    contract_abi TEXT,

                    metadata TEXT,

                    FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS invocations (
                    invocation_id TEXT PRIMARY KEY,
                    capability_id TEXT NOT NULL,
                    requester_id TEXT NOT NULL,

                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    duration REAL,

                    status TEXT NOT NULL,
                    error_message TEXT,

                    rating REAL,
                    feedback TEXT,

                    metadata TEXT,

                    FOREIGN KEY (capability_id) REFERENCES capabilities(capability_id)
                )
            """)

            # Indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capabilities_provider
                ON capabilities(provider_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capabilities_type
                ON capabilities(capability_type, status)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capabilities_reputation
                ON capabilities(reputation DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_invocations_capability
                ON invocations(capability_id)
            """)

            conn.commit()

    def register_provider(
        self,
        provider_id: str,
        provider_type: str = "agent",
        trust_domain: TrustDomain = TrustDomain.EXECUTION,
        certificate_serial: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Provider:
        """
        Register a new capability provider.

        Args:
            provider_id: Unique identifier for the provider
            provider_type: Type of provider ("agent", "service", "human")
            trust_domain: PKI trust domain
            certificate_serial: Certificate serial number for verification
            metadata: Additional provider metadata

        Returns:
            Provider object
        """
        # Get trust score from tracker if available
        trust_score = 0.0
        total_operations = 0
        success_rate = 0.0

        if self.trust_tracker:
            metrics = self.trust_tracker.get_agent_metrics(provider_id)
            if metrics:
                trust_score = metrics.trust_score
                total_operations = metrics.total_operations
                success_rate = metrics.success_rate

        provider = Provider(
            provider_id=provider_id,
            provider_type=provider_type,
            trust_domain=trust_domain,
            certificate_serial=certificate_serial,
            trust_score=trust_score,
            total_operations=total_operations,
            success_rate=success_rate,
            metadata=metadata or {}
        )

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO providers
                (provider_id, provider_type, trust_domain, certificate_serial,
                 trust_score, total_operations, success_rate,
                 created_at, last_seen, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                provider.provider_id,
                provider.provider_type,
                provider.trust_domain.value,
                provider.certificate_serial,
                provider.trust_score,
                provider.total_operations,
                provider.success_rate,
                provider.created_at.isoformat(),
                provider.last_seen.isoformat(),
                json.dumps(provider.metadata)
            ))
            conn.commit()

        return provider

    def register_capability(
        self,
        provider_id: str,
        capability_type: CapabilityType,
        name: str,
        description: str,
        version: str = "1.0.0",
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        requirements: Optional[Dict[str, Any]] = None,
        price: float = 0.0,
        estimated_duration: float = 0.0,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Capability:
        """
        Register a new capability.

        Args:
            provider_id: ID of the provider offering this capability
            capability_type: Type of capability
            name: Human-readable name
            description: Detailed description
            version: Semantic version string
            input_schema: JSON schema for inputs
            output_schema: JSON schema for outputs
            requirements: Capability requirements (e.g., {"language": "python"})
            price: Cost per invocation
            estimated_duration: Expected duration in seconds
            tags: List of tags for discovery
            categories: List of categories
            expires_at: Expiration timestamp
            metadata: Additional metadata

        Returns:
            Capability object
        """
        capability_id = f"cap-{uuid4().hex[:12]}"

        capability = Capability(
            capability_id=capability_id,
            provider_id=provider_id,
            capability_type=capability_type,
            name=name,
            description=description,
            version=version,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            requirements=requirements or {},
            price=price,
            estimated_duration=estimated_duration,
            tags=tags or [],
            categories=categories or [],
            expires_at=expires_at,
            metadata=metadata or {}
        )

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT INTO capabilities
                (capability_id, provider_id, capability_type, name, description, version,
                 status, input_schema, output_schema, requirements,
                 price, estimated_duration, max_concurrent,
                 reputation, total_invocations, successful_invocations, average_rating,
                 created_at, updated_at, expires_at,
                 tags, categories, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capability.capability_id,
                capability.provider_id,
                capability.capability_type.value,
                capability.name,
                capability.description,
                capability.version,
                capability.status.value,
                json.dumps(capability.input_schema),
                json.dumps(capability.output_schema),
                json.dumps(capability.requirements),
                capability.price,
                capability.estimated_duration,
                capability.max_concurrent,
                capability.reputation,
                capability.total_invocations,
                capability.successful_invocations,
                capability.average_rating,
                capability.created_at.isoformat(),
                capability.updated_at.isoformat(),
                capability.expires_at.isoformat() if capability.expires_at else None,
                json.dumps(capability.tags),
                json.dumps(capability.categories),
                json.dumps(capability.metadata)
            ))
            conn.commit()

        return capability

    def discover_capabilities(
        self,
        capability_type: Optional[CapabilityType] = None,
        tags: Optional[List[str]] = None,
        min_reputation: float = 0.0,
        min_trust_score: float = 0.0,
        status: CapabilityStatus = CapabilityStatus.ACTIVE,
        limit: int = 100
    ) -> List[Tuple[Capability, Provider]]:
        """
        Discover available capabilities.

        Args:
            capability_type: Filter by capability type
            tags: Filter by tags (must have all tags)
            min_reputation: Minimum reputation score
            min_trust_score: Minimum provider trust score
            status: Capability status
            limit: Maximum number of results

        Returns:
            List of (Capability, Provider) tuples
        """
        query = """
            SELECT c.*, p.*
            FROM capabilities c
            JOIN providers p ON c.provider_id = p.provider_id
            WHERE c.status = ?
            AND c.reputation >= ?
            AND p.trust_score >= ?
        """
        params = [status.value, min_reputation, min_trust_score]

        if capability_type:
            query += " AND c.capability_type = ?"
            params.append(capability_type.value)

        query += " ORDER BY c.reputation DESC, p.trust_score DESC LIMIT ?"
        params.append(limit)

        results = []
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            for row in cursor.fetchall():
                capability = self._row_to_capability(row)
                provider = self._row_to_provider(row)

                # Filter by tags if specified
                if tags:
                    if not all(tag in capability.tags for tag in tags):
                        continue

                results.append((capability, provider))

        return results

    def match_capabilities(
        self,
        requirement: CapabilityRequirement,
        limit: int = 10
    ) -> List[CapabilityMatch]:
        """
        Find and rank capabilities that match a requirement.

        Uses a weighted scoring algorithm:
        - Type match: 40 points (exact match required)
        - Trust score: 30 points (provider trust)
        - Reputation: 20 points (capability reputation)
        - Cost: 10 points (lower cost = higher score)

        Args:
            requirement: Capability requirement specification
            limit: Maximum number of matches to return

        Returns:
            List of CapabilityMatch objects, sorted by overall_score (descending)
        """
        # Discover candidates
        candidates = self.discover_capabilities(
            capability_type=requirement.capability_type,
            tags=requirement.required_tags,
            min_reputation=requirement.min_reputation,
            min_trust_score=requirement.min_trust_score,
            status=CapabilityStatus.ACTIVE,
            limit=limit * 2  # Get more candidates for better filtering
        )

        matches = []

        for capability, provider in candidates:
            # Calculate individual scores
            match_score = self._calculate_match_score(capability, requirement)
            trust_score = provider.trust_score
            reputation_score = capability.reputation
            cost_score = self._calculate_cost_score(capability.price, requirement.max_price)

            # Weighted overall score
            overall_score = (
                match_score * 0.40 +
                trust_score * 0.30 +
                reputation_score * 0.20 +
                cost_score * 0.10
            )

            # Generate match reasons and warnings
            reasons = []
            warnings = []

            if match_score == 100:
                reasons.append("Exact capability type match")

            if trust_score >= 90:
                reasons.append(f"High trust provider ({trust_score:.1f})")
            elif trust_score < requirement.min_trust_score:
                warnings.append(f"Trust score below minimum ({trust_score:.1f} < {requirement.min_trust_score})")

            if reputation_score >= 90:
                reasons.append(f"Excellent reputation ({reputation_score:.1f})")

            if capability.price == 0:
                reasons.append("Free capability")
            elif requirement.max_price and capability.price > requirement.max_price:
                warnings.append(f"Price above budget ({capability.price} > {requirement.max_price})")

            if requirement.max_duration and capability.estimated_duration > requirement.max_duration:
                warnings.append(f"Duration may exceed limit ({capability.estimated_duration}s > {requirement.max_duration}s)")

            match = CapabilityMatch(
                capability=capability,
                provider=provider,
                match_score=match_score,
                trust_score=trust_score,
                reputation_score=reputation_score,
                cost_score=cost_score,
                overall_score=overall_score,
                match_reasons=reasons,
                warnings=warnings
            )

            matches.append(match)

        # Sort by overall score (descending)
        matches.sort(key=lambda m: m.overall_score, reverse=True)

        return matches[:limit]

    def _calculate_match_score(
        self,
        capability: Capability,
        requirement: CapabilityRequirement
    ) -> float:
        """Calculate how well a capability matches a requirement (0-100)."""
        score = 0.0

        # Type match (required)
        if capability.capability_type == requirement.capability_type:
            score = 100.0
        else:
            return 0.0  # No match if type doesn't match

        # Version check (if specified)
        if requirement.required_version:
            if capability.version != requirement.required_version:
                score *= 0.8  # Penalize version mismatch

        # Feature requirements
        if requirement.required_features:
            cap_features = capability.requirements
            missing_features = []

            for feature_key, required_value in requirement.required_features.items():
                if feature_key not in cap_features:
                    missing_features.append(feature_key)
                elif cap_features[feature_key] != required_value:
                    missing_features.append(feature_key)

            if missing_features:
                # Penalize based on missing features
                penalty = len(missing_features) / len(requirement.required_features)
                score *= (1.0 - penalty * 0.5)

        return min(score, 100.0)

    def _calculate_cost_score(
        self,
        price: float,
        max_price: Optional[float]
    ) -> float:
        """Calculate cost score (0-100, lower cost = higher score)."""
        if price == 0:
            return 100.0

        if max_price is None:
            # No budget constraint, score based on absolute price
            # Lower is better: 100 points at $0, decreasing with price
            return max(0.0, 100.0 - price * 10)

        if price > max_price:
            # Over budget
            return 0.0

        # Within budget: linear scale from 0 to 100
        return 100.0 * (1.0 - price / max_price)

    def record_invocation(
        self,
        capability_id: str,
        requester_id: str,
        status: str,
        duration: Optional[float] = None,
        rating: Optional[float] = None,
        feedback: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a capability invocation for reputation tracking.

        Args:
            capability_id: ID of the invoked capability
            requester_id: ID of the requesting agent
            status: Invocation status ("success", "failure", "timeout")
            duration: Actual duration in seconds
            rating: User rating (0-5 stars)
            feedback: User feedback text
            error_message: Error message if failed
            metadata: Additional metadata

        Returns:
            Invocation ID
        """
        invocation_id = f"inv-{uuid4().hex[:12]}"
        now = datetime.utcnow()

        with sqlite3.connect(str(self.db_path)) as conn:
            # Record invocation
            conn.execute("""
                INSERT INTO invocations
                (invocation_id, capability_id, requester_id,
                 started_at, completed_at, duration, status,
                 error_message, rating, feedback, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invocation_id,
                capability_id,
                requester_id,
                now.isoformat(),
                now.isoformat(),
                duration,
                status,
                error_message,
                rating,
                feedback,
                json.dumps(metadata or {})
            ))

            # Update capability statistics
            conn.execute("""
                UPDATE capabilities
                SET total_invocations = total_invocations + 1,
                    successful_invocations = successful_invocations + CASE WHEN ? = 'success' THEN 1 ELSE 0 END,
                    updated_at = ?
                WHERE capability_id = ?
            """, (status, now.isoformat(), capability_id))

            # Update average rating if provided
            if rating is not None:
                cursor = conn.execute("""
                    SELECT average_rating, total_invocations
                    FROM capabilities
                    WHERE capability_id = ?
                """, (capability_id,))
                row = cursor.fetchone()
                if row:
                    current_avg, total = row
                    new_avg = ((current_avg * (total - 1)) + rating) / total

                    conn.execute("""
                        UPDATE capabilities
                        SET average_rating = ?
                        WHERE capability_id = ?
                    """, (new_avg, capability_id))

            # Recalculate reputation score
            self._update_reputation(conn, capability_id)

            conn.commit()

        return invocation_id

    def _update_reputation(self, conn: sqlite3.Connection, capability_id: str):
        """Update capability reputation based on invocation history."""
        cursor = conn.execute("""
            SELECT total_invocations, successful_invocations, average_rating
            FROM capabilities
            WHERE capability_id = ?
        """, (capability_id,))

        row = cursor.fetchone()
        if not row:
            return

        total, successful, avg_rating = row

        if total == 0:
            reputation = 100.0
        else:
            # Success rate: 50% weight
            success_rate = successful / total

            # Average rating: 30% weight (normalized to 0-1)
            rating_score = (avg_rating / 5.0) if avg_rating > 0 else 0.5

            # Volume bonus: 20% weight (logarithmic, maxes at 1.0 for 100+ invocations)
            import math
            volume_score = min(1.0, math.log10(total + 1) / 2.0)

            reputation = (
                success_rate * 50.0 +
                rating_score * 30.0 +
                volume_score * 20.0
            )

        conn.execute("""
            UPDATE capabilities
            SET reputation = ?
            WHERE capability_id = ?
        """, (reputation, capability_id))

    def revoke_capability(
        self,
        capability_id: str,
        reason: str = "Provider request"
    ):
        """
        Revoke a capability (mark as REVOKED).

        Args:
            capability_id: ID of the capability to revoke
            reason: Reason for revocation
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                UPDATE capabilities
                SET status = ?, updated_at = ?, metadata = json_set(metadata, '$.revocation_reason', ?)
                WHERE capability_id = ?
            """, (CapabilityStatus.REVOKED.value, datetime.utcnow().isoformat(), reason, capability_id))
            conn.commit()

    def get_capability(self, capability_id: str) -> Optional[Tuple[Capability, Provider]]:
        """Get a specific capability by ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT c.*, p.*
                FROM capabilities c
                JOIN providers p ON c.provider_id = p.provider_id
                WHERE c.capability_id = ?
            """, (capability_id,))

            row = cursor.fetchone()
            if row:
                return (self._row_to_capability(row), self._row_to_provider(row))

        return None

    def get_provider_capabilities(self, provider_id: str) -> List[Capability]:
        """Get all capabilities for a provider."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM capabilities
                WHERE provider_id = ?
                ORDER BY reputation DESC
            """, (provider_id,))

            return [self._row_to_capability(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            stats = {}

            # Provider stats
            cursor = conn.execute("""
                SELECT COUNT(*) as total,
                       AVG(trust_score) as avg_trust,
                       SUM(total_operations) as total_ops
                FROM providers
            """)
            row = cursor.fetchone()
            stats['providers'] = {
                'total': row[0],
                'average_trust_score': row[1] or 0.0,
                'total_operations': row[2] or 0
            }

            # Capability stats
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM capabilities
                GROUP BY status
            """)
            stats['capabilities'] = {row[0]: row[1] for row in cursor.fetchall()}

            cursor = conn.execute("""
                SELECT COUNT(*) as total,
                       AVG(reputation) as avg_reputation,
                       SUM(total_invocations) as total_invocations
                FROM capabilities
            """)
            row = cursor.fetchone()
            stats['capabilities']['total'] = row[0]
            stats['capabilities']['average_reputation'] = row[1] or 0.0
            stats['capabilities']['total_invocations'] = row[2] or 0

            # Invocation stats
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM invocations
                GROUP BY status
            """)
            stats['invocations'] = {row[0]: row[1] for row in cursor.fetchall()}

            return stats

    def _row_to_capability(self, row: sqlite3.Row) -> Capability:
        """Convert a database row to a Capability object."""
        return Capability(
            capability_id=row['capability_id'],
            provider_id=row['provider_id'],
            capability_type=CapabilityType(row['capability_type']),
            name=row['name'],
            description=row['description'],
            version=row['version'],
            status=CapabilityStatus(row['status']),
            input_schema=json.loads(row['input_schema']),
            output_schema=json.loads(row['output_schema']),
            requirements=json.loads(row['requirements']),
            price=row['price'],
            estimated_duration=row['estimated_duration'],
            max_concurrent=row['max_concurrent'],
            reputation=row['reputation'],
            total_invocations=row['total_invocations'],
            successful_invocations=row['successful_invocations'],
            average_rating=row['average_rating'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            tags=json.loads(row['tags']),
            categories=json.loads(row['categories']),
            contract_address=row['contract_address'],
            contract_abi=json.loads(row['contract_abi']) if row['contract_abi'] else None,
            metadata=json.loads(row['metadata'])
        )

    def _row_to_provider(self, row: sqlite3.Row) -> Provider:
        """Convert a database row to a Provider object."""
        # Handle prefixed column names when joining tables
        provider_id_col = 'provider_id' if 'provider_id' in row.keys() else row['provider_id']

        return Provider(
            provider_id=row['provider_id'],
            provider_type=row['provider_type'],
            trust_domain=TrustDomain(row['trust_domain']),
            certificate_serial=row['certificate_serial'],
            trust_score=row['trust_score'],
            total_operations=row['total_operations'],
            success_rate=row['success_rate'],
            created_at=datetime.fromisoformat(row['created_at']),
            last_seen=datetime.fromisoformat(row['last_seen']),
            metadata=json.loads(row['metadata'])
        )
