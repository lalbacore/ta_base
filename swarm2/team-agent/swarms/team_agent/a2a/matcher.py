"""
Agent Matcher - Advanced matching and scoring for agent selection.

Features:
- Multi-criteria matching with weights
- Scoring algorithms
- Requirement-based matching
- Capability compatibility checking
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .client import AgentCard


@dataclass
class MatchCriteria:
    """Criteria for matching agents to requirements."""

    # Required criteria
    agent_type: Optional[str] = None
    capability_type: Optional[str] = None

    # Trust/quality criteria
    min_trust_score: float = 0.0
    min_success_rate: float = 0.0
    min_total_invocations: int = 0
    min_average_rating: float = 0.0

    # Capability criteria
    required_specialties: List[str] = field(default_factory=list)
    required_tags: List[str] = field(default_factory=list)
    required_languages: List[str] = field(default_factory=list)

    # Scoring weights (should sum to 1.0)
    trust_score_weight: float = 0.4
    success_rate_weight: float = 0.3
    experience_weight: float = 0.2  # Based on total invocations
    rating_weight: float = 0.1

    def __post_init__(self):
        """Validate weights."""
        total_weight = (
            self.trust_score_weight +
            self.success_rate_weight +
            self.experience_weight +
            self.rating_weight
        )
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Scoring weights must sum to 1.0, got {total_weight}")


@dataclass
class MatchResult:
    """Result of agent matching with score."""
    agent: AgentCard
    score: float
    match_reasons: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'agent': self.agent.to_dict(),
            'score': self.score,
            'match_reasons': self.match_reasons
        }


class AgentMatcher:
    """
    Advanced agent matching and scoring.

    Usage:
        matcher = AgentMatcher()

        # Define requirements
        criteria = MatchCriteria(
            capability_type="cloud_infrastructure",
            required_specialties=["aws"],
            min_trust_score=85.0,
            min_success_rate=0.9
        )

        # Find and rank matches
        matches = matcher.match_agents(agents, criteria)

        # Get best match
        if matches:
            best_agent = matches[0].agent
            print(f"Best match: {best_agent.agent_name} (score: {matches[0].score:.2f})")
    """

    def match_agents(
        self,
        agents: List[AgentCard],
        criteria: MatchCriteria
    ) -> List[MatchResult]:
        """
        Match and score agents against criteria.

        Args:
            agents: List of agents to match
            criteria: Matching criteria

        Returns:
            List of matches sorted by score (highest first)
        """
        matches = []

        for agent in agents:
            # Check if agent meets hard requirements
            if not self._meets_requirements(agent, criteria):
                continue

            # Calculate match score
            score, reasons = self._calculate_score(agent, criteria)

            match = MatchResult(
                agent=agent,
                score=score,
                match_reasons=reasons
            )
            matches.append(match)

        # Sort by score (highest first)
        matches.sort(key=lambda m: m.score, reverse=True)

        return matches

    def _meets_requirements(
        self,
        agent: AgentCard,
        criteria: MatchCriteria
    ) -> bool:
        """Check if agent meets hard requirements."""

        # Agent type
        if criteria.agent_type and agent.agent_type != criteria.agent_type:
            return False

        # Trust score
        if agent.trust_score < criteria.min_trust_score:
            return False

        # Success rate
        if agent.success_rate < criteria.min_success_rate:
            return False

        # Total invocations (experience)
        if agent.total_invocations < criteria.min_total_invocations:
            return False

        # Average rating
        if agent.average_rating < criteria.min_average_rating:
            return False

        # Required specialties
        if criteria.required_specialties:
            agent_specs_lower = [s.lower() for s in agent.specialties]
            if not all(spec.lower() in agent_specs_lower for spec in criteria.required_specialties):
                return False

        # Required tags
        if criteria.required_tags:
            agent_tags_lower = [t.lower() for t in agent.tags]
            if not all(tag.lower() in agent_tags_lower for tag in criteria.required_tags):
                return False

        # Required languages
        if criteria.required_languages:
            agent_langs_lower = [l.lower() for l in agent.supported_languages]
            if not all(lang.lower() in agent_langs_lower for lang in criteria.required_languages):
                return False

        # Capability type
        if criteria.capability_type:
            has_capability = any(
                cap.get('capability_type') == criteria.capability_type
                for cap in agent.capabilities
            )
            if not has_capability:
                return False

        return True

    def _calculate_score(
        self,
        agent: AgentCard,
        criteria: MatchCriteria
    ) -> tuple[float, List[str]]:
        """
        Calculate weighted match score.

        Returns:
            (score, reasons) tuple
        """
        reasons = []
        score = 0.0

        # Trust score component (0-100 -> 0-1)
        trust_component = (agent.trust_score / 100.0) * criteria.trust_score_weight
        score += trust_component
        if agent.trust_score >= 90:
            reasons.append(f"High trust score ({agent.trust_score:.1f})")

        # Success rate component (0-1)
        success_component = agent.success_rate * criteria.success_rate_weight
        score += success_component
        if agent.success_rate >= 0.95:
            reasons.append(f"Excellent success rate ({agent.success_rate*100:.1f}%)")

        # Experience component (normalize invocations)
        # Use log scale to prevent huge numbers from dominating
        import math
        if agent.total_invocations > 0:
            # Log scale: 1 invocation = 0, 10 = 0.5, 100 = 0.67, 1000 = 0.75, etc.
            experience_normalized = math.log10(agent.total_invocations + 1) / 3.0
            experience_normalized = min(experience_normalized, 1.0)  # Cap at 1.0
        else:
            experience_normalized = 0.0

        experience_component = experience_normalized * criteria.experience_weight
        score += experience_component
        if agent.total_invocations >= 100:
            reasons.append(f"Experienced ({agent.total_invocations} invocations)")

        # Rating component (0-5 -> 0-1)
        if agent.average_rating > 0:
            rating_component = (agent.average_rating / 5.0) * criteria.rating_weight
            score += rating_component
            if agent.average_rating >= 4.5:
                reasons.append(f"Highly rated ({agent.average_rating:.1f}/5.0)")

        # Bonus for exact capability match
        if criteria.capability_type:
            for cap in agent.capabilities:
                if cap.get('capability_type') == criteria.capability_type:
                    if cap.get('is_primary', False):
                        score += 0.05  # 5% bonus for primary capability
                        reasons.append(f"Primary {criteria.capability_type} capability")
                    break

        # Bonus for specialty match
        if criteria.required_specialties:
            matched_specs = [
                spec for spec in criteria.required_specialties
                if spec.lower() in [s.lower() for s in agent.specialties]
            ]
            if matched_specs:
                reasons.append(f"Specialties: {', '.join(matched_specs)}")

        # Ensure score is in [0, 1] range
        score = max(0.0, min(1.0, score))

        return score, reasons

    def get_best_match(
        self,
        agents: List[AgentCard],
        criteria: MatchCriteria
    ) -> Optional[MatchResult]:
        """
        Get single best matching agent.

        Args:
            agents: List of agents to match
            criteria: Matching criteria

        Returns:
            Best match or None if no matches
        """
        matches = self.match_agents(agents, criteria)

        if matches:
            return matches[0]

        return None
