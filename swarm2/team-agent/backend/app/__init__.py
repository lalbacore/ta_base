"""
Team Agent Backend - Flask API and WebSocket server.
"""
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os

socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize SocketIO
    socketio.init_app(app)

    # Register blueprints
    from app.api.mission import mission_bp
    from app.api.trust import trust_bp
    from app.api.pki import pki_bp
    from app.api.registry import registry_bp
    from app.api.governance import governance_bp
    from app.api.artifacts import artifacts_bp
    from app.api.crypto_chain import crypto_chain_bp
    from app.api.logs import logs_bp
    from app.api.agents import agents_bp
    from app.api.well_known import well_known_bp
    from app.api.episodes import episodes_bp  # NEW

    app.register_blueprint(mission_bp, url_prefix='/api/mission')
    app.register_blueprint(trust_bp, url_prefix='/api/trust')
    app.register_blueprint(pki_bp, url_prefix='/api/pki')
    app.register_blueprint(registry_bp, url_prefix='/api/registry')
    app.register_blueprint(governance_bp, url_prefix='/api/governance')
    app.register_blueprint(artifacts_bp, url_prefix='/api')
    app.register_blueprint(crypto_chain_bp, url_prefix='/api/crypto-chain')
    app.register_blueprint(logs_bp, url_prefix='/api')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    app.register_blueprint(well_known_bp)  # No prefix - .well-known at root
    app.register_blueprint(episodes_bp)  # NEW - /api/episodes
    
    from app.api.provider import provider_bp
    app.register_blueprint(provider_bp, url_prefix='/api/provider')
    
    from swarms.team_agent.mcp.server import mcp_bp
    app.register_blueprint(mcp_bp)

    # Register WebSocket handlers
    from app.websocket import workflow_handler, trust_handler, pki_handler

    # Initialize database schema
    print("🔧 Initializing database...")
    from app.database import init_backend_db
    init_backend_db()
    print("✅ Database schema ready")

    # Load seed data on first run
    with app.app_context():
        from app.data.seed_loader import seed_database
        seed_database()

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'team-agent-backend'}

    return app
