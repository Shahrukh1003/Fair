"""
FairLens - Fairness Drift Alert System

A lightweight, runnable Flask-based Fairness Drift Alert System that:
1. Simulates loan decisions with controllable bias
2. Computes fairness using Disparate Impact Ratio (DIR) and group gap
3. Triggers & encrypts alerts
4. Writes immutable compliance logs
5. Generates simple explanations for bias causes
6. Exposes a Streamlit dashboard that visualizes trends

Pipeline: Data → Metric → Detect → Alert → Log → Explain → Visualize
"""

__version__ = "1.0.0"
__author__ = "FairLens Team"
