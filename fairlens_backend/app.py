"""
Flask API for FairLens Fairness Drift Alert System

Purpose: Orchestrator that ties together all FairLens modules via REST API endpoints.

This Flask application serves as the backend for fairness monitoring, providing:
- /api/monitor_fairness: Generate data, compute metrics, trigger alerts
- /api/audit_history: Retrieve compliance audit log

How it fits: This is the ORCHESTRATION layer in the FairLens pipeline.
Data → Metric → Detect → Alert → Log → Explain → Visualize
                           ↑                          ↑
                        [THIS API]              Dashboard queries
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import sys

try:
    from .data_simulator import generate_loan_data
    from .fairness_metrics import calculate_disparate_impact_ratio
    from .security_utils import encrypt_alert, decrypt_alert, init_key, anonymize_data
    from .compliance_logger import log_event, get_audit_history
    from .explainability_module import analyze_feature_impact, generate_explanation
except ImportError:
    from data_simulator import generate_loan_data
    from fairness_metrics import calculate_disparate_impact_ratio
    from security_utils import encrypt_alert, decrypt_alert, init_key, anonymize_data
    from compliance_logger import log_event, get_audit_history
    from explainability_module import analyze_feature_impact, generate_explanation

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

encryption_key = init_key()


@app.route('/api/monitor_fairness', methods=['GET'])
def monitor_fairness():
    """
    Main endpoint for fairness monitoring.
    
    Query Parameters:
    -----------------
    - n_samples (int): Number of loan applications to generate (default: 1000)
    - drift_level (float): Bias level 0.0-1.0 (default: 0.5)
    
    Returns:
    --------
    JSON object with:
    - fair_scenario: metrics for unbiased baseline (drift=0.0)
    - drifted_scenario: metrics for requested drift level
    - audit_tail: last 10 compliance log entries
    
    Process:
    --------
    1. Generate two datasets: fair (drift=0.0) and drifted (drift=user_specified)
    2. Compute DIR and gap metrics for both
    3. If DIR < 0.8: trigger alert, encrypt message, log to compliance
    4. Generate explanations for bias causes
    5. Return comprehensive results
    """
    try:
        n_samples = int(request.args.get('n_samples', 1000))
        drift_level = float(request.args.get('drift_level', 0.5))
        
        n_samples = max(10, min(n_samples, 10000))
        drift_level = max(0.0, min(drift_level, 1.0))
        
        logger.info(f"Fairness check requested: n_samples={n_samples}, drift_level={drift_level}")
        
        fair_data = generate_loan_data(n_samples, drift_level=0.0, seed=42)
        drifted_data = generate_loan_data(n_samples, drift_level=drift_level, seed=42)
        
        fair_metrics = calculate_disparate_impact_ratio(fair_data)
        drifted_metrics = calculate_disparate_impact_ratio(drifted_data)
        
        impact_analysis = analyze_feature_impact(drifted_data, numeric_cols=["credit_score"])
        explanation = generate_explanation(
            drifted_metrics['dir'],
            impact_analysis['likely_causes']
        )
        
        encrypted_alert = None
        
        if drifted_metrics['dir_alert']:
            encrypted_alert = encrypt_alert(explanation, encryption_key)
            decrypted_msg = decrypt_alert(encrypted_alert, encryption_key)
            
            logger.warning(f"⚠ ALERT: Fairness Drift Detected! DIR = {drifted_metrics['dir']}")
            logger.info(f"Encrypted alert token: {encrypted_alert[:50]}...")
            logger.info(f"Decrypted alert: {decrypted_msg}")
            
            log_event("fairness_check", {
                "status": "ALERT",
                "dir": drifted_metrics['dir'],
                "female_rate": drifted_metrics['female_rate'],
                "male_rate": drifted_metrics['male_rate'],
                "drift_level": drift_level,
                "n_samples": n_samples,
                "encrypted_alert": encrypted_alert,
                "explanation": explanation
            })
        else:
            logger.info(f"✅ Model Fairness Stable. DIR = {drifted_metrics['dir']}")
            
            log_event("fairness_check", {
                "status": "OK",
                "dir": drifted_metrics['dir'],
                "female_rate": drifted_metrics['female_rate'],
                "male_rate": drifted_metrics['male_rate'],
                "drift_level": drift_level,
                "n_samples": n_samples,
                "explanation": explanation
            })
        
        audit_tail = get_audit_history(last_n=10)
        
        response = {
            "fair_scenario": {
                "female_rate": fair_metrics['female_rate'],
                "male_rate": fair_metrics['male_rate'],
                "dir": fair_metrics['dir'],
                "dir_alert": fair_metrics['dir_alert'],
                "gap": fair_metrics['gap'],
                "gap_alert": fair_metrics['gap_alert'],
                "details": fair_metrics['details']
            },
            "drifted_scenario": {
                "female_rate": drifted_metrics['female_rate'],
                "male_rate": drifted_metrics['male_rate'],
                "dir": drifted_metrics['dir'],
                "dir_alert": drifted_metrics['dir_alert'],
                "gap": drifted_metrics['gap'],
                "gap_alert": drifted_metrics['gap_alert'],
                "explanation": explanation,
                "encrypted_alert": encrypted_alert,
                "likely_causes": impact_analysis['likely_causes'],
                "stats": impact_analysis['stats'],
                "details": drifted_metrics['details']
            },
            "audit_tail": audit_tail,
            "parameters": {
                "n_samples": n_samples,
                "drift_level": drift_level
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in monitor_fairness: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to complete fairness check"
        }), 500


@app.route('/api/audit_history', methods=['GET'])
def audit_history():
    """
    Retrieve compliance audit log.
    
    Query Parameters:
    -----------------
    - last_n (int): Number of recent entries to return (default: 10)
    
    Returns:
    --------
    JSON array of audit log entries.
    
    Note: In production, this endpoint should be access-controlled with
    role-based authentication (e.g., auditor role only). This is a demo
    implementation without authentication.
    """
    try:
        last_n = int(request.args.get('last_n', 10))
        last_n = max(1, min(last_n, 100))
        
        history = get_audit_history(last_n=last_n)
        
        return jsonify({
            "entries": history,
            "count": len(history)
        })
    
    except Exception as e:
        logger.error(f"Error in audit_history: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to retrieve audit history"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and deployment."""
    return jsonify({
        "status": "healthy",
        "service": "FairLens Fairness Drift Alert System",
        "version": "1.0.0"
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation."""
    return jsonify({
        "service": "FairLens Fairness Drift Alert System",
        "version": "1.0.0",
        "endpoints": {
            "/api/monitor_fairness": "Perform fairness check (params: n_samples, drift_level)",
            "/api/audit_history": "Retrieve compliance audit log (params: last_n)",
            "/api/health": "Health check"
        },
        "fairness_metrics": {
            "DIR": "Disparate Impact Ratio (EEOC 80% rule)",
            "alert_threshold": "DIR < 0.8 triggers bias alert",
            "gap_threshold": "Gap > 0.2 (20 percentage points)"
        },
        "usage": {
            "example": "/api/monitor_fairness?n_samples=1000&drift_level=0.5"
        }
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("FairLens Fairness Drift Alert System")
    logger.info("=" * 60)
    logger.info("")
    logger.info("How Fairness Drift is Calculated:")
    logger.info("  DIR (Disparate Impact Ratio) = female_approval_rate / male_approval_rate")
    logger.info("  EEOC 80% Rule: DIR < 0.8 indicates potential discrimination")
    logger.info("  Gap = |female_rate - male_rate|")
    logger.info("")
    logger.info("How the System Detects Drift:")
    logger.info("  1. Generate synthetic loan data with configurable bias (drift_level)")
    logger.info("  2. Calculate DIR and compare to 0.8 threshold")
    logger.info("  3. If DIR < 0.8: Trigger alert, encrypt message, log to audit trail")
    logger.info("  4. Analyze feature distributions to explain bias causes")
    logger.info("")
    logger.info("Running Flask API and Streamlit Dashboard:")
    logger.info("  Flask API:  python fairlens_backend/app.py")
    logger.info("              OR: FLASK_APP=fairlens_backend.app flask run --port 5000")
    logger.info("  Streamlit:  streamlit run fairlens_backend/dashboard.py --server.port 8501")
    logger.info("")
    logger.info("Ethical AI & Banking Compliance:")
    logger.info("  - EEOC 80% rule enforces fair lending practices")
    logger.info("  - Immutable audit trail provides regulatory compliance")
    logger.info("  - Encrypted alerts protect sensitive fairness findings")
    logger.info("  - Statistical explanations enable bias remediation")
    logger.info("")
    logger.info("=" * 60)
    port = int(os.environ.get('FLASK_PORT', 8000))
    logger.info(f"FairLens API running on http://127.0.0.1:{port}")
    logger.info("=" * 60)
    logger.info("")
    
    app.run(host='0.0.0.0', port=port, debug=False)
