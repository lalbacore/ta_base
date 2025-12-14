"""
Drift Detection Service - Monitor episode metrics for behavioral changes

Detects:
- Token consumption drift
- Effectiveness score degradation  
- Token efficiency changes
"""

import numpy as np
from scipy.stats import ks_2samp
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DriftService:
    """Service for detecting drift in episode metrics."""
    
    def __init__(self):
        self.baseline_window = 100  # Episodes for baseline
        self.detection_window = 30   # Recent episodes to check
        self.drift_threshold = 0.05  # P-value threshold
    
    def detect_token_drift(self) -> Dict:
        """
        Detect drift in token consumption patterns.
        
        Returns:
            Dictionary with drift detection results
        """
        try:
            from app.services.episode_service import episode_service
            
            episodes = episode_service.list_episodes(limit=200)
            
            if len(episodes) < self.baseline_window + self.detection_window:
                return {
                    'status': 'insufficient_data',
                    'drift_detected': False,
                    'message': f'Need at least {self.baseline_window + self.detection_window} episodes'
                }
            
            # Split baseline vs current
            baseline = episodes[self.detection_window:][:self.baseline_window]
            current = episodes[:self.detection_window]
            
            # Extract token metrics (filter out zeros)
            baseline_tokens = [
                e.total_tokens_consumed 
                for e in baseline 
                if e.total_tokens_consumed > 0
            ]
            current_tokens = [
                e.total_tokens_consumed 
                for e in current 
                if e.total_tokens_consumed > 0
            ]
            
            if not baseline_tokens or not current_tokens:
                return {
                    'status': 'insufficient_data',
                    'drift_detected': False,
                    'message': 'No token data available'
                }
            
            # Kolmogorov-Smirnov test
            statistic, p_value = ks_2samp(baseline_tokens, current_tokens)
            drift_detected = p_value < self.drift_threshold
            
            baseline_mean = float(np.mean(baseline_tokens))
            current_mean = float(np.mean(current_tokens))
            change_percent = ((current_mean - baseline_mean) / baseline_mean * 100)
            
            return {
                'metric': 'token_consumption',
                'drift_detected': drift_detected,
                'p_value': float(p_value),
                'statistic': float(statistic),
                'baseline_mean': baseline_mean,
                'current_mean': current_mean,
                'change_percent': change_percent,
                'severity': self._get_severity(p_value, abs(change_percent)),
                'samples': {
                    'baseline': len(baseline_tokens),
                    'current': len(current_tokens)
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting token drift: {e}")
            return {'status': 'error', 'error': str(e), 'drift_detected': False}
    
    def detect_effectiveness_drift(self) -> Dict:
        """
        Detect drift in effectiveness scores.
        
        Returns:
            Dictionary with drift detection results
        """
        try:
            from app.services.episode_service import episode_service
            
            episodes = episode_service.list_episodes(limit=200)
            
            if len(episodes) < self.baseline_window + self.detection_window:
                return {
                    'status': 'insufficient_data',
                    'drift_detected': False
                }
            
            baseline = episodes[self.detection_window:][:self.baseline_window]
            current = episodes[:self.detection_window]
            
            baseline_scores = [e.effectiveness_score for e in baseline]
            current_scores = [e.effectiveness_score for e in current]
            
            # KS test
            statistic, p_value = ks_2samp(baseline_scores, current_scores)
            drift_detected = p_value < self.drift_threshold
            
            baseline_mean = float(np.mean(baseline_scores))
            current_mean = float(np.mean(current_scores))
            degradation = baseline_mean - current_mean
            
            return {
                'metric': 'effectiveness_score',
                'drift_detected': drift_detected,
                'p_value': float(p_value),
                'statistic': float(statistic),
                'baseline_mean': baseline_mean,
                'current_mean': current_mean,
                'degradation': degradation,
                'severity': self._get_effectiveness_severity(degradation, p_value),
                'samples': {
                    'baseline': len(baseline_scores),
                    'current': len(current_scores)
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting effectiveness drift: {e}")
            return {'status': 'error', 'error': str(e), 'drift_detected': False}
    
    def detect_efficiency_drift(self) -> Dict:
        """
        Detect drift in token efficiency (tokens per artifact).
        
        Returns:
            Dictionary with drift detection results
        """
        try:
            from app.services.episode_service import episode_service
            
            episodes = episode_service.list_episodes(limit=200)
            
            if len(episodes) < self.baseline_window + self.detection_window:
                return {
                    'status': 'insufficient_data',
                    'drift_detected': False
                }
            
            baseline = episodes[self.detection_window:][:self.baseline_window]
            current = episodes[:self.detection_window]
            
            # Calculate efficiency (tokens per artifact)
            baseline_eff = [
                e.total_tokens_consumed / len(e.artifacts)
                for e in baseline
                if len(e.artifacts) > 0 and e.total_tokens_consumed > 0
            ]
            current_eff = [
                e.total_tokens_consumed / len(e.artifacts)
                for e in current
                if len(e.artifacts) > 0 and e.total_tokens_consumed > 0
            ]
            
            if not baseline_eff or not current_eff:
                return {
                    'status': 'insufficient_data',
                    'drift_detected': False
                }
            
            # KS test
            statistic, p_value = ks_2samp(baseline_eff, current_eff)
            drift_detected = p_value < self.drift_threshold
            
            baseline_mean = float(np.mean(baseline_eff))
            current_mean = float(np.mean(current_eff))
            efficiency_change = ((current_mean - baseline_mean) / baseline_mean * 100)
            
            return {
                'metric': 'token_efficiency',
                'drift_detected': drift_detected,
                'p_value': float(p_value),
                'baseline_mean': baseline_mean,
                'current_mean': current_mean,
                'efficiency_change_percent': efficiency_change,
                'severity': self._get_severity(p_value, abs(efficiency_change)),
                'samples': {
                    'baseline': len(baseline_eff),
                    'current': len(current_eff)
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting efficiency drift: {e}")
            return {'status': 'error', 'error': str(e), 'drift_detected': False}
    
    def get_drift_report(self) -> Dict:
        """
        Generate comprehensive drift report.
        
        Returns:
            Complete drift analysis with recommendations
        """
        token_drift = self.detect_token_drift()
        effectiveness_drift = self.detect_effectiveness_drift()
        efficiency_drift = self.detect_efficiency_drift()
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            token_drift,
            effectiveness_drift,
            efficiency_drift
        )
        
        # Determine overall alert level
        alert_level = self._get_alert_level(
            token_drift,
            effectiveness_drift,
            efficiency_drift
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'token_drift': token_drift,
            'effectiveness_drift': effectiveness_drift,
            'efficiency_drift': efficiency_drift,
            'recommendation': recommendation,
            'alert_level': alert_level
        }
    
    def _get_severity(self, p_value: float, magnitude: float) -> str:
        """Determine severity based on p-value and magnitude."""
        if p_value >= self.drift_threshold:
            return 'none'
        elif p_value < 0.01 and magnitude > 30:
            return 'critical'
        elif p_value < 0.01 or magnitude > 20:
            return 'high'
        else:
            return 'medium'
    
    def _get_effectiveness_severity(self, degradation: float, p_value: float) -> str:
        """Determine severity for effectiveness drift."""
        if p_value >= self.drift_threshold:
            return 'none'
        elif degradation > 15:
            return 'critical'
        elif degradation > 10:
            return 'high'
        elif degradation > 5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendation(
        self,
        token_drift: Dict,
        effectiveness_drift: Dict,
        efficiency_drift: Dict
    ) -> str:
        """Generate actionable recommendation based on drift."""
        issues = []
        
        if token_drift.get('drift_detected'):
            change = token_drift.get('change_percent', 0)
            issues.append(f"token consumption changed by {change:.1f}%")
        
        if effectiveness_drift.get('drift_detected'):
            deg = effectiveness_drift.get('degradation', 0)
            issues.append(f"effectiveness degraded by {deg:.1f} points")
        
        if efficiency_drift.get('drift_detected'):
            change = efficiency_drift.get('efficiency_change_percent', 0)
            issues.append(f"token efficiency changed by {change:.1f}%")
        
        if not issues:
            return "OK: No significant drift detected."
        
        if len(issues) >= 2:
            return f"CRITICAL: Multiple drift signals detected - {', '.join(issues)}. Investigate immediately."
        else:
            return f"WARNING: Drift detected - {issues[0]}. Monitor closely."
    
    def _get_alert_level(
        self,
        token_drift: Dict,
        effectiveness_drift: Dict,
        efficiency_drift: Dict
    ) -> str:
        """Determine overall alert level."""
        severities = [
            token_drift.get('severity', 'none'),
            effectiveness_drift.get('severity', 'none'),
            efficiency_drift.get('severity', 'none')
        ]
        
        if 'critical' in severities:
            return 'critical'
        elif 'high' in severities:
            return 'high'
        elif 'medium' in severities:
            return 'medium'
        else:
            return 'none'


# Singleton instance
drift_service = DriftService()
