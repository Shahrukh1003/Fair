"""
Data Simulator Module for FairLens

Purpose: Generate synthetic loan application records with controllable bias.

This module creates realistic loan application datasets where bias can be injected
in a controlled manner by reducing approval rates for protected groups (e.g., females)
relative to privileged groups (e.g., males).

How it fits: This is the DATA step in the FairLens pipeline.
Data → Metric → Detect → Alert → Log → Explain → Visualize
"""

import pandas as pd
import numpy as np
from typing import Tuple


def generate_loan_data(n_samples: int, drift_level: float, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic loan application data with controllable bias.
    
    Bias is injected by reducing the approval probability for female applicants
    proportionally to the drift_level parameter. This simulates real-world scenarios
    where algorithmic or systemic bias may disadvantage protected groups.
    
    Parameters:
    -----------
    n_samples : int
        Total number of loan applications to generate. Will be split approximately
        evenly between Male and Female applicants.
    
    drift_level : float
        Bias intensity level in range [0.0, 1.0]
        - 0.0 = no bias (equal approval rates for both groups)
        - 1.0 = maximum bias (female approval rate reduced by 40 percentage points)
        Linear interpolation: female_approval = base_rate - (drift_level * 0.4)
    
    seed : int, default=42
        Random seed for reproducibility of results.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns:
        - application_id: unique integer identifier (1 to n_samples)
        - gender: 'Male' or 'Female'
        - credit_score: integer score between 500 and 800
        - approved: boolean indicating if loan was approved
    
    Examples:
    ---------
    >>> # Generate fair data (no bias)
    >>> fair_data = generate_loan_data(1000, drift_level=0.0)
    >>> 
    >>> # Generate biased data (moderate drift)
    >>> biased_data = generate_loan_data(1000, drift_level=0.5)
    """
    np.random.seed(seed)
    
    # Handle edge case: ensure minimum samples
    if n_samples < 2:
        n_samples = 2
    
    # Base approval rate for the privileged group (males)
    base_approval_rate = 0.70  # 70% baseline
    
    # Bias injection formula:
    # Female approval rate decreases linearly with drift_level
    # When drift_level=0.0: female_rate = 0.70 (fair)
    # When drift_level=1.0: female_rate = 0.30 (40 percentage points lower)
    female_approval_rate = max(0.0, base_approval_rate - drift_level * 0.4)
    male_approval_rate = base_approval_rate
    
    # Split samples approximately evenly between genders
    n_female = n_samples // 2
    n_male = n_samples - n_female  # Handle odd numbers
    
    # Generate data arrays
    application_ids = list(range(1, n_samples + 1))
    
    # Create gender labels
    genders = ['Female'] * n_female + ['Male'] * n_male
    
    # Generate credit scores using normal distribution clipped to 500-800 range
    # Mean=650, StdDev=60 gives realistic distribution
    credit_scores = np.clip(
        np.random.normal(650, 60, size=n_samples),
        500,
        800
    ).astype(int)
    
    # Generate approval decisions based on group-specific rates
    approvals = []
    for gender in genders:
        if gender == 'Female':
            approved = np.random.rand() < female_approval_rate
        else:  # Male
            approved = np.random.rand() < male_approval_rate
        approvals.append(approved)
    
    # Construct DataFrame
    df = pd.DataFrame({
        'application_id': application_ids,
        'gender': genders,
        'credit_score': credit_scores,
        'approved': approvals
    })
    
    return df
