"""
MCP Server Implementation.

Exposes agent capabilities as Model Context Protocol (MCP) tools.
Supports both HTTP and WebSocket transport.
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
import importlib
import json
from datetime import datetime
import os

from app.database import get_backend_session
from app.models.agent import AgentCard, CapabilityRegistry, AgentCapabilityMapping

# Create Blueprint
mcp_bp = Blueprint('mcp', __name__)

@mcp_bp.route('/mcp/tools', methods=['GET'])
def list_tools():
    """List all available MCP tools."""
    try:
        with get_backend_session() as session:
            capabilities = session.query(CapabilityRegistry).filter_by(status='active').all()

            tools = []
            for cap in capabilities:
                # Basic input schema based on capability type
                # In a real implementation, this would be stored in the DB as JSON schema
                input_schema = {
                    "type": "object",
                    "properties": {
                        "mission": {"type": "string", "description": "Mission description"},
                        "context": {"type": "object", "description": "Additional context"}
                    },
                    "required": ["mission"]
                }
                
                tools.append({
                    "name": cap.capability_id,
                    "description": cap.description,
                    "input_schema": input_schema,
                    "version": cap.version,
                    "capability_type": cap.capability_type
                })

            return jsonify({"tools": tools})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mcp_bp.route('/mcp/tools/<tool_name>/invoke', methods=['POST'])
def invoke_tool(tool_name):
    """Invoke a capability via MCP."""
    payload = request.json
    
    # Authenticate request (Simple API Key for now)
    api_key = request.headers.get('X-API-Key')
    if not validate_api_key(api_key):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with get_backend_session() as session:
            # Check if capability exists
            cap = session.query(CapabilityRegistry).filter_by(
                capability_id=tool_name,
                status='active'
            ).first()

            if not cap:
                return jsonify({"error": "Tool not found"}), 404

            # Find agent that can execute this capability
            mapping = session.query(AgentCapabilityMapping).filter_by(
                capability_id=tool_name,
                is_primary=True
            ).first()

            if not mapping:
                # Fallback to any agent
                mapping = session.query(AgentCapabilityMapping).filter_by(
                    capability_id=tool_name
                ).first()

            if not mapping:
                return jsonify({"error": "No agent available for this capability"}), 404

            agent_card = session.query(AgentCard).filter_by(
                agent_id=mapping.agent_id
            ).first()

            # Execute capability
            # We need to dynamically load the agent class
            try:
                module = importlib.import_module(agent_card.module_path)
                # Assuming class name matches Convention or is stored (it is stored in agent_card)
                # But wait, agent_card table has class_name?
                # Let's check AgentCard model or assume class_name is correct
                specialist_class = getattr(module, agent_card.class_name)
                specialist = specialist_class()
                
                # Execute
                # Most specialists expect 'mission' string or dict
                result = specialist.run(payload.get('mission', payload))
                
                return jsonify({
                    "status": "success",
                    "agent": agent_card.agent_name,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })

            except ImportError:
                return jsonify({"error": f"Could not load agent module {agent_card.module_path}"}), 500
            except AttributeError:
                return jsonify({"error": f"Could not find agent class {agent_card.class_name}"}), 500
            except Exception as e:
                return jsonify({"error": f"Execution failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def validate_api_key(api_key: str) -> bool:
    """Validate API key for MCP access."""
    # In production, check against DB or Vault
    valid_key = os.getenv('MCP_API_KEY')
    if not valid_key:
        return True # Open if no key configured (Dev mode)
    return api_key == valid_key
