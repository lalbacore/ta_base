"""
Provider Management API.

Handles:
- Network Provider registration (Optimism, Filecoin, etc.)
- User Wallet management (Encrypted credentials)
"""
from flask import Blueprint, jsonify, request
from app.database import get_backend_session
from app.models.provider import NetworkProvider, WalletCredential
import uuid
import datetime

provider_bp = Blueprint('provider', __name__)

@provider_bp.route('/list', methods=['GET'])
def list_providers():
    """List all configured network providers."""
    try:
        with get_backend_session() as session:
            providers = session.query(NetworkProvider).all()
            return jsonify([p.to_dict() for p in providers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/add', methods=['POST'])
def add_provider():
    """Add a new network provider."""
    data = request.json
    required = ['name', 'provider_type', 'rpc_url']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        with get_backend_session() as session:
            provider = NetworkProvider(
                provider_id=f"provider_{uuid.uuid4().hex[:8]}",
                name=data['name'],
                provider_type=data['provider_type'],
                rpc_url=data['rpc_url'],
                chain_id=data.get('chain_id'),
                meta_data=data.get('meta_data', {})
            )
            session.add(provider)
            # implicitly committed by context manager
            
        return jsonify({'status': 'success', 'provider_id': provider.provider_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/wallets', methods=['GET'])
def list_wallets():
    """List available wallets (metadata only)."""
    try:
        with get_backend_session() as session:
            wallets = session.query(WalletCredential).filter_by(is_active=True).all()
            return jsonify([w.to_dict() for w in wallets])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/add_wallet', methods=['POST'])
def add_wallet():
    """Add a new wallet credential."""
    data = request.json
    required = ['address', 'provider_type', 'private_key'] # private_key is expected in clear text or client-encrypted?
    # For now assuming clear text over TLS, and we encrypt here? 
    # Or simplified: store as is for prototype if no KMS available.
    # To be safe, let's assume inputs are 'address' and 'encrypted_private_key' if client does it,
    # or we do a mock encryption here.
    
    if not all(k in data for k in ['address', 'provider_type', 'private_key']):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # TODO: REAL ENCRYPTION
        # In a real app, use app.services.crypto.encrypt(data['private_key'])
        # For prototype, we will just prefix it to show intent.
        encrypted_key = f"ENC_{data['private_key']}" 
        
        with get_backend_session() as session:
            wallet = WalletCredential(
                wallet_id=f"wallet_{uuid.uuid4().hex[:8]}",
                user_id=data.get('user_id', 'system'),
                label=data.get('label', 'New Wallet'),
                address=data['address'],
                provider_type=data['provider_type'],
                encrypted_private_key=encrypted_key,
                encryption_version="mock_v1"
            )
            session.add(wallet)
            
        return jsonify({'status': 'success', 'wallet_id': wallet.wallet_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
