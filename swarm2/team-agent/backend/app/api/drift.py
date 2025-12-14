"""
Drift Detection API - Endpoints for monitoring system drift
"""

from flask import Blueprint, jsonify
from app.services.drift_service import drift_service
import logging

logger = logging.getLogger(__name__)

drift_bp = Blueprint('drift', __name__, url_prefix='/api/drift')


@drift_bp.route('/report', methods=['GET'])
def get_drift_report():
    """
    Get comprehensive drift detection report.
    
    Returns:
        {
            "timestamp": "2025-12-14T...",
            "token_drift": {...},
            "effectiveness_drift": {...},
            "efficiency_drift": {...},
            "recommendation": "...",
            "alert_level": "none|medium|high|critical"
        }
    """
    try:
        report = drift_service.get_drift_report()
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Error generating drift report: {e}")
        return jsonify({'error': str(e)}), 500


@drift_bp.route('/token', methods=['GET'])
def get_token_drift():
    """
    Get token consumption drift analysis.
    
    Returns:
        {
            "drift_detected": bool,
            "baseline_mean": float,
            "current_mean": float,
            "change_percent": float,
            "severity": "none|medium|high|critical"
        }
    """
    try:
        drift = drift_service.detect_token_drift()
        return jsonify(drift), 200
    except Exception as e:
        logger.error(f"Error detecting token drift: {e}")
        return jsonify({'error': str(e)}), 500


@drift_bp.route('/effectiveness', methods=['GET'])
def get_effectiveness_drift():
    """
    Get effectiveness score drift analysis.
    
    Returns:
        {
            "drift_detected": bool,
            "baseline_mean": float,
            "current_mean": float,
            "degradation": float,
            "severity": "none|low|medium|high|critical"
        }
    """
    try:
        drift = drift_service.detect_effectiveness_drift()
        return jsonify(drift), 200
    except Exception as e:
        logger.error(f"Error detecting effectiveness drift: {e}")
        return jsonify({'error': str(e)}), 500


@drift_bp.route('/efficiency', methods=['GET'])
def get_efficiency_drift():
    """
    Get token efficiency drift analysis.
    
    Returns:
        {
            "drift_detected": bool,
            "baseline_mean": float,
            "current_mean": float,
            "efficiency_change_percent": float,
            "severity": "none|medium|high|critical"
        }
    """
    try:
        drift = drift_service.detect_efficiency_drift()
        return jsonify(drift), 200
    except Exception as e:
        logger.error(f"Error detecting efficiency drift: {e}")
        return jsonify({'error': str(e)}), 500
