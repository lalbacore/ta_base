
"""
Optimization Service - Calculates multi-objective optimization scores for mission steps.

Equation: min_w F(w) where F(w) := sum_{i=1}^{K} nu_i F_i(w)
"""
from typing import Dict, Any, List

class OptimizationService:
    def __init__(self):
        # Default weights (nu_i)
        self.default_weights = {
            'time': 0.4,
            'cost': 0.4,
            'risk': 0.2
        }

    def calculate_step_optimization(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate optimization score F(w) for a given step.
        
        Args:
            step_data: Dictionary containing step metrics (time_taken, cost, etc.)
            
        Returns:
            Dictionary with optimization score and component breakdown.
        """
        # Extract metrics (F_i(w)) - normalizing to 0-1 scale approx for demo
        # Actual implementation would need real normalization based on historical data
        
        # Time (lower is better for minimization)
        # Assume 60 seconds is "max" for normalization (1.0)
        time_taken = float(step_data.get('time_taken', 0))
        f_time = min(time_taken / 60.0, 1.0)
        
        # Cost (lower is better)
        # Assume $1.00 is "max"
        cost = float(step_data.get('cost', 0))
        f_cost = min(cost / 1.0, 1.0)
        
        # Risk (lower is better, derived from confidence)
        # If confidence is high (1.0), risk is low (0.0)
        confidence = float(step_data.get('confidence', 1.0))
        f_risk = 1.0 - confidence
        
        # Calculate components (nu_i * F_i(w))
        w_time = self.default_weights['time']
        w_cost = self.default_weights['cost']
        w_risk = self.default_weights['risk']
        
        comp_time = w_time * f_time
        comp_cost = w_cost * f_cost
        comp_risk = w_risk * f_risk
        
        # Total F(w)
        f_total = comp_time + comp_cost + comp_risk
        
        return {
            'score': round(f_total, 4),
            'components': {
                'time': {
                    'value': f_time,
                    'weight': w_time,
                    'contribution': round(comp_time, 4)
                },
                'cost': {
                    'value': f_cost,
                    'weight': w_cost,
                    'contribution': round(comp_cost, 4)
                },
                'risk': {
                    'value': f_risk,
                    'weight': w_risk,
                    'contribution': round(comp_risk, 4)
                }
            },
            'equation_md': r"\min _{w}F(w) = " + f"{f_total:.4f}"
        }

optimization_service = OptimizationService()
