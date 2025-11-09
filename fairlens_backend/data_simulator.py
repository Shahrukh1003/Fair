"""
Data Simulator Module for BiasCheck

Purpose: Generate synthetic loan application records with controllable bias.

This module creates realistic loan application datasets where bias can be injected
in a controlled manner by reducing approval rates for protected groups (e.g., females)
relative to privileged groups (e.g., males).

How it fits: This is the DATA step in the BiasCheck pipeline.
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
        - income: annual income between $20,000 and $150,000
        - credit_score: integer score between 500 and 800
        - age: applicant age between 22 and 65
        - existing_debt: current debt between $0 and $80,000
        - employment_length: years at current job (0-20)
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
    
    # Generate additional realistic features for ML model
    # Income: correlated with credit score, range $20k-$150k
    income_base = (credit_scores - 500) * 200 + 20000
    income = np.clip(
        income_base + np.random.normal(0, 10000, size=n_samples),
        20000,
        150000
    ).astype(int)
    
    # Age: adults between 22-65
    age = np.clip(
        np.random.normal(38, 12, size=n_samples),
        22,
        65
    ).astype(int)
    
    # Existing debt: inversely correlated with credit score, range $0-$80k
    debt_base = (800 - credit_scores) * 150
    existing_debt = np.clip(
        debt_base + np.random.normal(0, 5000, size=n_samples),
        0,
        80000
    ).astype(int)
    
    # Employment length: years at current job, 0-20 years
    employment_length = np.clip(
        np.random.exponential(5, size=n_samples),
        0,
        20
    ).astype(int)
    
    # Generate approval decisions based on group-specific rates
    # Generate all random numbers at once for consistency
    random_values = np.random.rand(n_samples)
    approvals = []
    for i, gender in enumerate(genders):
        if gender == 'Female':
            approved = random_values[i] < female_approval_rate
        else:  # Male
            approved = random_values[i] < male_approval_rate
        approvals.append(approved)
    
    # Construct DataFrame with all features
    df = pd.DataFrame({
        'application_id': application_ids,
        'gender': genders,
        'income': income,
        'credit_score': credit_scores,
        'age': age,
        'existing_debt': existing_debt,
        'employment_length': employment_length,
        'approved': approvals
    })
    
    return df
