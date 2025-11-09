"""
Enhanced Explainability Module for FairLens v3.0
Advanced feature attribution and AI-assisted remediation suggestions
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import sqlite3

from config import Config

logger = logging.getLogger(__name__)

class EnhancedExplainer:
    """
    Advanced explainability system with feature attribution and remediation suggestions
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Config.DATABASE_PATH
        self.db_path = db_path
    
    def analyze_feature_contributions(self,
                                     data: pd.DataFrame,
                                     predictions: np.ndarray,
                                     protected_attribute: np.ndarray,
                                     feature_importance: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze how features contribute to fairness (or bias)
        
        Args:
            data: Feature dataframe
            predictions: Model predictions
            protected_attribute: Protected attribute values
            feature_importance: Model feature importance scores
        
        Returns:
            Detailed feature contribution analysis
        """
        privileged_mask = protected_attribute == 0
        protected_mask = protected_attribute == 1
        
        feature_analysis = {}
        
        for feature in data.columns:
            # Calculate feature statistics for each group
            privileged_mean = data.loc[privileged_mask, feature].mean()
            protected_mean = data.loc[protected_mask, feature].mean()
            privileged_median = data.loc[privileged_mask, feature].median()
            protected_median = data.loc[protected_mask, feature].median()
            
            # Calculate differences
            mean_diff = protected_mean - privileged_mean
            median_diff = protected_median - privileged_median
            
            # Normalize difference by standard deviation
            overall_std = data[feature].std()
            normalized_diff = mean_diff / overall_std if overall_std > 0 else 0
            
            # Get feature importance
            importance = feature_importance.get(feature, 0)
            
            # Calculate contribution score (importance * difference)
            contribution_score = abs(normalized_diff) * importance
            
            feature_analysis[feature] = {
                'privileged_mean': float(privileged_mean),
                'protected_mean': float(protected_mean),
                'mean_difference': float(mean_diff),
                'median_difference': float(median_diff),
                'normalized_difference': float(normalized_diff),
                'feature_importance': float(importance),
                'contribution_score': float(contribution_score),
                'direction': 'protected_higher' if mean_diff > 0 else 'privileged_higher'
            }
        
        # Rank features by contribution
        ranked_features = sorted(
            feature_analysis.items(),
            key=lambda x: x[1]['contribution_score'],
            reverse=True
        )
        
        return {
            'feature_contributions': dict(ranked_features),
            'top_contributors': [
                {
                    'feature': f,
                    'score': data['contribution_score'],
                    'difference': data['mean_difference'],
                    'importance': data['feature_importance']
                }
                for f, data in ranked_features[:3]
            ]
        }
    
    def get_temporal_attribution(self, window_size: int = 10) -> List[Dict[str, Any]]:
        """
        Analyze feature attribution over time
        
        Args:
            window_size: Number of recent records to analyze
        
        Returns:
            List of temporal attribution records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # In a production system, this would query a temporal feature store
            # For now, we'll return a structured format
            temporal_data = []
            
            cursor.execute("""
                SELECT timestamp, created_at
                FROM fairness_trend
                ORDER BY created_at DESC
                LIMIT ?
            """, (window_size,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Placeholder for temporal attribution
            # In production, this would include feature contribution trends
            for row in rows:
                temporal_data.append({
                    'timestamp': row[0],
                    'created_at': row[1],
                    'note': 'Full temporal attribution requires feature history tracking'
                })
            
            return temporal_data
        except Exception as e:
            logger.error(f"Error fetching temporal attribution: {e}")
            return []
    
    def generate_remediation_suggestions(self,
                                        feature_contributions: Dict[str, Any],
                                        current_dir: float,
                                        velocity: float,
                                        risk_level: str) -> List[Dict[str, str]]:
        """
        Generate AI-assisted remediation suggestions based on bias patterns
        
        Args:
            feature_contributions: Feature contribution analysis
            current_dir: Current DIR value
            velocity: Drift velocity
            risk_level: Risk level (HIGH, MEDIUM, LOW)
        
        Returns:
            List of actionable remediation suggestions
        """
        suggestions = []
        
        top_contributors = feature_contributions.get('top_contributors', [])
        
        # Priority 1: Critical risk - immediate action
        if risk_level == 'HIGH' or current_dir < 0.75:
            suggestions.append({
                'priority': 'CRITICAL',
                'category': 'Model Retraining',
                'suggestion': '🚨 Immediate model retraining required. DIR is critically low or deteriorating rapidly.',
                'action': 'Retrain model with balanced sampling or apply bias mitigation techniques (reweighting, resampling).',
                'expected_impact': 'HIGH'
            })
        
        # Priority 2: Feature-based interventions
        if top_contributors:
            top_feature = top_contributors[0]
            feature_name = top_feature['feature']
            mean_diff = top_feature['difference']
            
            if abs(mean_diff) > 0:
                direction = "higher" if mean_diff > 0 else "lower"
                suggestions.append({
                    'priority': 'HIGH',
                    'category': 'Feature Engineering',
                    'suggestion': f'⚠️ {feature_name.replace("_", " ").title()} shows significant group disparity ({direction} for protected group by {abs(mean_diff):.1f}).',
                    'action': f'Consider feature normalization, adding interaction terms, or investigating data collection bias for {feature_name}.',
                    'expected_impact': 'MEDIUM-HIGH'
                })
        
        # Priority 3: Velocity-based preventive measures
        if velocity < -0.01:
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'Preventive Monitoring',
                'suggestion': f'📉 Fairness is degrading at {abs(velocity):.4f} per period. Trend is concerning.',
                'action': 'Increase monitoring frequency to daily. Set up automated alerts. Review recent data pipeline changes.',
                'expected_impact': 'MEDIUM'
            })
        
        # Priority 4: Data quality checks
        if len(top_contributors) >= 2:
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'Data Quality',
                'suggestion': '🔍 Multiple features show group disparities. This may indicate systematic data collection bias.',
                'action': 'Audit data collection process. Check for sampling bias. Ensure balanced representation in training data.',
                'expected_impact': 'MEDIUM'
            })
        
        # Priority 5: Algorithmic fairness techniques
        if current_dir < 0.8 and current_dir >= 0.75:
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'Bias Mitigation',
                'suggestion': '⚖️ DIR is below threshold but not critical. Apply fairness constraints.',
                'action': 'Implement algorithmic fairness techniques: adversarial debiasing, fairness constraints in loss function, or post-processing calibration.',
                'expected_impact': 'MEDIUM-HIGH'
            })
        
        # Priority 6: Positive reinforcement
        if risk_level == 'LOW' and current_dir >= 0.9:
            suggestions.append({
                'priority': 'LOW',
                'category': 'Best Practices',
                'suggestion': '✅ Model is performing well on fairness metrics. Continue current practices.',
                'action': 'Document successful approaches. Maintain current monitoring schedule. Consider gradual feature improvements.',
                'expected_impact': 'LOW'
            })
        
        return suggestions
    
    def generate_confidence_scores(self,
                                   feature_contributions: Dict[str, Any],
                                   sample_size: int) -> Dict[str, float]:
        """
        Calculate confidence scores for feature attributions
        
        Args:
            feature_contributions: Feature contribution data
            sample_size: Number of samples in analysis
        
        Returns:
            Confidence scores for each attribution
        """
        # Confidence based on sample size and contribution magnitude
        base_confidence = min(sample_size / 1000, 1.0)  # More samples = more confidence
        
        confidence_scores = {}
        
        for feature, data in feature_contributions.get('feature_contributions', {}).items():
            contribution = data.get('contribution_score', 0)
            
            # Higher contribution = higher confidence in attribution
            magnitude_factor = min(contribution / 0.5, 1.0)
            
            confidence = base_confidence * (0.5 + 0.5 * magnitude_factor)
            confidence_scores[feature] = float(max(0.3, min(confidence, 1.0)))
        
        return confidence_scores
    
    def explain_bias_pattern(self,
                            feature_contributions: Dict[str, Any],
                            metrics_summary: Dict[str, Any]) -> str:
        """
        Generate natural language explanation of detected bias patterns
        
        Args:
            feature_contributions: Feature contribution analysis
            metrics_summary: Summary of all fairness metrics
        
        Returns:
            Natural language explanation
        """
        top_contributors = feature_contributions.get('top_contributors', [])
        
        if not top_contributors:
            return "Insufficient data for bias pattern analysis."
        
        top_feature = top_contributors[0]
        feature_name = top_feature['feature'].replace('_', ' ').title()
        mean_diff = top_feature['difference']
        direction = "higher" if mean_diff > 0 else "lower"
        
        explanation_parts = []
        
        # Primary cause
        explanation_parts.append(
            f"The primary driver of bias is **{feature_name}**, "
            f"which is {abs(mean_diff):.1f} units {direction} for the protected group. "
        )
        
        # Secondary factors
        if len(top_contributors) > 1:
            second_feature = top_contributors[1]['feature'].replace('_', ' ').title()
            explanation_parts.append(
                f"Secondary contributing factor: **{second_feature}**, "
                f"showing {abs(top_contributors[1]['difference']):.1f} unit difference. "
            )
        
        # Metrics summary
        passed = metrics_summary.get('passed', 0)
        total = metrics_summary.get('total_metrics', 5)
        
        explanation_parts.append(
            f"\n\nOverall fairness assessment: **{passed}/{total} metrics passed**. "
        )
        
        if passed < total:
            failed_metrics = total - passed
            explanation_parts.append(
                f"{failed_metrics} metric{'s' if failed_metrics > 1 else ''} "
                f"indicate{'s' if failed_metrics == 1 else ''} potential discrimination. "
            )
        
        return ''.join(explanation_parts)
