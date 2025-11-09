"""
Fairness Metrics Module for BiasCheck

Purpose: Compute Disparate Impact Ratio (DIR) and group approval gaps.

This module implements the EEOC 80% rule (also known as the four-fifths rule),
which is a legal standard used to detect adverse impact in employment and lending.
A DIR < 0.8 indicates potential discrimination against the protected group.

How it fits: This is the METRIC step in the BiasCheck pipeline.
Data → Metric → Detect → Alert → Log → Explain → Visualize
"""

import pandas as pd
from typing import Dict


def calculate_disparate_impact_ratio(
    df: pd.DataFrame,
    protected_attribute: str = "gender",
    protected_value: str = "Female",
    privileged_value: str = "Male",
    outcome: str = "approved"
) -> Dict:
    """
    Calculate Disparate Impact Ratio (DIR) and approval rate gap.
    
    The DIR measures the ratio of approval rates between protected and privileged groups.
    According to the EEOC 80% rule, a DIR below 0.8 (or 4/5) suggests potential
    discrimination and requires investigation.
    
    Formula:
    --------
    DIR = (approval_rate_protected) / (approval_rate_privileged)
    
    Where approval_rate = (approved_count) / (total_count) for each group.
    
    EEOC 80% Rule:
    --------------
    - DIR >= 0.8: No adverse impact indicated (system considered fair)
    - DIR < 0.8: Adverse impact detected (potential discrimination)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset containing loan applications with protected attribute and outcome.
    
    protected_attribute : str, default="gender"
        Column name of the protected attribute (e.g., 'gender', 'race', 'age_group').
    
    protected_value : str, default="Female"
        Value identifying the protected/disadvantaged group.
    
    privileged_value : str, default="Male"
        Value identifying the privileged/advantaged group.
    
    outcome : str, default="approved"
        Column name of the binary outcome (True/False or 1/0).
    
    Returns:
    --------
    Dict
        Dictionary containing:
        - female_rate: approval rate for protected group (float 0-1)
        - male_rate: approval rate for privileged group (float 0-1)
        - dir: Disparate Impact Ratio (float or None if male_rate=0)
        - dir_alert: True if DIR < 0.8 or DIR is None
        - gap: absolute difference between approval rates (float)
        - gap_alert: True if gap > 0.2 (20 percentage points)
        - details: dict with female_count and male_count
    
    Edge Cases:
    -----------
    - If male_rate = 0: DIR is undefined (None), alert is True
    - If groups are missing: rates set to 0.0
    
    Examples:
    ---------
    >>> df = pd.DataFrame({
    ...     'gender': ['Female', 'Female', 'Male', 'Male'],
    ...     'approved': [True, False, True, True]
    ... })
    >>> result = calculate_disparate_impact_ratio(df)
    >>> print(f"DIR: {result['dir']:.2f}, Alert: {result['dir_alert']}")
    DIR: 0.50, Alert: True
    """
    
    # Filter data by group
    protected_group = df[df[protected_attribute] == protected_value]
    privileged_group = df[df[protected_attribute] == privileged_value]
    
    # Count totals and approvals for each group
    female_count = len(protected_group)
    male_count = len(privileged_group)
    
    # Handle edge case: empty groups
    if female_count == 0:
        female_rate = 0.0
        female_approved = 0
    else:
        female_approved = protected_group[outcome].sum()
        female_rate = female_approved / female_count
    
    if male_count == 0:
        male_rate = 0.0
        male_approved = 0
    else:
        male_approved = privileged_group[outcome].sum()
        male_rate = male_approved / male_count
    
    # Calculate Disparate Impact Ratio (DIR)
    # DIR is only computable if male_rate > 0 (avoid division by zero)
    if male_rate > 0:
        dir_value = female_rate / male_rate
    else:
        dir_value = None  # Undefined when privileged group has 0% approval
    
    # Apply EEOC 80% rule: DIR < 0.8 triggers alert
    # Also alert if DIR is None (cannot compute)
    dir_alert = (dir_value is None) or (dir_value < 0.8)
    
    # Calculate absolute approval rate gap
    # Gap > 0.2 (20 percentage points) is also a simple fairness threshold
    gap = abs(male_rate - female_rate)
    gap_alert = gap > 0.2
    
    return {
        "female_rate": float(female_rate),
        "male_rate": float(male_rate),
        "dir": float(dir_value) if dir_value is not None else None,
        "dir_alert": bool(dir_alert),
        "gap": float(gap),
        "gap_alert": bool(gap_alert),
        "details": {
            "female_count": int(female_count),
            "male_count": int(male_count),
            "female_approved": int(female_approved) if female_count > 0 else 0,
            "male_approved": int(male_approved) if male_count > 0 else 0
        }
    }
