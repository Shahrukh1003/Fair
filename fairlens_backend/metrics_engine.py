"""
Multi-Metric Fairness Engine for BiasCheck v3.0
Implements comprehensive fairness metrics beyond DIR
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Tuple
from abc import ABC, abstractmethod

from config import Config

logger = logging.getLogger(__name__)

class FairnessMetric(ABC):
    """Base class for fairness metrics"""
    
    @abstractmethod
    def calculate(self, 
                  y_true: np.ndarray, 
                  y_pred: np.ndarray, 
                  protected_attribute: np.ndarray) -> Dict[str, Any]:
        """
        Calculate the fairness metric
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            protected_attribute: Protected attribute (e.g., gender)
        
        Returns:
            Dictionary with metric value, status, and details
        """
        pass
    
    @abstractmethod
    def get_threshold(self) -> float:
        """Get the fairness threshold for this metric"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the metric name"""
        pass
    
    def is_fair(self, value: float) -> bool:
        """Determine if metric value indicates fairness"""
        pass

class DisparateImpactRatio(FairnessMetric):
    """
    Disparate Impact Ratio (DIR)
    Formula: P(approved | protected) / P(approved | privileged)
    Threshold: >= 0.8 (EEOC 80% rule)
    """
    
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attribute: np.ndarray) -> Dict[str, Any]:
        # Get unique groups (assume binary: 0=privileged, 1=protected)
        privileged_mask = protected_attribute == 0
        protected_mask = protected_attribute == 1
        
        # Calculate approval rates
        privileged_approval_rate = y_pred[privileged_mask].mean() if privileged_mask.sum() > 0 else 0
        protected_approval_rate = y_pred[protected_mask].mean() if protected_mask.sum() > 0 else 0
        
        # Calculate DIR
        dir_value = protected_approval_rate / privileged_approval_rate if privileged_approval_rate > 0 else 0
        
        threshold = self.get_threshold()
        is_fair = dir_value >= threshold
        
        return {
            'name': self.get_name(),
            'value': float(dir_value),
            'threshold': threshold,
            'is_fair': bool(is_fair),
            'status': 'PASS' if is_fair else 'FAIL',
            'privileged_rate': float(privileged_approval_rate),
            'protected_rate': float(protected_approval_rate),
            'gap': float(abs(privileged_approval_rate - protected_approval_rate))
        }
    
    def get_threshold(self) -> float:
        return Config.DIR_THRESHOLD
    
    def get_name(self) -> str:
        return "Disparate Impact Ratio (DIR)"
    
    def is_fair(self, value: float) -> bool:
        return value >= self.get_threshold()

class StatisticalParityDifference(FairnessMetric):
    """
    Statistical Parity Difference (SPD)
    Formula: P(approved | protected) - P(approved | privileged)
    Threshold: abs(SPD) <= 0.1 (10% difference)
    """
    
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attribute: np.ndarray) -> Dict[str, Any]:
        privileged_mask = protected_attribute == 0
        protected_mask = protected_attribute == 1
        
        privileged_approval_rate = y_pred[privileged_mask].mean() if privileged_mask.sum() > 0 else 0
        protected_approval_rate = y_pred[protected_mask].mean() if protected_mask.sum() > 0 else 0
        
        spd_value = protected_approval_rate - privileged_approval_rate
        
        threshold = self.get_threshold()
        is_fair = abs(spd_value) <= threshold
        
        return {
            'name': self.get_name(),
            'value': float(spd_value),
            'threshold': threshold,
            'is_fair': bool(is_fair),
            'status': 'PASS' if is_fair else 'FAIL',
            'privileged_rate': float(privileged_approval_rate),
            'protected_rate': float(protected_approval_rate),
            'absolute_difference': float(abs(spd_value))
        }
    
    def get_threshold(self) -> float:
        return Config.SPD_THRESHOLD
    
    def get_name(self) -> str:
        return "Statistical Parity Difference (SPD)"
    
    def is_fair(self, value: float) -> bool:
        return abs(value) <= self.get_threshold()

class EqualOpportunityDifference(FairnessMetric):
    """
    Equal Opportunity Difference (EOD)
    Formula: TPR(protected) - TPR(privileged)
    TPR = True Positive Rate = TP / (TP + FN)
    Threshold: abs(EOD) <= 0.1
    """
    
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attribute: np.ndarray) -> Dict[str, Any]:
        privileged_mask = protected_attribute == 0
        protected_mask = protected_attribute == 1
        
        # Calculate TPR for each group (only among truly qualified applicants)
        def calculate_tpr(mask):
            y_true_group = y_true[mask]
            y_pred_group = y_pred[mask]
            
            # True positives among positive examples
            positive_mask = y_true_group == 1
            if positive_mask.sum() == 0:
                return 0
            
            tp = ((y_true_group == 1) & (y_pred_group == 1)).sum()
            tpr = tp / positive_mask.sum()
            return tpr
        
        privileged_tpr = calculate_tpr(privileged_mask)
        protected_tpr = calculate_tpr(protected_mask)
        
        eod_value = protected_tpr - privileged_tpr
        
        threshold = self.get_threshold()
        is_fair = abs(eod_value) <= threshold
        
        return {
            'name': self.get_name(),
            'value': float(eod_value),
            'threshold': threshold,
            'is_fair': bool(is_fair),
            'status': 'PASS' if is_fair else 'FAIL',
            'privileged_tpr': float(privileged_tpr),
            'protected_tpr': float(protected_tpr),
            'absolute_difference': float(abs(eod_value))
        }
    
    def get_threshold(self) -> float:
        return Config.EOD_THRESHOLD
    
    def get_name(self) -> str:
        return "Equal Opportunity Difference (EOD)"
    
    def is_fair(self, value: float) -> bool:
        return abs(value) <= self.get_threshold()

class AverageOddsDifference(FairnessMetric):
    """
    Average Odds Difference (AOD)
    Formula: 0.5 * [(TPR_protected - TPR_privileged) + (FPR_protected - FPR_privileged)]
    Threshold: abs(AOD) <= 0.1
    """
    
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attribute: np.ndarray) -> Dict[str, Any]:
        privileged_mask = protected_attribute == 0
        protected_mask = protected_attribute == 1
        
        def calculate_rates(mask):
            y_true_group = y_true[mask]
            y_pred_group = y_pred[mask]
            
            # TPR
            positive_mask = y_true_group == 1
            if positive_mask.sum() > 0:
                tp = ((y_true_group == 1) & (y_pred_group == 1)).sum()
                tpr = tp / positive_mask.sum()
            else:
                tpr = 0
            
            # FPR
            negative_mask = y_true_group == 0
            if negative_mask.sum() > 0:
                fp = ((y_true_group == 0) & (y_pred_group == 1)).sum()
                fpr = fp / negative_mask.sum()
            else:
                fpr = 0
            
            return tpr, fpr
        
        privileged_tpr, privileged_fpr = calculate_rates(privileged_mask)
        protected_tpr, protected_fpr = calculate_rates(protected_mask)
        
        tpr_diff = protected_tpr - privileged_tpr
        fpr_diff = protected_fpr - privileged_fpr
        
        aod_value = 0.5 * (tpr_diff + fpr_diff)
        
        threshold = self.get_threshold()
        is_fair = abs(aod_value) <= threshold
        
        return {
            'name': self.get_name(),
            'value': float(aod_value),
            'threshold': threshold,
            'is_fair': bool(is_fair),
            'status': 'PASS' if is_fair else 'FAIL',
            'privileged_tpr': float(privileged_tpr),
            'protected_tpr': float(protected_tpr),
            'privileged_fpr': float(privileged_fpr),
            'protected_fpr': float(protected_fpr),
            'tpr_difference': float(tpr_diff),
            'fpr_difference': float(fpr_diff)
        }
    
    def get_threshold(self) -> float:
        return Config.AOD_THRESHOLD
    
    def get_name(self) -> str:
        return "Average Odds Difference (AOD)"
    
    def is_fair(self, value: float) -> bool:
        return abs(value) <= self.get_threshold()

class TheilIndex(FairnessMetric):
    """
    Theil Index (Entropy-based fairness inequality)
    Formula: Generalized entropy index measuring outcome inequality
    Threshold: <= 0.15
    """
    
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attribute: np.ndarray) -> Dict[str, Any]:
        privileged_mask = protected_attribute == 0
        protected_mask = protected_attribute == 1
        
        # Calculate approval rates
        privileged_rate = y_pred[privileged_mask].mean() if privileged_mask.sum() > 0 else 0
        protected_rate = y_pred[protected_mask].mean() if protected_mask.sum() > 0 else 0
        
        overall_rate = y_pred.mean()
        
        # Theil index calculation (simplified version)
        if overall_rate == 0 or overall_rate == 1:
            theil_value = 0
        else:
            privileged_prop = privileged_mask.sum() / len(protected_attribute)
            protected_prop = protected_mask.sum() / len(protected_attribute)
            
            # Calculate contribution from each group
            def theil_contrib(rate, prop):
                if rate == 0 or prop == 0:
                    return 0
                return prop * (rate / overall_rate) * np.log(rate / overall_rate)
            
            theil_value = (theil_contrib(privileged_rate, privileged_prop) + 
                          theil_contrib(protected_rate, protected_prop))
        
        threshold = self.get_threshold()
        is_fair = theil_value <= threshold
        
        return {
            'name': self.get_name(),
            'value': float(theil_value),
            'threshold': threshold,
            'is_fair': bool(is_fair),
            'status': 'PASS' if is_fair else 'FAIL',
            'privileged_rate': float(privileged_rate),
            'protected_rate': float(protected_rate),
            'overall_rate': float(overall_rate),
            'inequality_level': 'LOW' if theil_value < 0.05 else 'MEDIUM' if theil_value < 0.1 else 'HIGH'
        }
    
    def get_threshold(self) -> float:
        return Config.THEIL_THRESHOLD
    
    def get_name(self) -> str:
        return "Theil Index"
    
    def is_fair(self, value: float) -> bool:
        return value <= self.get_threshold()

class MetricsEngine:
    """
    Comprehensive fairness metrics engine
    Calculates all 5 fairness metrics and provides aggregate analysis
    """
    
    def __init__(self):
        self.metrics = {
            'DIR': DisparateImpactRatio(),
            'SPD': StatisticalParityDifference(),
            'EOD': EqualOpportunityDifference(),
            'AOD': AverageOddsDifference(),
            'THEIL': TheilIndex()
        }
    
    def calculate_all_metrics(self, 
                              y_true: np.ndarray, 
                              y_pred: np.ndarray, 
                              protected_attribute: np.ndarray) -> Dict[str, Any]:
        """
        Calculate all fairness metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            protected_attribute: Protected attribute (0=privileged, 1=protected)
        
        Returns:
            Dictionary with all metrics and overall fairness assessment
        """
        results = {}
        
        for metric_id, metric in self.metrics.items():
            try:
                results[metric_id] = metric.calculate(y_true, y_pred, protected_attribute)
            except Exception as e:
                logger.error(f"Error calculating {metric_id}: {e}")
                results[metric_id] = {
                    'name': metric.get_name(),
                    'value': None,
                    'error': str(e),
                    'status': 'ERROR'
                }
        
        # Calculate overall fairness
        passed_metrics = sum(1 for r in results.values() if r.get('is_fair', False))
        total_metrics = len(results)
        
        overall_fairness = {
            'all_metrics': results,
            'summary': {
                'total_metrics': total_metrics,
                'passed': passed_metrics,
                'failed': total_metrics - passed_metrics,
                'fairness_score': passed_metrics / total_metrics,
                'overall_status': 'PASS' if passed_metrics == total_metrics else 'FAIL',
                'compliance_level': self._get_compliance_level(passed_metrics, total_metrics)
            }
        }
        
        return overall_fairness
    
    def _get_compliance_level(self, passed: int, total: int) -> str:
        """Determine compliance level based on passed metrics"""
        score = passed / total
        
        if score == 1.0:
            return 'FULL_COMPLIANCE'
        elif score >= 0.8:
            return 'HIGH_COMPLIANCE'
        elif score >= 0.6:
            return 'MODERATE_COMPLIANCE'
        elif score >= 0.4:
            return 'LOW_COMPLIANCE'
        else:
            return 'NON_COMPLIANT'
    
    def get_metric(self, metric_id: str) -> FairnessMetric:
        """Get a specific metric by ID"""
        return self.metrics.get(metric_id)
    
    def list_metrics(self) -> List[Dict[str, Any]]:
        """List all available metrics"""
        return [
            {
                'id': metric_id,
                'name': metric.get_name(),
                'threshold': metric.get_threshold()
            }
            for metric_id, metric in self.metrics.items()
        ]
