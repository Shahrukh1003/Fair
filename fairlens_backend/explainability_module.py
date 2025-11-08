"""
Explainability Module for FairLens

Purpose: Generate statistical explanations for detected bias.

This module provides simple, interpretable explanations for why fairness drift
occurred by analyzing feature distributions and approval rates across groups.

IMPORTANT LIMITATIONS:
----------------------
- Purely statistical analysis (correlation, not causation)
- Does not perform causal inference
- Not a substitute for fairness-aware machine learning
- Explanations are descriptive, not prescriptive

For deeper analysis, consider:
- Causal inference methods (do-calculus, counterfactuals)
- Fairness-aware feature importance (SHAP, LIME with fairness constraints)
- Structural equation modeling

How it fits: This is the EXPLAIN step in the FairLens pipeline.
Data → Metric → Detect → Alert → Log → Explain → Visualize
"""

import pandas as pd
from typing import Dict, List, Optional
import numpy as np


def analyze_feature_impact(
    df: pd.DataFrame,
    protected_attribute: str = "gender",
    numeric_cols: Optional[List[str]] = None
) -> Dict:
    """
    Analyze feature distributions to identify potential bias causes.
    
    This function computes group-level statistics and compares them to identify
    features that differ significantly between protected and privileged groups.
    
    Analysis performed:
    -------------------
    1. Group-level means and medians for numeric features
    2. Approval rates per group
    3. Normalized differences (delta / mean) for ranking
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset containing applications with protected attribute and features.
    
    protected_attribute : str, default="gender"
        Column name of protected attribute (e.g., 'gender').
    
    numeric_cols : List[str], default=["credit_score"]
        List of numeric columns to analyze.
    
    Returns:
    --------
    Dict
        Dictionary containing:
        - likely_causes: list of human-readable explanations
        - stats: detailed statistics for each group
    
    Examples:
    ---------
    >>> result = analyze_feature_impact(df)
    >>> print(result['likely_causes'])
    ['Lower average credit_score for females', 'Lower female approval rate']
    """
    if numeric_cols is None:
        numeric_cols = ["credit_score"]
    
    # Split data by protected attribute
    female_data = df[df[protected_attribute] == "Female"]
    male_data = df[df[protected_attribute] == "Male"]
    
    # Initialize statistics dictionary
    stats = {}
    likely_causes = []
    
    # Calculate approval rates
    if len(female_data) > 0:
        female_approval_rate = female_data['approved'].sum() / len(female_data)
        stats['female_approval_rate'] = float(female_approval_rate)
    else:
        female_approval_rate = 0.0
        stats['female_approval_rate'] = 0.0
    
    if len(male_data) > 0:
        male_approval_rate = male_data['approved'].sum() / len(male_data)
        stats['male_approval_rate'] = float(male_approval_rate)
    else:
        male_approval_rate = 0.0
        stats['male_approval_rate'] = 0.0
    
    # Analyze numeric features
    feature_deltas = []
    
    for col in numeric_cols:
        if col in df.columns:
            female_mean = female_data[col].mean() if len(female_data) > 0 else 0.0
            male_mean = male_data[col].mean() if len(male_data) > 0 else 0.0
            
            stats[f'female_mean_{col}'] = float(female_mean)
            stats[f'male_mean_{col}'] = float(male_mean)
            
            # Calculate normalized difference
            delta = male_mean - female_mean
            avg_mean = (female_mean + male_mean) / 2.0
            
            if avg_mean > 0:
                normalized_delta = abs(delta) / avg_mean
            else:
                normalized_delta = 0.0
            
            feature_deltas.append({
                'feature': col,
                'delta': delta,
                'normalized_delta': normalized_delta
            })
    
    # Rank features by normalized difference
    feature_deltas.sort(key=lambda x: x['normalized_delta'], reverse=True)
    
    # Generate likely causes based on top features
    for feat_info in feature_deltas[:2]:  # Top 2 features
        if feat_info['delta'] > 0:
            likely_causes.append(
                f"Lower average {feat_info['feature']} for females "
                f"(Female: {stats[f'female_mean_{feat_info['feature']}']: .1f}, "
                f"Male: {stats[f'male_mean_{feat_info['feature']}']: .1f})"
            )
    
    # Always mention approval rate difference if significant
    approval_gap = abs(male_approval_rate - female_approval_rate)
    if approval_gap > 0.05:  # 5% threshold
        likely_causes.append(
            f"Approval rate difference "
            f"(Female: {female_approval_rate:.1%}, Male: {male_approval_rate:.1%})"
        )
    
    # Fallback if no causes identified
    if not likely_causes:
        likely_causes = ["Statistical variation in small sample", "No significant feature differences detected"]
    
    return {
        "likely_causes": likely_causes,
        "stats": stats
    }


def generate_explanation(dir_value: float, causes_list: List[str]) -> str:
    """
    Generate human-readable explanation of fairness check result.
    
    This function translates the DIR metric and statistical analysis into
    plain language suitable for compliance reports, dashboards, and alerts.
    
    Parameters:
    -----------
    dir_value : float or None
        The Disparate Impact Ratio. None if not computable.
    
    causes_list : List[str]
        List of likely causes from analyze_feature_impact().
    
    Returns:
    --------
    str
        Human-readable explanation string.
    
    Examples:
    ---------
    >>> explanation = generate_explanation(0.64, ["Lower credit scores for females"])
    >>> print(explanation)
    DIR = 0.64 (<0.8). Potential bias detected. Likely causes: Lower credit scores for females
    """
    if dir_value is None:
        return "DIR not computable: male approval rate is zero."
    
    if dir_value < 0.8:
        # Alert condition: potential bias
        causes_str = "; ".join(causes_list)
        return (
            f"DIR = {dir_value:.2f} (<0.8). "
            f"Potential bias detected per EEOC 80% rule. "
            f"Likely causes: {causes_str}"
        )
    else:
        # No alert: system considered fair
        causes_str = "; ".join(causes_list[:2])  # Mention top 2 only
        return (
            f"DIR = {dir_value:.2f} (≥0.8). "
            f"System considered fair under EEOC 80% rule. "
            f"Minor contributing factors: {causes_str}"
        )
