"""
Trend Analyzer for BiasCheck Fairness Monitoring System

Purpose: Analyze temporal fairness trends and predict drift before it happens.
This module implements predictive fairness monitoring by detecting gradual
degradation in fairness metrics over time.

How it fits: This is the PREDICTIVE layer in the BiasCheck pipeline.
Data → Metric → Detect → Alert → Log → DB → [Trend Analysis] → Pre-Alert
"""

import statistics
from typing import Dict, List, Optional
from db_manager import get_recent_checks


def get_recent_trend(window: int = 10, model_name: str = None) -> Dict:
    """
    Analyze recent fairness trend using moving average.
    
    This function retrieves the last 'window' fairness checks and computes
    statistical trends to detect gradual fairness degradation.
    
    Parameters:
    -----------
    window : int
        Number of recent checks to analyze (default: 10)
    model_name : str, optional
        Filter by specific model name
    
    Returns:
    --------
    Dict containing:
        - average_dir: mean DIR value over the window
        - median_dir: median DIR value
        - min_dir: minimum DIR value
        - max_dir: maximum DIR value
        - trend_direction: "up", "down", or "stable"
        - alert_count: number of alerts in the window
        - data_points: number of records analyzed
    
    Trend Direction Logic:
    ----------------------
    - Compare first half vs second half of the window
    - If second half average < first half average by >0.05 → "down"
    - If second half average > first half average by >0.05 → "up"
    - Otherwise → "stable"
    """
    records = get_recent_checks(limit=window, model_name=model_name)
    
    if not records:
        return {
            "average_dir": None,
            "median_dir": None,
            "min_dir": None,
            "max_dir": None,
            "trend_direction": "unknown",
            "alert_count": 0,
            "data_points": 0,
            "message": "No data available for trend analysis"
        }
    
    # Extract DIR values (reverse to get chronological order)
    dir_values = [r['dir_value'] for r in reversed(records)]
    alert_count = sum(1 for r in records if r['alert_status'])
    
    # Calculate statistics
    avg_dir = statistics.mean(dir_values)
    median_dir = statistics.median(dir_values)
    min_dir = min(dir_values)
    max_dir = max(dir_values)
    
    # Determine trend direction
    trend_direction = "stable"
    if len(dir_values) >= 4:
        # Split into first half and second half
        mid_point = len(dir_values) // 2
        first_half_avg = statistics.mean(dir_values[:mid_point])
        second_half_avg = statistics.mean(dir_values[mid_point:])
        
        difference = second_half_avg - first_half_avg
        
        if difference < -0.05:
            trend_direction = "down"
        elif difference > 0.05:
            trend_direction = "up"
    
    return {
        "average_dir": round(avg_dir, 4),
        "median_dir": round(median_dir, 4),
        "min_dir": round(min_dir, 4),
        "max_dir": round(max_dir, 4),
        "trend_direction": trend_direction,
        "alert_count": alert_count,
        "data_points": len(dir_values),
        "dir_values": [round(v, 4) for v in dir_values]
    }


def check_pre_alert(threshold: float = 0.8, window: int = 10, model_name: str = None) -> Dict:
    """
    Check for early warning signs of fairness degradation.
    
    This is PREDICTIVE fairness monitoring - it detects problems before
    they cross the legal threshold. Even if current DIR ≥ 0.8, if the
    trend is declining, we issue a pre-alert.
    
    Parameters:
    -----------
    threshold : float
        The fairness threshold (default: 0.8 for EEOC rule)
    window : int
        Number of recent checks to analyze
    model_name : str, optional
        Filter by specific model name
    
    Returns:
    --------
    Dict containing:
        - pre_alert: True if fairness is degrading
        - current_avg: current average DIR
        - trend: trend direction
        - message: human-readable warning
        - severity: "none", "low", "medium", "high"
    
    Pre-Alert Logic:
    ----------------
    1. If average DIR < threshold → HIGH severity (already unfair)
    2. If average DIR ≥ threshold but trend is "down" → MEDIUM severity
    3. If average DIR ≥ threshold + 0.1 and trend is "down" → LOW severity
    4. Otherwise → no alert
    """
    trend_data = get_recent_trend(window=window, model_name=model_name)
    
    if trend_data['data_points'] == 0:
        return {
            "pre_alert": False,
            "current_avg": None,
            "trend": "unknown",
            "message": "Insufficient data for pre-alert analysis",
            "severity": "none"
        }
    
    avg_dir = trend_data['average_dir']
    trend = trend_data['trend_direction']
    alert_count = trend_data['alert_count']
    
    # Determine severity and message
    if avg_dir < threshold:
        # Already below threshold - critical
        return {
            "pre_alert": True,
            "current_avg": avg_dir,
            "trend": trend,
            "message": f"⚠️ CRITICAL: Average DIR ({avg_dir:.3f}) is below threshold ({threshold}). "
                      f"{alert_count} alerts in last {window} checks.",
            "severity": "high",
            "recommendation": "Immediate model review required. Fairness threshold violated."
        }
    
    elif trend == "down":
        # Trending down but still above threshold - warning
        if avg_dir < threshold + 0.1:
            # Close to threshold
            return {
                "pre_alert": True,
                "current_avg": avg_dir,
                "trend": trend,
                "message": f"⚠️ WARNING: Fairness degrading. Average DIR ({avg_dir:.3f}) is declining "
                          f"and approaching threshold ({threshold}).",
                "severity": "medium",
                "recommendation": "Monitor closely. Consider model retraining if trend continues."
            }
        else:
            # Still safe but declining
            return {
                "pre_alert": True,
                "current_avg": avg_dir,
                "trend": trend,
                "message": f"ℹ️ NOTICE: Fairness trend declining. Average DIR ({avg_dir:.3f}) is decreasing "
                          f"but still above threshold.",
                "severity": "low",
                "recommendation": "Continue monitoring. Investigate data quality and model inputs."
            }
    
    else:
        # All good
        return {
            "pre_alert": False,
            "current_avg": avg_dir,
            "trend": trend,
            "message": f"✅ Fairness stable. Average DIR ({avg_dir:.3f}) is above threshold "
                      f"with {trend} trend.",
            "severity": "none",
            "recommendation": "Continue regular monitoring."
        }


def calculate_drift_velocity(window: int = 10, model_name: str = None) -> Dict:
    """
    Calculate the rate of fairness change (drift velocity).
    
    This metric shows how fast fairness is changing, which helps
    predict when it might cross the threshold.
    
    Parameters:
    -----------
    window : int
        Number of recent checks to analyze
    model_name : str, optional
        Filter by specific model name
    
    Returns:
    --------
    Dict containing:
        - velocity: rate of change per check
        - estimated_checks_to_threshold: predicted checks until DIR < 0.8
        - is_accelerating: True if decline is speeding up
    """
    records = get_recent_checks(limit=window, model_name=model_name)
    
    if len(records) < 3:
        return {
            "velocity": None,
            "estimated_checks_to_threshold": None,
            "is_accelerating": False,
            "message": "Insufficient data for velocity calculation"
        }
    
    # Get DIR values in chronological order
    dir_values = [r['dir_value'] for r in reversed(records)]
    
    # Calculate simple linear velocity (change per check)
    total_change = dir_values[-1] - dir_values[0]
    velocity = total_change / (len(dir_values) - 1)
    
    # Estimate checks until threshold (if declining)
    estimated_checks = None
    if velocity < 0 and dir_values[-1] > 0.8:
        distance_to_threshold = dir_values[-1] - 0.8
        estimated_checks = int(distance_to_threshold / abs(velocity))
    
    # Check if decline is accelerating
    is_accelerating = False
    if len(dir_values) >= 6:
        first_half_velocity = (dir_values[len(dir_values)//2] - dir_values[0]) / (len(dir_values)//2)
        second_half_velocity = (dir_values[-1] - dir_values[len(dir_values)//2]) / (len(dir_values) - len(dir_values)//2)
        is_accelerating = second_half_velocity < first_half_velocity
    
    return {
        "velocity": round(velocity, 5),
        "estimated_checks_to_threshold": estimated_checks,
        "is_accelerating": is_accelerating,
        "current_dir": round(dir_values[-1], 4),
        "message": f"Fairness changing at {velocity:.5f} per check" if velocity else "Fairness stable"
    }


"""
WHY PREDICTIVE FAIRNESS MATTERS:

Traditional Approach:
- Wait until DIR < 0.8
- React after bias happens
- Damage already done (complaints, legal issues)

BiasCheck Approach:
- Detect declining trends early
- Alert before threshold violation
- Preventive action possible

Real-World Impact:
- A bank can retrain models BEFORE bias affects customers
- Compliance teams get early warnings, not emergency alerts
- Demonstrates proactive ethical AI governance

This is the difference between "fairness auditing" and "fairness monitoring."

HOW TO EXTEND:
- Add seasonal trend detection (monthly patterns)
- Implement ARIMA or Prophet for time-series forecasting
- Add confidence intervals for predictions
- Create fairness SLA (Service Level Agreement) tracking
"""
