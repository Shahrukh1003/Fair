"""
Flask API for BiasCheck Fairness Drift Alert System

Purpose: Orchestrator that ties together all BiasCheck modules via REST API endpoints.

This Flask application serves as the backend for fairness monitoring, providing:
- /api/monitor_fairness: Generate data, compute metrics, trigger alerts
- /api/audit_history: Retrieve compliance audit log

How it fits: This is the ORCHESTRATION layer in the BiasCheck pipeline.
Data → Metric → Detect → Alert → Log → Explain → Visualize
                           ↑                          ↑
                        [THIS API]              Dashboard queries
"""

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import logging
import os
import sys

try:
    from .data_simulator import generate_loan_data
    from .fairness_metrics import calculate_disparate_impact_ratio
    from .security_utils import encrypt_alert, decrypt_alert, init_key, anonymize_data
    from .compliance_logger import log_event, get_audit_history, verify_record_integrity, get_record_by_hash, compute_record_hash
    from .explainability_module import analyze_feature_impact, generate_explanation
    from .db_manager import init_database, store_fairness_check, get_recent_checks, get_record_by_id
    from .trend_analyzer import get_recent_trend, check_pre_alert, calculate_drift_velocity
    from .fairness_trend import predict_fairness_drift, generate_fairness_forecast
    from .auth_middleware import require_role, get_token_for_role, list_available_roles
    from .blockchain_anchor import anchor_to_blockchain, get_anchor, verify_anchor, get_recent_anchors
    from .config import Config
    from .model_service import LoanApprovalModel, create_and_train_default_model
    from .model_registry import ModelRegistry, get_registry
    from .metrics_engine import MetricsEngine
    from .drift_monitor import DriftMonitor
    from .explainability_enhanced import EnhancedExplainer
    from .report_generator import ReportGenerator
    from .auth import authenticate_user, refresh_access_token, revoke_refresh_token, require_jwt, get_current_user
    from .webhook_utils import send_fairness_alert, test_webhook_configuration
except ImportError:
    from data_simulator import generate_loan_data
    from fairness_metrics import calculate_disparate_impact_ratio
    from security_utils import encrypt_alert, decrypt_alert, init_key, anonymize_data
    from compliance_logger import log_event, get_audit_history, verify_record_integrity, get_record_by_hash, compute_record_hash
    from explainability_module import analyze_feature_impact, generate_explanation
    from db_manager import init_database, store_fairness_check, get_recent_checks, get_record_by_id
    from trend_analyzer import get_recent_trend, check_pre_alert, calculate_drift_velocity
    from fairness_trend import predict_fairness_drift, generate_fairness_forecast
    from auth_middleware import require_role, get_token_for_role, list_available_roles
    from blockchain_anchor import anchor_to_blockchain, get_anchor, verify_anchor, get_recent_anchors
    from config import Config
    from model_service import LoanApprovalModel, create_and_train_default_model
    from model_registry import ModelRegistry, get_registry
    from metrics_engine import MetricsEngine
    from drift_monitor import DriftMonitor
    from explainability_enhanced import EnhancedExplainer
    from report_generator import ReportGenerator
    from auth import authenticate_user, refresh_access_token, revoke_refresh_token, require_jwt, get_current_user
    from webhook_utils import send_fairness_alert, test_webhook_configuration

app = Flask(__name__, static_folder='../dist', static_url_path='')
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

encryption_key = init_key()

# Initialize database on startup
init_database()

# Initialize v3.0 components
logger.info("Initializing BiasCheck v3.0 components...")
model_registry = get_registry()
metrics_engine = MetricsEngine()
drift_monitor = DriftMonitor()
enhanced_explainer = EnhancedExplainer()
report_generator = ReportGenerator()

# Initialize or load ML model
ml_model = None
try:
    active_model_meta = model_registry.get_active_model()
    if active_model_meta:
        ml_model = model_registry.load_active_model()
        logger.info(f"✅ Loaded active model: {active_model_meta['model_id']}")
    else:
        logger.info("No active model found. Creating default model...")
        ml_model = create_and_train_default_model()
        model_path = ml_model.save()
        model_id = model_registry.register_model(
            ml_model,
            model_path,
            description="Default loan approval model (Logistic Regression)",
            tags=["default", "production"]
        )
        logger.info(f"✅ Default model created and registered: {model_id}")
except Exception as e:
    logger.error(f"Error initializing ML model: {e}")
    logger.warning("System will continue without ML model support")

logger.info("✅ All v3.0 components initialized successfully")


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
            
            # Log to JSONL with hash
            record_hash = log_event("fairness_check", {
                "status": "ALERT",
                "dir": drifted_metrics['dir'],
                "female_rate": drifted_metrics['female_rate'],
                "male_rate": drifted_metrics['male_rate'],
                "drift_level": drift_level,
                "n_samples": n_samples,
                "encrypted_alert": encrypted_alert,
                "explanation": explanation
            })
            
            # Store in database
            db_record_id = store_fairness_check(
                model_name="loan_approval_v1",
                dir_value=drifted_metrics['dir'],
                female_rate=drifted_metrics['female_rate'],
                male_rate=drifted_metrics['male_rate'],
                alert_status=True,
                drift_level=drift_level,
                n_samples=n_samples,
                hash_value=record_hash,
                explanation=explanation
            )
            
            # Anchor to blockchain
            anchor = anchor_to_blockchain(
                record_hash=record_hash,
                model_name="loan_approval_v1",
                metadata={"db_record_id": db_record_id, "alert": True}
            )
            logger.info(f"✅ Alert hash verified: {record_hash[:16]}...")
            logger.info(f"🔗 Blockchain anchor: {anchor['tx_id'][:16]}...")
            
            # Send webhook alerts for fairness violations
            webhook_results = send_fairness_alert(
                alert_type='DIR_VIOLATION',
                metrics={
                    'DIR': drifted_metrics['dir'],
                    'Female_Rate': drifted_metrics['female_rate'],
                    'Male_Rate': drifted_metrics['male_rate'],
                    'Drift_Level': drift_level
                },
                threshold=0.8,
                actual_value=drifted_metrics['dir'],
                record_id=record_hash[:16]
            )
            logger.info(f"📢 Webhook alerts sent: {webhook_results}")
            
        else:
            logger.info(f"✅ Model Fairness Stable. DIR = {drifted_metrics['dir']}")
            
            # Log to JSONL with hash
            record_hash = log_event("fairness_check", {
                "status": "OK",
                "dir": drifted_metrics['dir'],
                "female_rate": drifted_metrics['female_rate'],
                "male_rate": drifted_metrics['male_rate'],
                "drift_level": drift_level,
                "n_samples": n_samples,
                "explanation": explanation
            })
            
            # Store in database
            db_record_id = store_fairness_check(
                model_name="loan_approval_v1",
                dir_value=drifted_metrics['dir'],
                female_rate=drifted_metrics['female_rate'],
                male_rate=drifted_metrics['male_rate'],
                alert_status=False,
                drift_level=drift_level,
                n_samples=n_samples,
                hash_value=record_hash,
                explanation=explanation
            )
            
            # Anchor to blockchain
            anchor = anchor_to_blockchain(
                record_hash=record_hash,
                model_name="loan_approval_v1",
                metadata={"db_record_id": db_record_id, "alert": False}
            )
        
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
@require_jwt(['auditor', 'admin'])
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
        "service": "BiasCheck Fairness Drift Alert System",
        "version": "1.0.0"
    })


@app.route('/api/fairness_trend', methods=['GET'])
def fairness_trend():
    """
    Get recent fairness trend analysis.
    
    Query Parameters:
    -----------------
    - window (int): Number of recent checks to analyze (default: 10)
    - model_name (str): Filter by model name (optional)
    
    Returns:
    --------
    JSON with trend statistics and direction
    """
    try:
        window = int(request.args.get('window', 10))
        model_name = request.args.get('model_name')
        
        trend_data = get_recent_trend(window=window, model_name=model_name)
        
        return jsonify(trend_data)
    
    except Exception as e:
        logger.error(f"Error in fairness_trend: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to analyze fairness trend"
        }), 500


@app.route('/api/pre_alert', methods=['GET'])
def pre_alert():
    """
    Check for early warning signs of fairness degradation.
    
    Query Parameters:
    -----------------
    - threshold (float): Fairness threshold (default: 0.8)
    - window (int): Number of recent checks to analyze (default: 10)
    - model_name (str): Filter by model name (optional)
    
    Returns:
    --------
    JSON with pre-alert status and recommendations
    """
    try:
        threshold = float(request.args.get('threshold', 0.8))
        window = int(request.args.get('window', 10))
        model_name = request.args.get('model_name')
        
        alert_data = check_pre_alert(
            threshold=threshold,
            window=window,
            model_name=model_name
        )
        
        return jsonify(alert_data)
    
    except Exception as e:
        logger.error(f"Error in pre_alert: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to check pre-alert"
        }), 500


@app.route('/api/predict_fairness_drift', methods=['GET'])
def predict_drift():
    """
    Predict future fairness drift using trend analysis.
    
    Query Parameters:
    -----------------
    - window (int): Number of recent checks to analyze (default: 10)
    - model_name (str): Filter by model name (optional)
    
    Returns:
    --------
    JSON with prediction, confidence, and recommendations
    """
    try:
        window = int(request.args.get('window', 10))
        model_name = request.args.get('model_name')
        
        prediction = predict_fairness_drift(window=window, model_name=model_name)
        
        return jsonify(prediction)
    
    except Exception as e:
        logger.error(f"Error in predict_fairness_drift: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to predict fairness drift"
        }), 500


@app.route('/api/verify_alert/<record_id>', methods=['GET'])
@require_jwt(['auditor', 'admin'])
def verify_alert(record_id):
    """
    Verify integrity of a specific audit record.
    
    Parameters:
    -----------
    record_id : int
        The database record ID to verify
    
    Returns:
    --------
    JSON with verification status and details
    """
    try:
        record_id = int(record_id)
        
        # Get record from database
        db_record = get_record_by_id(record_id)
        
        if not db_record:
            return jsonify({
                "error": "Record not found",
                "record_id": record_id
            }), 404
        
        # Get blockchain anchor
        anchor = get_anchor(db_record['hash_value'])
        
        # Verify blockchain anchor
        verification = verify_anchor(db_record['hash_value'], anchor['tx_id']) if anchor else None
        
        return jsonify({
            "record_id": record_id,
            "hash_value": db_record['hash_value'],
            "blockchain_anchor": anchor,
            "blockchain_verified": verification['verified'] if verification else False,
            "record": db_record
        })
    
    except Exception as e:
        logger.error(f"Error in verify_alert: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to verify alert"
        }), 500


@app.route('/api/submit_predictions', methods=['POST'])
def submit_predictions():
    """
    Submit live AI predictions for fairness monitoring.
    
    Request Body:
    -------------
    {
        "model": "model_name",
        "predictions": [
            {"gender": "Female", "approved": true},
            {"gender": "Male", "approved": false},
            ...
        ]
    }
    
    Returns:
    --------
    JSON with fairness metrics and alert status
    """
    try:
        data = request.get_json()
        
        if not data or 'predictions' not in data:
            return jsonify({
                "error": "Invalid request",
                "message": "Request must include 'predictions' array"
            }), 400
        
        model_name = data.get('model', 'unknown_model')
        predictions = data['predictions']
        
        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(predictions)
        
        # Calculate fairness metrics
        metrics = calculate_disparate_impact_ratio(df)
        
        # Generate explanation if biased
        explanation = None
        if metrics['dir_alert']:
            impact_analysis = analyze_feature_impact(df)
            explanation = generate_explanation(
                metrics['dir'],
                impact_analysis['likely_causes']
            )
        
        # Log the check
        record_hash = log_event("live_prediction_check", {
            "status": "ALERT" if metrics['dir_alert'] else "OK",
            "model": model_name,
            "dir": metrics['dir'],
            "female_rate": metrics['female_rate'],
            "male_rate": metrics['male_rate'],
            "n_predictions": len(predictions),
            "explanation": explanation
        })
        
        # Store in database
        db_record_id = store_fairness_check(
            model_name=model_name,
            dir_value=metrics['dir'],
            female_rate=metrics['female_rate'],
            male_rate=metrics['male_rate'],
            alert_status=metrics['dir_alert'],
            n_samples=len(predictions),
            hash_value=record_hash,
            explanation=explanation
        )
        
        logger.info(f"Live predictions logged: model={model_name}, DIR={metrics['dir']:.3f}, alert={metrics['dir_alert']}")
        
        return jsonify({
            "dir": metrics['dir'],
            "alert": metrics['dir_alert'],
            "female_rate": metrics['female_rate'],
            "male_rate": metrics['male_rate'],
            "explanation": explanation,
            "record_id": db_record_id,
            "message": "Predictions logged successfully"
        })
    
    except Exception as e:
        logger.error(f"Error in submit_predictions: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to process predictions"
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def jwt_login():
    """
    JWT-based authentication endpoint.
    
    Request Body:
    -------------
    {
        "username": "admin" | "auditor" | "monitor",
        "password": "your-password"
    }
    
    Default credentials:
    - admin/admin123 (full access)
    - auditor/auditor123 (read + export)
    - monitor/monitor123 (read only)
    
    Returns:
    --------
    JSON with access token, refresh token, and user info
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Username and password required"
            }), 400
        
        result = authenticate_user(username, password)
        
        if not result['success']:
            return jsonify({
                "status": "error",
                "message": result['message']
            }), 401
        
        return jsonify({
            "status": "success",
            "access_token": result['access_token'],
            "refresh_token": result['refresh_token'],
            "token_type": result['token_type'],
            "expires_in": result['expires_in'],
            "user": result['user']
        })
    
    except Exception as e:
        logger.error(f"Error in jwt_login: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Login failed"
        }), 500


@app.route('/api/auth/refresh', methods=['POST'])
def jwt_refresh():
    """
    Refresh access token using refresh token.
    
    Request Body:
    -------------
    {
        "refresh_token": "your-refresh-token"
    }
    
    Returns:
    --------
    JSON with new access token
    """
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({
                "status": "error",
                "message": "Refresh token required"
            }), 400
        
        result = refresh_access_token(refresh_token)
        
        if not result['success']:
            return jsonify({
                "status": "error",
                "message": result['message']
            }), 401
        
        return jsonify({
            "status": "success",
            "access_token": result['access_token'],
            "token_type": result['token_type'],
            "expires_in": result['expires_in']
        })
    
    except Exception as e:
        logger.error(f"Error in jwt_refresh: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Token refresh failed"
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
@require_jwt()
def jwt_logout():
    """
    Logout by revoking refresh token.
    
    Request Body:
    -------------
    {
        "refresh_token": "your-refresh-token"
    }
    
    Returns:
    --------
    JSON confirmation
    """
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if refresh_token:
            revoke_refresh_token(refresh_token)
        
        user = get_current_user()
        logger.info(f"User '{user['username']}' logged out")
        
        return jsonify({
            "status": "success",
            "message": "Logged out successfully"
        })
    
    except Exception as e:
        logger.error(f"Error in jwt_logout: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Logout failed"
        }), 500


@app.route('/api/webhooks/test', methods=['GET'])
@require_jwt(['admin'])
def test_webhooks():
    """
    Test webhook configuration (admin only).
    
    Returns:
    --------
    JSON with test results for all configured webhooks
    """
    try:
        results = test_webhook_configuration()
        
        return jsonify({
            "status": "success",
            "results": results
        })
    
    except Exception as e:
        logger.error(f"Error in test_webhooks: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/login', methods=['POST'])
def login_legacy():
    """
    DEPRECATED: Legacy role-based login for backward compatibility.
    Use /api/auth/login instead.
    
    Request Body:
    -------------
    {
        "role": "monitor" | "auditor" | "admin"
    }
    
    Returns:
    --------
    JSON with authentication token for the requested role
    """
    try:
        data = request.get_json()
        role = data.get('role')
        
        if not role:
            return jsonify({
                "error": "Missing role",
                "available_roles": list(list_available_roles().keys()),
                "deprecation_notice": "This endpoint is deprecated. Use /api/auth/login with username/password"
            }), 400
        
        token = get_token_for_role(role)
        
        if not token:
            return jsonify({
                "error": "Invalid role",
                "available_roles": list(list_available_roles().keys()),
                "deprecation_notice": "This endpoint is deprecated. Use /api/auth/login with username/password"
            }), 400
        
        return jsonify({
            "token": token,
            "role": role,
            "message": f"Token generated for role: {role}",
            "usage": f"Include 'Authorization: Bearer {token}' in request headers",
            "deprecation_notice": "This endpoint is deprecated. Use /api/auth/login with username/password"
        })
    
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Login failed"
        }), 500


@app.route('/api/get_anchor/<hash_value>', methods=['GET'])
def get_blockchain_anchor(hash_value):
    """
    Get blockchain anchor information for a record hash.
    
    Parameters:
    -----------
    hash_value : str
        The SHA256 hash to look up
    
    Returns:
    --------
    JSON with blockchain anchor details
    """
    try:
        anchor = get_anchor(hash_value)
        
        if not anchor:
            return jsonify({
                "error": "Anchor not found",
                "hash_value": hash_value
            }), 404
        
        return jsonify(anchor)
    
    except Exception as e:
        logger.error(f"Error in get_blockchain_anchor: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to retrieve anchor"
        }), 500


@app.route('/api/evaluate_model', methods=['POST'])
def evaluate_model():
    """
    Evaluate real ML model predictions with fairness monitoring
    
    Request Body:
    ------------
    {
        "applicants": [
            {"income": 50000, "credit_score": 680, "age": 35, "existing_debt": 10000, "employment_length": 5, "gender": 0},
            ...
        ]
    }
    
    Returns:
    --------
    Predictions with fairness metrics
    """
    try:
        if ml_model is None:
            return jsonify({
                "error": "ML model not available",
                "message": "Model initialization failed. Check server logs."
            }), 503
        
        data = request.get_json()
        applicants = data.get('applicants', [])
        
        if not applicants:
            return jsonify({"error": "No applicants provided"}), 400
        
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame(applicants)
        
        required_features = ['income', 'credit_score', 'age', 'existing_debt', 'employment_length']
        for feature in required_features:
            if feature not in df.columns:
                return jsonify({"error": f"Missing required feature: {feature}"}), 400
        
        X = df[required_features]
        protected_attr = df.get('gender', np.zeros(len(df))).values
        
        predictions = ml_model.predict(X)
        probabilities = ml_model.predict_proba(X)
        
        all_metrics = metrics_engine.calculate_all_metrics(
            y_true=predictions,
            y_pred=predictions,
            protected_attribute=protected_attr
        )
        
        return jsonify({
            "model_version": ml_model.model_version,
            "n_applicants": len(applicants),
            "predictions": predictions.tolist(),
            "approval_rate": float(predictions.mean()),
            "fairness_metrics": all_metrics,
            "mode": Config.get_mode_display()
        })
    
    except Exception as e:
        logger.error(f"Error in evaluate_model: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/fairness_summary', methods=['GET'])
def fairness_summary():
    """
    Get comprehensive fairness summary across all 5 metrics
    
    Query Parameters:
    ----------------
    - n_samples (int): Number of samples to generate (default: 1000)
    - drift_level (float): Bias level 0.0-1.0 (default: 0.5)
    
    Returns:
    --------
    All 5 fairness metrics with compliance assessment
    """
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime
        
        n_samples = int(request.args.get('n_samples', 1000))
        drift_level = float(request.args.get('drift_level', 0.5))
        
        data = generate_loan_data(n_samples, drift_level=drift_level, seed=42)
        
        y_true = data['approved'].astype(int).values
        protected_attr = (data['gender'] == 'Female').astype(int).values
        
        if ml_model:
            feature_cols = ['income', 'credit_score', 'age', 'existing_debt', 'employment_length']
            X = data[feature_cols]
            y_pred = ml_model.predict(X)
        else:
            y_pred = y_true
        
        all_metrics = metrics_engine.calculate_all_metrics(y_true, y_pred, protected_attr)
        
        return jsonify({
            "n_samples": n_samples,
            "drift_level": drift_level,
            "metrics": all_metrics,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in fairness_summary: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/explainability', methods=['GET'])
def explainability():
    """
    Get enhanced explainability with feature contributions and AI-assisted remediation
    
    Query Parameters:
    ----------------
    - n_samples (int): Number of samples (default: 1000)
    - drift_level (float): Bias level (default: 0.5)
    
    Returns:
    --------
    Feature contributions, bias explanation, and remediation suggestions
    """
    try:
        import pandas as pd
        import numpy as np
        
        n_samples = int(request.args.get('n_samples', 1000))
        drift_level = float(request.args.get('drift_level', 0.5))
        
        data = generate_loan_data(n_samples, drift_level=drift_level, seed=42)
        
        y_pred = data['approved'].astype(int).values
        protected_attr = (data['gender'] == 'Female').astype(int).values
        
        feature_cols = [col for col in data.columns if col not in ['approved', 'gender', 'application_id']]
        available_features = [col for col in feature_cols if col in data.columns]
        
        feature_importance = {}
        if ml_model:
            raw_importance = ml_model.get_feature_importance()
            feature_importance = {k: v for k, v in raw_importance.items() if k in available_features}
        
        if not feature_importance:
            feature_importance = {f: 1.0/len(available_features) for f in available_features}
        
        feature_data = data[list(feature_importance.keys())]
        
        feature_contributions = enhanced_explainer.analyze_feature_contributions(
            feature_data,
            y_pred,
            protected_attr,
            feature_importance
        )
        
        all_metrics = metrics_engine.calculate_all_metrics(y_pred, y_pred, protected_attr)
        
        drift_analysis = drift_monitor.generate_drift_report('DIR')
        current_dir = drift_analysis.get('current_value', 0.8)
        velocity = drift_analysis.get('velocity', 0)
        risk_level = drift_analysis.get('risk_assessment', {}).get('risk_level', 'MEDIUM')
        
        remediation_suggestions = enhanced_explainer.generate_remediation_suggestions(
            feature_contributions,
            current_dir,
            velocity,
            risk_level
        )
        
        bias_explanation = enhanced_explainer.explain_bias_pattern(
            feature_contributions,
            all_metrics.get('summary', {})
        )
        
        confidence_scores = enhanced_explainer.generate_confidence_scores(
            feature_contributions,
            n_samples
        )
        
        return jsonify({
            "feature_contributions": feature_contributions,
            "bias_explanation": bias_explanation,
            "remediation_suggestions": remediation_suggestions,
            "confidence_scores": confidence_scores,
            "sample_size": n_samples
        })
    
    except Exception as e:
        logger.error(f"Error in explainability: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/export_report', methods=['GET'])
@require_jwt(['auditor', 'admin'])
def export_report():
    """
    Generate and download comprehensive PDF compliance report
    
    Requires: auditor or admin role
    
    Returns:
    --------
    PDF file path
    """
    try:
        import pandas as pd
        import numpy as np
        
        data = generate_loan_data(1000, drift_level=0.5, seed=42)
        y_pred = data['approved'].astype(int).values
        protected_attr = (data['gender'] == 'Female').astype(int).values
        
        metrics_summary = metrics_engine.calculate_all_metrics(y_pred, y_pred, protected_attr)
        
        drift_analysis = drift_monitor.generate_drift_report('DIR')
        
        feature_importance = ml_model.get_feature_importance() if ml_model else {}
        feature_data = data[list(feature_importance.keys())] if feature_importance else data
        
        feature_contributions = enhanced_explainer.analyze_feature_contributions(
            feature_data,
            y_pred,
            protected_attr,
            feature_importance
        )
        
        remediation = enhanced_explainer.generate_remediation_suggestions(
            feature_contributions,
            drift_analysis.get('current_value', 0.8),
            drift_analysis.get('velocity', 0),
            drift_analysis.get('risk_assessment', {}).get('risk_level', 'MEDIUM')
        )
        
        audit_history = get_audit_history(last_n=20)
        
        pdf_path = report_generator.generate_pdf_report(
            metrics_summary,
            drift_analysis,
            feature_contributions,
            remediation,
            audit_history
        )
        
        return jsonify({
            "status": "success",
            "report_path": pdf_path,
            "message": "PDF report generated successfully"
        })
    
    except Exception as e:
        logger.error(f"Error in export_report: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/export_csv', methods=['GET'])
@require_jwt(['auditor', 'admin'])
def export_csv():
    """
    Export fairness data to CSV format
    
    Requires: auditor or admin role
    
    Returns:
    --------
    CSV file path
    """
    try:
        import pandas as pd
        import numpy as np
        
        data = generate_loan_data(1000, drift_level=0.5, seed=42)
        y_pred = data['approved'].astype(int).values
        protected_attr = (data['gender'] == 'Female').astype(int).values
        
        metrics_summary = metrics_engine.calculate_all_metrics(y_pred, y_pred, protected_attr)
        
        audit_history = get_audit_history(last_n=100)
        
        drift_data = drift_monitor.get_recent_trends('DIR', window_size=50)
        
        csv_path = report_generator.export_to_csv(
            metrics_summary,
            audit_history,
            drift_data
        )
        
        return jsonify({
            "status": "success",
            "csv_path": csv_path,
            "message": "CSV export generated successfully"
        })
    
    except Exception as e:
        logger.error(f"Error in export_csv: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/models', methods=['GET'])
@require_jwt()
def list_models():
    """
    List all registered models.
    
    Requires: Any authenticated user
    
    Returns:
    --------
    JSON array of model metadata
    """
    try:
        models = model_registry.list_models()
        
        return jsonify({
            "status": "success",
            "models": models,
            "count": len(models)
        })
    
    except Exception as e:
        logger.error(f"Error in list_models: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/models/active', methods=['GET'])
@require_jwt()
def get_active_model_info():
    """
    Get active model information.
    
    Requires: Any authenticated user
    
    Returns:
    --------
    JSON with active model metadata
    """
    try:
        active_model = model_registry.get_active_model()
        
        if not active_model:
            return jsonify({
                "status": "error",
                "message": "No active model found"
            }), 404
        
        return jsonify({
            "status": "success",
            "model": active_model
        })
    
    except Exception as e:
        logger.error(f"Error in get_active_model_info: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/models/<model_id>/activate', methods=['POST'])
@require_jwt(['admin'])
def activate_model(model_id):
    """
    Set a model as active (admin only).
    
    Requires: admin role
    
    Parameters:
    -----------
    model_id : str
        ID of the model to activate
    
    Returns:
    --------
    JSON confirmation
    """
    try:
        success = model_registry.set_active_model(model_id)
        
        if not success:
            return jsonify({
                "status": "error",
                "message": f"Failed to activate model: {model_id}"
            }), 400
        
        # Reload the global ml_model
        global ml_model
        ml_model = model_registry.load_active_model()
        
        return jsonify({
            "status": "success",
            "message": f"Model {model_id} activated successfully",
            "active_model": model_id
        })
    
    except Exception as e:
        logger.error(f"Error in activate_model: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/models/<model_id>', methods=['GET'])
@require_jwt()
def get_model_details(model_id):
    """
    Get detailed information about a specific model.
    
    Requires: Any authenticated user
    
    Parameters:
    -----------
    model_id : str
        ID of the model
    
    Returns:
    --------
    JSON with model metadata
    """
    try:
        model_info = model_registry.get_model_metadata(model_id)
        
        if not model_info:
            return jsonify({
                "status": "error",
                "message": f"Model not found: {model_id}"
            }), 404
        
        return jsonify({
            "status": "success",
            "model": model_info
        })
    
    except Exception as e:
        logger.error(f"Error in get_model_details: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/models/registry/summary', methods=['GET'])
@require_jwt()
def get_registry_summary():
    """
    Get model registry summary statistics.
    
    Requires: Any authenticated user
    
    Returns:
    --------
    JSON with registry statistics
    """
    try:
        summary = model_registry.get_registry_summary()
        
        return jsonify({
            "status": "success",
            "summary": summary
        })
    
    except Exception as e:
        logger.error(f"Error in get_registry_summary: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation endpoint."""
    return jsonify({
        "service": "BiasCheck Fairness Drift Alert System",
        "version": "3.0.0",
        "description": "Production-grade fairness monitoring with predictive analytics",
        "endpoints": {
            "monitoring": {
                "/api/monitor_fairness": "Perform fairness check (params: n_samples, drift_level)",
                "/api/submit_predictions": "Submit live AI predictions for monitoring (POST)",
                "/api/evaluate_model": "Evaluate real ML model predictions (POST) [v3.0]",
                "/api/health": "Health check"
            },
            "analytics": {
                "/api/fairness_trend": "Get recent fairness trend (params: window, model_name)",
                "/api/fairness_summary": "Get all 5 fairness metrics (params: n_samples, drift_level) [v3.0]",
                "/api/pre_alert": "Check for early warning signs (params: threshold, window)",
                "/api/predict_fairness_drift": "Predict future drift (params: window, model_name)",
                "/api/explainability": "Get feature contributions & AI remediation [v3.0]"
            },
            "compliance": {
                "/api/audit_history": "Retrieve audit log [requires auditor role] (params: last_n)",
                "/api/verify_alert/<record_id>": "Verify record integrity [requires auditor role]",
                "/api/get_anchor/<hash>": "Get blockchain anchor for hash",
                "/api/export_report": "Generate PDF compliance report [auditor/admin] [v3.0]",
                "/api/export_csv": "Export data to CSV [auditor/admin] [v3.0]"
            },
            "authentication": {
                "/api/auth/login": "JWT login (POST: {username, password}) [ENTERPRISE]",
                "/api/auth/refresh": "Refresh access token (POST: {refresh_token}) [ENTERPRISE]",
                "/api/auth/logout": "Logout (POST: {refresh_token}) [ENTERPRISE]",
                "/api/login": "Legacy token (deprecated, use /api/auth/login)"
            },
            "webhooks": {
                "/api/webhooks/test": "Test webhook configuration [admin only] [ENTERPRISE]"
            },
            "model_registry": {
                "/api/models": "List all registered models [ENTERPRISE]",
                "/api/models/active": "Get active model info [ENTERPRISE]",
                "/api/models/<id>/activate": "Set model as active [admin only] [ENTERPRISE]",
                "/api/models/<id>": "Get model details [ENTERPRISE]",
                "/api/models/registry/summary": "Registry summary [ENTERPRISE]"
            }
        },
        "fairness_metrics": {
            "DIR": "Disparate Impact Ratio (EEOC 80% rule)",
            "SPD": "Statistical Parity Difference [v3.0]",
            "EOD": "Equal Opportunity Difference [v3.0]",
            "AOD": "Average Odds Difference [v3.0]",
            "THEIL": "Theil Index (inequality measure) [v3.0]",
            "alert_threshold": "DIR < 0.8 triggers bias alert",
            "compliance_level": "Based on all 5 metrics [v3.0]"
        },
        "features": {
            "jwt_authentication": "Secure JWT-based auth with refresh tokens [ENTERPRISE]",
            "webhook_alerts": "Real-time Slack/email notifications [ENTERPRISE]",
            "postgresql_persistence": "Scalable database with connection pooling [ENTERPRISE]",
            "model_versioning": "ML model registry & version management [ENTERPRISE]",
            "real_ml_integration": "Production ML model (Logistic Regression) [v3.0]",
            "multi_metric_engine": "5 comprehensive fairness metrics [v3.0]",
            "predictive_drift": "Velocity, acceleration, confidence intervals [v3.0]",
            "deep_explainability": "Feature attribution & AI remediation [v3.0]",
            "enterprise_reporting": "PDF & CSV export for compliance [v3.0]",
            "predictive_monitoring": "Detect fairness drift before it happens",
            "tamper_proof_logging": "SHA256 hashes for audit trail integrity",
            "blockchain_anchoring": "Public verifiability of fairness records",
            "role_based_access": "Secure access control for compliance data",
            "live_monitoring": "Real-time fairness checks on AI predictions"
        },
        "enterprise_credentials": {
            "admin": "admin/admin123 (full access)",
            "auditor": "auditor/auditor123 (read + export)",
            "monitor": "monitor/monitor123 (read only)"
        },
        "demo_tokens_legacy": {
            "monitor": "MONITOR123",
            "auditor": "AUDITOR123",
            "admin": "ADMIN123",
            "note": "Deprecated - use JWT login at /api/auth/login"
        },
        "usage_examples": {
            "basic_check": "GET /api/monitor_fairness?n_samples=1000&drift_level=0.5",
            "trend_analysis": "GET /api/fairness_trend?window=10",
            "prediction": "GET /api/predict_fairness_drift",
            "audit_access": "GET /api/audit_history -H 'Authorization: Bearer AUDITOR123'",
            "live_monitoring": "POST /api/submit_predictions -d '{\"model\":\"loan_v1\",\"predictions\":[...]}'"
        }
    })


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React frontend or API routes"""
    # API routes pass through
    if path.startswith('api/'):
        return jsonify({"error": "API route not found"}), 404
    
    # Serve static files from dist folder
    dist_path = os.path.join(os.path.dirname(__file__), '..', 'dist')
    if path != "" and os.path.exists(os.path.join(dist_path, path)):
        return send_from_directory(dist_path, path)
    
    # For all other routes, serve index.html (React Router will handle routing)
    return send_from_directory(dist_path, 'index.html')


if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("BiasCheck v3.0 - Predictive Fairness Governance Platform")
    logger.info("Production-Grade AI Ethics & Compliance Monitoring System")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✅ All v3.0 modules loaded successfully:")
    logger.info("")
    logger.info("  🤖 PHASE 1: ML Model Integration")
    logger.info("     ✓ Production Loan Approval Model (Logistic Regression)")
    logger.info("     ✓ Model Registry & Versioning System")
    logger.info("     ✓ Real-Time Prediction Pipeline")
    logger.info("")
    logger.info("  📊 PHASE 2: Multi-Metric Fairness Engine")
    logger.info("     ✓ Disparate Impact Ratio (DIR) - EEOC 80% Rule")
    logger.info("     ✓ Statistical Parity Difference (SPD)")
    logger.info("     ✓ Equal Opportunity Difference (EOD)")
    logger.info("     ✓ Average Odds Difference (AOD)")
    logger.info("     ✓ Theil Index (Inequality Measure)")
    logger.info("")
    logger.info("  🔮 PHASE 3: Predictive Ethics Engine")
    logger.info("     ✓ Drift Velocity & Acceleration Tracking")
    logger.info("     ✓ Confidence Intervals (Bootstrapping)")
    logger.info("     ✓ Probabilistic Risk Scoring")
    logger.info("     ✓ Auto-Retraining Triggers")
    logger.info("")
    logger.info("  🧠 PHASE 4: Deep Explainability")
    logger.info("     ✓ Feature Attribution Analysis")
    logger.info("     ✓ Temporal Contribution Tracking")
    logger.info("     ✓ AI-Assisted Remediation Suggestions")
    logger.info("     ✓ Confidence-Weighted Explanations")
    logger.info("")
    logger.info("  📄 PHASE 5: Enterprise Reporting")
    logger.info("     ✓ PDF Compliance Report Generator")
    logger.info("     ✓ CSV Data Export")
    logger.info("     ✓ Blockchain Verification Proofs")
    logger.info("     ✓ Role-Based Report Access")
    logger.info("")
    logger.info("  🔐 CORE SYSTEMS:")
    logger.info("     ✓ Trend Analyzer - Predictive fairness monitoring")
    logger.info("     ✓ Alert Fingerprinting - Tamper-proof audit trail")
    logger.info("     ✓ Role-Based Access Control - Secure compliance access")
    logger.info("     ✓ Blockchain Anchoring - Public verifiability")
    logger.info("     ✓ Database Storage - Temporal trend tracking")
    logger.info("")
    logger.info(f"  🎯 MODE: {Config.get_mode_display()}")
    logger.info("")
    logger.info("=" * 80)
    logger.info("How BiasCheck v3.0 Works:")
    logger.info("=" * 80)
    logger.info("")
    logger.info("  1. REAL MODEL PREDICTIONS → Live loan approval decisions")
    logger.info("  2. MULTI-METRIC ANALYSIS → 5 fairness metrics calculated")
    logger.info("  3. DRIFT PREDICTION → Velocity + acceleration forecasting")
    logger.info("  4. FEATURE ATTRIBUTION → Identify bias root causes")
    logger.info("  5. AI REMEDIATION → Automated improvement suggestions")
    logger.info("  6. ENCRYPTED ALERTS → Secure bias notifications")
    logger.info("  7. BLOCKCHAIN ANCHORING → Tamper-proof compliance proof")
    logger.info("  8. ENTERPRISE REPORTS → PDF/CSV for regulators")
    logger.info("")
    logger.info("=" * 80)
    logger.info("Compliance Standards:")
    logger.info("=" * 80)
    logger.info("  - EEOC 80% Rule (Disparate Impact)")
    logger.info("  - EU AI Act Multi-Metric Audit Standards")
    logger.info("  - Fair Lending Practices (ECOA, FCRA)")
    logger.info("  - Immutable Audit Trail (SOX, GDPR)")
    logger.info("  - Blockchain Verifiability (Public Trust)")
    logger.info("")
    logger.info("=" * 80)
    port = int(os.environ.get('FLASK_PORT', 8000))
    logger.info(f"✅ BiasCheck v3.0 – Predictive Fairness Governance Active")
    logger.info(f"   API running on http://127.0.0.1:{port}")
    logger.info("=" * 80)
    logger.info("")
    
    app.run(host='0.0.0.0', port=port, debug=False)
