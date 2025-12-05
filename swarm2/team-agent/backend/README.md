# Team Agent Backend

Flask REST API and WebSocket server for the Team Agent platform.

## Features

- **REST API**: Full CRUD operations for missions, trust, PKI, registry, governance, and artifacts
- **WebSocket**: Real-time updates for workflow progress, trust scores, and PKI events
- **Service Layer**: Bridges Flask API to existing Team Agent Python codebase
- **CORS**: Configured for cross-origin requests from Vue frontend

## Tech Stack

- **Framework**: Flask 3.0
- **WebSockets**: Flask-SocketIO with python-socketio
- **CORS**: Flask-CORS for cross-origin support
- **WSGI Server**: Gunicorn for production deployment

## Project Structure

```
backend/
├── app.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── app/
│   ├── __init__.py                 # App factory
│   ├── api/                        # REST API blueprints
│   │   ├── mission.py              # Mission endpoints
│   │   ├── trust.py                # Trust endpoints
│   │   ├── pki.py                  # PKI endpoints
│   │   ├── registry.py             # Registry endpoints
│   │   ├── governance.py           # Governance endpoints
│   │   └── artifacts.py            # Artifacts endpoints
│   ├── websocket/                  # WebSocket handlers
│   │   ├── workflow_handler.py     # Workflow real-time updates
│   │   ├── trust_handler.py        # Trust score updates
│   │   └── pki_handler.py          # Certificate events
│   └── services/                   # Business logic layer
│       ├── mission_service.py      # Mission orchestration bridge
│       ├── trust_service.py        # Trust tracker bridge
│       ├── pki_service.py          # PKI manager bridge
│       ├── registry_service.py     # Registry bridge
│       ├── governance_service.py   # Governance bridge
│       └── artifacts_service.py    # Manifest generator bridge
```

## Installation

### Prerequisites

- Python 3.9+
- pip or poetry

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and set SECRET_KEY
```

## Development

### Run Development Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Run with Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet app:app
```

## API Endpoints

### Mission Management

- `POST /api/mission/submit` - Submit new mission
- `GET /api/mission/list` - List all missions
- `GET /api/mission/<mission_id>` - Get mission details
- `GET /api/mission/workflow/<workflow_id>/status` - Get workflow status
- `POST /api/mission/workflow/<workflow_id>/resume` - Resume workflow
- `POST /api/mission/breakpoint/<breakpoint_id>/approve` - Approve breakpoint
- `POST /api/mission/breakpoint/<breakpoint_id>/reject` - Reject breakpoint

### Trust Management

- `GET /api/trust/agents` - Get all agents with metrics
- `GET /api/trust/agent/<agent_id>` - Get agent details
- `GET /api/trust/agent/<agent_id>/history` - Get trust history
- `GET /api/trust/agent/<agent_id>/events` - Get trust events
- `POST /api/trust/agent/<agent_id>/event` - Record event

### PKI Management

- `GET /api/pki/status` - Get all certificates
- `GET /api/pki/certificate/<domain>` - Get certificate details
- `POST /api/pki/renew/<domain>` - Renew certificate
- `POST /api/pki/rotate/<domain>` - Rotate certificate
- `POST /api/pki/revoke` - Revoke certificate
- `GET /api/pki/revoked` - Get revoked certificates
- `GET /api/pki/crl` - Get CRL

### Registry

- `GET /api/registry/capabilities` - List/search capabilities
- `GET /api/registry/capability/<capability_id>` - Get capability
- `GET /api/registry/providers` - List providers
- `GET /api/registry/provider/<provider_id>` - Get provider
- `POST /api/registry/discover` - Discover capabilities
- `POST /api/registry/match` - Match capabilities
- `POST /api/registry/capability/<capability_id>/revoke` - Revoke capability

### Governance

- `GET /api/policy/config` - Get policy config
- `PUT /api/policy/config` - Update policy config
- `GET /api/governance/decisions` - Get decision history
- `GET /api/approval/pending` - Get pending gates
- `POST /api/approval/<gate_id>/action` - Approve/reject gate

### Artifacts

- `GET /api/workflow/<workflow_id>/manifest` - Get manifest
- `GET /api/workflow/<workflow_id>/artifacts` - Get artifacts
- `POST /api/artifact/verify` - Verify artifact
- `POST /api/manifest/verify` - Verify manifest
- `GET /api/workflow/<workflow_id>/manifest/export` - Export manifest

## WebSocket Events

### Client → Server

- `join_workflow` - Join workflow room for updates
- `leave_workflow` - Leave workflow room
- `join_trust` - Subscribe to trust updates
- `leave_trust` - Unsubscribe from trust updates
- `join_pki` - Subscribe to PKI events
- `leave_pki` - Unsubscribe from PKI events

### Server → Client

- `workflow_update` - Workflow progress update
  - Types: `stage_started`, `stage_completed`, `stage_failed`, `breakpoint_requested`
- `trust_update` - Trust score changed
  - Type: `trust_score_updated`
- `agent_event` - Agent event occurred
  - Type: `agent_event`
- `pki_event` - Certificate event
  - Types: `certificate_expiring`, `certificate_revoked`, `certificate_renewed`

## Integration with Team Agent

The service layer (`app/services/`) bridges Flask API to existing Team Agent code:

- `mission_service.py` → `swarms.team_agent.orchestrator_a2a.OrchestratorA2A`
- `trust_service.py` → `swarms.team_agent.crypto.trust.AgentReputationTracker`
- `pki_service.py` → `swarms.team_agent.crypto.pki.PKIManager`, `CRLManager`
- `registry_service.py` → `swarms.team_agent.a2a.registry.CapabilityRegistry`
- `governance_service.py` → `swarms.team_agent.roles.governance.Governance`
- `artifacts_service.py` → `swarms.team_agent.crypto.manifest.ManifestGenerator`

## Phase 1 Status

✅ Flask app factory with blueprints
✅ REST API endpoints (all 6 blueprints)
✅ WebSocket handlers (workflow, trust, PKI)
✅ Service layer with TODOs for integration
✅ CORS configuration
✅ Health check endpoint

## Next Steps

- Implement service layer integration with existing Team Agent code
- Add authentication and authorization
- Add request validation with Marshmallow schemas
- Add rate limiting
- Add logging configuration
- Write unit tests for API endpoints
- Write integration tests for WebSocket handlers
