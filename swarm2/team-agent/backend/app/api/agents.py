"""
Agents API - Endpoints for agent management and discovery.

Provides:
- List all registered agents
- Get agent details and stats
- Get agent invocation history
- Agent discovery by capabilities
"""

from flask import Blueprint, jsonify, request
from app.database import get_backend_session
from app.models.agent import AgentCard, AgentInvocation
from sqlalchemy import desc

agents_bp = Blueprint('agents', __name__)


@agents_bp.route('', methods=['GET'])
def list_agents():
    """
    Get all registered agents.

    Query params:
        - type: Filter by agent_type (e.g., "role", "specialist")
        - domain: Filter by trust_domain (e.g., "EXECUTION", "GOVERNMENT")
        - status: Filter by status (e.g., "active", "inactive")

    Returns:
        {
            "agents": [...],
            "total": 4,
            "summary": {
                "by_type": {...},
                "by_domain": {...},
                "by_status": {...}
            }
        }
    """
    try:
        # Get query params
        agent_type = request.args.get('type')
        trust_domain = request.args.get('domain')
        status = request.args.get('status')

        with get_backend_session() as session:
            # Build query
            query = session.query(AgentCard)

            if agent_type:
                query = query.filter(AgentCard.agent_type == agent_type)
            if trust_domain:
                query = query.filter(AgentCard.trust_domain == trust_domain)
            if status:
                query = query.filter(AgentCard.status == status)

            # Order by trust score descending
            query = query.order_by(desc(AgentCard.trust_score))

            agents = query.all()

            # Calculate summary statistics
            all_agents = session.query(AgentCard).all()
            summary = {
                "by_type": {},
                "by_domain": {},
                "by_status": {}
            }

            for agent in all_agents:
                # Count by type
                summary["by_type"][agent.agent_type] = summary["by_type"].get(agent.agent_type, 0) + 1
                # Count by domain
                summary["by_domain"][agent.trust_domain] = summary["by_domain"].get(agent.trust_domain, 0) + 1
                # Count by status
                summary["by_status"][agent.status] = summary["by_status"].get(agent.status, 0) + 1

            return jsonify({
                "agents": [agent.to_dict() for agent in agents],
                "total": len(agents),
                "summary": summary
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """
    Get detailed information about a specific agent.

    Returns:
        {
            "agent": {...},
            "recent_invocations": [...],
            "stats": {...}
        }
    """
    try:
        with get_backend_session() as session:
            agent = session.query(AgentCard).filter_by(agent_id=agent_id).first()

            if not agent:
                return jsonify({"error": "Agent not found"}), 404

            # Get recent invocations
            recent_invocations = session.query(AgentInvocation).filter_by(
                agent_id=agent_id
            ).order_by(desc(AgentInvocation.created_at)).limit(10).all()

            # Calculate additional stats
            all_invocations = session.query(AgentInvocation).filter_by(agent_id=agent_id).all()

            stats = {
                "total_invocations": len(all_invocations),
                "successful_invocations": sum(1 for inv in all_invocations if inv.status == "success"),
                "failed_invocations": sum(1 for inv in all_invocations if inv.status == "failure"),
                "success_rate": agent.success_rate,
                "trust_score": agent.trust_score,
                "average_duration": sum(inv.duration or 0 for inv in all_invocations) / len(all_invocations) if all_invocations else 0
            }

            return jsonify({
                "agent": agent.to_dict(),
                "recent_invocations": [inv.to_dict() for inv in recent_invocations],
                "stats": stats
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agents_bp.route('/<agent_id>/invocations', methods=['GET'])
def get_agent_invocations(agent_id):
    """
    Get invocation history for a specific agent.

    Query params:
        - limit: Number of invocations to return (default: 50)
        - offset: Pagination offset (default: 0)
        - status: Filter by status (success, failure)

    Returns:
        {
            "invocations": [...],
            "total": 100,
            "limit": 50,
            "offset": 0
        }
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        status_filter = request.args.get('status')

        with get_backend_session() as session:
            # Check if agent exists
            agent = session.query(AgentCard).filter_by(agent_id=agent_id).first()
            if not agent:
                return jsonify({"error": "Agent not found"}), 404

            # Build query
            query = session.query(AgentInvocation).filter_by(agent_id=agent_id)

            if status_filter:
                query = query.filter(AgentInvocation.status == status_filter)

            # Get total count
            total = query.count()

            # Get paginated results
            invocations = query.order_by(
                desc(AgentInvocation.created_at)
            ).limit(limit).offset(offset).all()

            return jsonify({
                "invocations": [inv.to_dict() for inv in invocations],
                "total": total,
                "limit": limit,
                "offset": offset
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agents_bp.route('/discover', methods=['POST'])
def discover_agents():
    """
    Discover agents by capabilities or requirements.

    Request body:
        {
            "capabilities": ["code_generation", "python"],
            "trust_domain": "EXECUTION",
            "min_trust_score": 50.0
        }

    Returns:
        {
            "agents": [...],
            "matches": 3
        }
    """
    try:
        data = request.get_json()
        capabilities = data.get('capabilities', [])
        trust_domain = data.get('trust_domain')
        min_trust_score = data.get('min_trust_score', 0.0)

        with get_backend_session() as session:
            query = session.query(AgentCard)

            # Filter by trust domain
            if trust_domain:
                query = query.filter(AgentCard.trust_domain == trust_domain)

            # Filter by minimum trust score
            query = query.filter(AgentCard.trust_score >= min_trust_score)

            # Filter by status (only active agents)
            query = query.filter(AgentCard.status == 'active')

            agents = query.all()

            # Filter by capabilities (checking JSON field)
            if capabilities:
                import json
                matching_agents = []
                for agent in agents:
                    try:
                        agent_caps = json.loads(agent.capabilities) if isinstance(agent.capabilities, str) else agent.capabilities
                        if agent_caps and any(cap in agent_caps for cap in capabilities):
                            matching_agents.append(agent)
                    except:
                        continue
                agents = matching_agents

            # Order by trust score
            agents.sort(key=lambda a: a.trust_score, reverse=True)

            return jsonify({
                "agents": [agent.to_dict() for agent in agents],
                "matches": len(agents)
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agents_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get overall agent system statistics.

    Returns:
        {
            "total_agents": 4,
            "total_invocations": 100,
            "average_trust_score": 85.5,
            "top_agents": [...],
            "recent_activity": [...]
        }
    """
    try:
        with get_backend_session() as session:
            agents = session.query(AgentCard).all()
            invocations = session.query(AgentInvocation).order_by(
                desc(AgentInvocation.created_at)
            ).limit(20).all()

            # Calculate stats
            total_agents = len(agents)
            total_invocations = sum(agent.total_invocations for agent in agents)
            avg_trust_score = sum(agent.trust_score for agent in agents) / total_agents if total_agents > 0 else 0

            # Get top agents by trust score
            top_agents = sorted(agents, key=lambda a: a.trust_score, reverse=True)[:5]

            return jsonify({
                "total_agents": total_agents,
                "total_invocations": total_invocations,
                "average_trust_score": avg_trust_score,
                "top_agents": [agent.to_dict() for agent in top_agents],
                "recent_activity": [inv.to_dict() for inv in invocations]
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
