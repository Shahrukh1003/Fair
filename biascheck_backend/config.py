"""
BiasCheck Configuration Module
Manages dual-mode operation (demo vs production) and system settings
"""

import os
from enum import Enum

class Mode(Enum):
    """Operating modes for BiasCheck"""
    DEMO = "demo"
    PRODUCTION = "production"

class Config:
    """BiasCheck Configuration"""
    
    # Operating mode
    MODE = Mode(os.getenv("BIASCHECK_MODE", "demo"))
    
    # Model settings
    MODEL_PATH = os.getenv("MODEL_PATH", "biascheck_backend/models")
    MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")
    
    # Fairness thresholds
    DIR_THRESHOLD = float(os.getenv("DIR_THRESHOLD", "0.8"))
    SPD_THRESHOLD = float(os.getenv("SPD_THRESHOLD", "0.1"))
    EOD_THRESHOLD = float(os.getenv("EOD_THRESHOLD", "0.1"))
    AOD_THRESHOLD = float(os.getenv("AOD_THRESHOLD", "0.1"))
    THEIL_THRESHOLD = float(os.getenv("THEIL_THRESHOLD", "0.15"))
    
    # Drift prediction settings
    DRIFT_WINDOW_SIZE = int(os.getenv("DRIFT_WINDOW_SIZE", "10"))
    DRIFT_VELOCITY_THRESHOLD = float(os.getenv("DRIFT_VELOCITY_THRESHOLD", "-0.01"))
    DRIFT_ACCELERATION_THRESHOLD = float(os.getenv("DRIFT_ACCELERATION_THRESHOLD", "-0.005"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    
    # Alert settings
    PRE_ALERT_ENABLED = os.getenv("PRE_ALERT_ENABLED", "true").lower() == "true"
    AUTO_RETRAIN_TRIGGER = os.getenv("AUTO_RETRAIN_TRIGGER", "true").lower() == "true"
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "biascheck_backend/biascheck.db")
    
    # Security
    ENCRYPTION_KEY_PATH = os.getenv("ENCRYPTION_KEY_PATH", "biascheck_backend/fernet.key")
    
    # Reporting
    REPORT_OUTPUT_PATH = os.getenv("REPORT_OUTPUT_PATH", "biascheck_backend/reports")
    
    @classmethod
    def is_demo_mode(cls):
        """Check if running in demo mode"""
        return cls.MODE == Mode.DEMO
    
    @classmethod
    def is_production_mode(cls):
        """Check if running in production mode"""
        return cls.MODE == Mode.PRODUCTION
    
    @classmethod
    def get_mode_display(cls):
        """Get human-readable mode name"""
        return "Demo Mode" if cls.is_demo_mode() else "Production Mode"
