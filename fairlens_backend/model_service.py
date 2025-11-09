"""
ML Model Service for BiasCheck
Handles model training, prediction, and fairness evaluation
"""

import numpy as np
import pandas as pd
import joblib
import logging
from datetime import datetime
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from typing import Dict, List, Tuple, Any

from config import Config

logger = logging.getLogger(__name__)

class LoanApprovalModel:
    """
    Production-ready loan approval model with fairness tracking
    """
    
    def __init__(self, model_version: str = "v1.0"):
        self.model_version = model_version
        self.model = None
        self.feature_names = [
            'income', 'credit_score', 'age', 
            'existing_debt', 'employment_length'
        ]
        self.model_path = Path(Config.MODEL_PATH)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.training_metadata = {}
    
    def train(self, X: pd.DataFrame, y: np.ndarray) -> Dict[str, Any]:
        """
        Train logistic regression model for loan approval
        
        Args:
            X: Feature dataframe
            y: Target labels (0=rejected, 1=approved)
        
        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training loan approval model {self.model_version}...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train logistic regression
        self.model = LogisticRegression(
            random_state=42,
            max_iter=1000,
            class_weight='balanced'  # Handle class imbalance
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        metrics = {
            'model_version': self.model_version,
            'training_date': datetime.now().isoformat(),
            'train_accuracy': float(accuracy_score(y_train, y_pred_train)),
            'test_accuracy': float(accuracy_score(y_test, y_pred_test)),
            'precision': float(precision_score(y_test, y_pred_test)),
            'recall': float(recall_score(y_test, y_pred_test)),
            'f1_score': float(f1_score(y_test, y_pred_test)),
            'n_samples_train': len(X_train),
            'n_samples_test': len(X_test),
            'feature_importance': dict(zip(
                self.feature_names,
                [float(coef) for coef in self.model.coef_[0]]
            ))
        }
        
        self.training_metadata = metrics
        logger.info(f"✅ Model trained: Accuracy={metrics['test_accuracy']:.3f}, F1={metrics['f1_score']:.3f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on new data
        
        Args:
            X: Feature dataframe
        
        Returns:
            Predictions array (0=rejected, 1=approved)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities
        
        Args:
            X: Feature dataframe
        
        Returns:
            Probability array for each class
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict_proba(X)
    
    def save(self, filename: str = None) -> str:
        """
        Save model to disk
        
        Args:
            filename: Optional custom filename
        
        Returns:
            Path to saved model
        """
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")
        
        if filename is None:
            filename = f"loan_model_{self.model_version}.pkl"
        
        filepath = self.model_path / filename
        
        model_data = {
            'model': self.model,
            'version': self.model_version,
            'feature_names': self.feature_names,
            'metadata': self.training_metadata
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"✅ Model saved to {filepath}")
        
        return str(filepath)
    
    def load(self, filename: str = None) -> Dict[str, Any]:
        """
        Load model from disk
        
        Args:
            filename: Optional custom filename
        
        Returns:
            Model metadata
        """
        if filename is None:
            filename = f"loan_model_{self.model_version}.pkl"
        
        filepath = self.model_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model not found: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.model_version = model_data['version']
        self.feature_names = model_data['feature_names']
        self.training_metadata = model_data['metadata']
        
        logger.info(f"✅ Model loaded from {filepath}")
        
        return self.training_metadata
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # For logistic regression, use absolute coefficient values
        importance = np.abs(self.model.coef_[0])
        
        # Normalize to sum to 1
        importance_normalized = importance / importance.sum()
        
        return dict(zip(
            self.feature_names,
            [float(score) for score in importance_normalized]
        ))

def create_and_train_default_model() -> LoanApprovalModel:
    """
    Create and train default loan approval model with synthetic data
    
    Returns:
        Trained LoanApprovalModel instance
    """
    logger.info("Creating default loan approval model with synthetic training data...")
    
    # Generate synthetic training data
    np.random.seed(42)
    n_samples = 5000
    
    # Features
    income = np.random.normal(60000, 20000, n_samples).clip(20000, 150000)
    credit_score = np.random.normal(680, 60, n_samples).clip(300, 850)
    age = np.random.normal(40, 12, n_samples).clip(18, 80)
    existing_debt = np.random.normal(15000, 10000, n_samples).clip(0, 100000)
    employment_length = np.random.normal(5, 3, n_samples).clip(0, 40)
    
    # Target: Approval based on creditworthiness
    approval_score = (
        0.0003 * income +
        0.01 * credit_score +
        0.5 * age +
        -0.0005 * existing_debt +
        1.0 * employment_length +
        np.random.normal(0, 10, n_samples)
    )
    
    # Convert to binary (approved/rejected)
    threshold = np.median(approval_score)
    approved = (approval_score > threshold).astype(int)
    
    # Create dataframe
    X = pd.DataFrame({
        'income': income,
        'credit_score': credit_score,
        'age': age,
        'existing_debt': existing_debt,
        'employment_length': employment_length
    })
    
    # Train model
    model = LoanApprovalModel(model_version="v1.0")
    metrics = model.train(X, approved)
    
    # Save model
    model.save()
    
    logger.info(f"✅ Default model created and saved")
    logger.info(f"   Accuracy: {metrics['test_accuracy']:.3f}")
    logger.info(f"   F1 Score: {metrics['f1_score']:.3f}")
    
    return model
