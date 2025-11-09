"""
Advanced Drift Monitoring for FairLens v3.0
Implements predictive drift detection with velocity, acceleration, and confidence intervals
"""

import numpy as np
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats

from config import Config

logger = logging.getLogger(__name__)

class DriftMonitor:
    """
    Advanced fairness drift monitoring with predictive capabilities
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Config.DATABASE_PATH
        self.db_path = db_path
    
    def get_recent_trends(self, metric_name: str = 'DIR', window_size: int = None) -> List[Dict[str, Any]]:
        """
        Get recent trend data for a specific metric
        
        Args:
            metric_name: Name of the metric (DIR, SPD, EOD, AOD, THEIL)
            window_size: Number of recent records to retrieve
        
        Returns:
            List of trend records with timestamps and values
        """
        if window_size is None:
            window_size = Config.DRIFT_WINDOW_SIZE
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query recent trend data
            cursor.execute("""
                SELECT timestamp, dir, created_at
                FROM fairness_trend
                ORDER BY created_at DESC
                LIMIT ?
            """, (window_size,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dictionaries (reverse to chronological order)
            trends = []
            for row in reversed(rows):
                trends.append({
                    'timestamp': row[0],
                    'value': row[1],
                    'created_at': row[2]
                })
            
            return trends
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            return []
    
    def calculate_velocity(self, trends: List[Dict[str, Any]]) -> float:
        """
        Calculate drift velocity (first derivative)
        
        Args:
            trends: List of trend data points
        
        Returns:
            Velocity value (rate of change)
        """
        if len(trends) < 2:
            return 0.0
        
        values = np.array([t['value'] for t in trends])
        
        # Calculate simple linear regression slope
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        return float(slope)
    
    def calculate_acceleration(self, trends: List[Dict[str, Any]]) -> float:
        """
        Calculate drift acceleration (second derivative)
        
        Args:
            trends: List of trend data points
        
        Returns:
            Acceleration value (rate of velocity change)
        """
        if len(trends) < 3:
            return 0.0
        
        values = np.array([t['value'] for t in trends])
        
        # Calculate velocities between consecutive points
        velocities = np.diff(values)
        
        # Acceleration is the change in velocity
        if len(velocities) < 2:
            return 0.0
        
        acceleration = np.mean(np.diff(velocities))
        
        return float(acceleration)
    
    def calculate_confidence_interval(self, trends: List[Dict[str, Any]], confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate confidence interval using bootstrapping
        
        Args:
            trends: List of trend data points
            confidence: Confidence level (default 0.95 for 95% CI)
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if len(trends) < 2:
            return (0.0, 0.0)
        
        values = np.array([t['value'] for t in trends])
        
        # Bootstrap confidence interval
        n_bootstrap = 1000
        bootstrap_means = []
        
        for _ in range(n_bootstrap):
            sample = np.random.choice(values, size=len(values), replace=True)
            bootstrap_means.append(np.mean(sample))
        
        # Calculate percentiles
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(bootstrap_means, lower_percentile)
        upper_bound = np.percentile(bootstrap_means, upper_percentile)
        
        return (float(lower_bound), float(upper_bound))
    
    def predict_future_drift(self, trends: List[Dict[str, Any]], horizon: int = 5) -> List[Dict[str, Any]]:
        """
        Predict future drift values using linear extrapolation
        
        Args:
            trends: Historical trend data
            horizon: Number of future periods to predict
        
        Returns:
            List of predicted values with timestamps
        """
        if len(trends) < 3:
            return []
        
        values = np.array([t['value'] for t in trends])
        x = np.arange(len(values))
        
        # Fit linear model
        slope, intercept = np.polyfit(x, values, 1)
        
        # Predict future values
        predictions = []
        for i in range(1, horizon + 1):
            future_x = len(values) + i
            predicted_value = slope * future_x + intercept
            
            predictions.append({
                'period': i,
                'predicted_value': float(predicted_value),
                'confidence': self._calculate_prediction_confidence(trends, i)
            })
        
        return predictions
    
    def _calculate_prediction_confidence(self, trends: List[Dict[str, Any]], periods_ahead: int) -> float:
        """
        Calculate confidence in prediction (decreases with distance)
        
        Args:
            trends: Historical trend data
            periods_ahead: How many periods into the future
        
        Returns:
            Confidence score (0-1)
        """
        if len(trends) < 2:
            return 0.0
        
        # Confidence decreases exponentially with distance
        base_confidence = min(len(trends) / 20, 1.0)  # More data = more confidence
        decay_factor = 0.15  # Confidence decay per period
        
        confidence = base_confidence * np.exp(-decay_factor * periods_ahead)
        
        return float(max(0.1, min(confidence, 1.0)))  # Clamp between 0.1 and 1.0
    
    def calculate_risk_score(self, 
                            velocity: float, 
                            acceleration: float, 
                            current_value: float,
                            threshold: float = 0.8) -> Dict[str, Any]:
        """
        Calculate probabilistic risk score for bias drift
        
        Args:
            velocity: Drift velocity
            acceleration: Drift acceleration
            current_value: Current metric value
            threshold: Fairness threshold (default 0.8 for DIR)
        
        Returns:
            Risk assessment dictionary
        """
        # Risk factors
        distance_to_threshold = current_value - threshold
        velocity_risk = abs(velocity) if velocity < 0 else 0
        acceleration_risk = abs(acceleration) if acceleration < 0 else 0
        
        # Weighted risk score (0-1)
        risk_score = (
            0.4 * (1 - max(0, distance_to_threshold) / 0.2) +  # Proximity to threshold
            0.35 * min(velocity_risk * 10, 1) +  # Velocity contribution
            0.25 * min(acceleration_risk * 20, 1)  # Acceleration contribution
        )
        
        risk_score = max(0, min(risk_score, 1))
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = 'HIGH'
            severity = 'critical'
        elif risk_score >= 0.4:
            risk_level = 'MEDIUM'
            severity = 'medium'
        else:
            risk_level = 'LOW'
            severity = 'low'
        
        # Determine if retraining is needed
        needs_retraining = (
            (velocity < Config.DRIFT_VELOCITY_THRESHOLD) or
            (acceleration < Config.DRIFT_ACCELERATION_THRESHOLD) or
            (current_value < threshold)
        )
        
        return {
            'risk_score': float(risk_score),
            'risk_level': risk_level,
            'severity': severity,
            'needs_retraining': needs_retraining,
            'factors': {
                'distance_to_threshold': float(distance_to_threshold),
                'velocity_risk': float(velocity_risk),
                'acceleration_risk': float(acceleration_risk)
            },
            'recommendation': self._get_recommendation(risk_level, needs_retraining)
        }
    
    def _get_recommendation(self, risk_level: str, needs_retraining: bool) -> str:
        """Generate risk-based recommendation"""
        if risk_level == 'HIGH':
            if needs_retraining:
                return "🚨 CRITICAL: Immediate model retraining required. Bias drift is accelerating rapidly."
            return "⚠️ HIGH RISK: Monitor closely. Consider retraining if trend continues."
        elif risk_level == 'MEDIUM':
            if needs_retraining:
                return "⚠️ WARNING: Model retraining recommended within 48 hours to prevent bias escalation."
            return "⚠️ MEDIUM RISK: Increase monitoring frequency. Review feature distributions."
        else:
            return "✅ LOW RISK: System operating within acceptable fairness parameters."
    
    def generate_drift_report(self, metric_name: str = 'DIR') -> Dict[str, Any]:
        """
        Generate comprehensive drift analysis report
        
        Args:
            metric_name: Metric to analyze
        
        Returns:
            Complete drift analysis report
        """
        trends = self.get_recent_trends(metric_name, Config.DRIFT_WINDOW_SIZE)
        
        if len(trends) < 2:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': 'Not enough historical data for drift analysis',
                'trends_count': len(trends)
            }
        
        current_value = trends[-1]['value'] if trends else 0
        velocity = self.calculate_velocity(trends)
        acceleration = self.calculate_acceleration(trends)
        ci_lower, ci_upper = self.calculate_confidence_interval(trends)
        predictions = self.predict_future_drift(trends, horizon=5)
        risk_assessment = self.calculate_risk_score(velocity, acceleration, current_value)
        
        return {
            'metric_name': metric_name,
            'current_value': float(current_value),
            'velocity': float(velocity),
            'acceleration': float(acceleration),
            'confidence_interval': {
                'lower': float(ci_lower),
                'upper': float(ci_upper),
                'confidence_level': 0.95
            },
            'predictions': predictions,
            'risk_assessment': risk_assessment,
            'trend_data': trends,
            'analysis_timestamp': datetime.now().isoformat(),
            'is_accelerating': acceleration < Config.DRIFT_ACCELERATION_THRESHOLD,
            'is_degrading': velocity < Config.DRIFT_VELOCITY_THRESHOLD
        }
