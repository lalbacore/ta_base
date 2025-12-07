"""
Flask application entry point.
"""
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    socketio.run(app, host='0.0.0.0', port=5002, debug=debug_mode, allow_unsafe_werkzeug=True)
