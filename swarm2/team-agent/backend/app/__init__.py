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

    app.register_blueprint(mission_bp, url_prefix='/api/mission')
    app.register_blueprint(trust_bp, url_prefix='/api/trust')
    app.register_blueprint(pki_bp, url_prefix='/api/pki')
    app.register_blueprint(registry_bp, url_prefix='/api/registry')
    app.register_blueprint(governance_bp, url_prefix='/api/governance')
    app.register_blueprint(artifacts_bp, url_prefix='/api')

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
