"""
Model Registry for FairLens
Manages model versioning, storage, and metadata tracking
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import joblib

from config import Config
from model_service import LoanApprovalModel

logger = logging.getLogger(__name__)

class ModelRegistry:
    """
    Centralized registry for managing ML models
    """
    
    def __init__(self, registry_path: str = None):
        if registry_path is None:
            registry_path = Path(Config.MODEL_PATH) / "registry.json"
        
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from disk"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {'models': [], 'active_model': None}
    
    def _save_registry(self):
        """Save registry to disk"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(
        self, 
        model: LoanApprovalModel, 
        filepath: str,
        description: str = None,
        tags: List[str] = None
    ) -> str:
        """
        Register a new model version
        
        Args:
            model: Trained model instance
            filepath: Path where model is saved
            description: Optional model description
            tags: Optional tags for categorization
        
        Returns:
            Model ID
        """
        model_id = f"model_{model.model_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        model_entry = {
            'model_id': model_id,
            'version': model.model_version,
            'filepath': str(filepath),
            'registered_at': datetime.now().isoformat(),
            'description': description or f"Loan approval model {model.model_version}",
            'tags': tags or [],
            'metadata': model.training_metadata,
            'feature_names': model.feature_names,
            'status': 'active'
        }
        
        self.registry['models'].append(model_entry)
        
        # Set as active if it's the first model or if specified
        if self.registry['active_model'] is None:
            self.registry['active_model'] = model_id
        
        self._save_registry()
        
        logger.info(f"✅ Model registered: {model_id}")
        
        return model_id
    
    def get_active_model(self) -> Optional[Dict[str, Any]]:
        """Get the currently active model metadata"""
        active_id = self.registry.get('active_model')
        if active_id is None:
            return None
        
        for model in self.registry['models']:
            if model['model_id'] == active_id:
                return model
        
        return None
    
    def load_active_model(self) -> Optional[LoanApprovalModel]:
        """
        Load the active model
        
        Returns:
            Loaded LoanApprovalModel instance or None
        """
        active_model_meta = self.get_active_model()
        
        if active_model_meta is None:
            logger.warning("No active model found in registry")
            return None
        
        try:
            model = LoanApprovalModel(model_version=active_model_meta['version'])
            model.load(filename=Path(active_model_meta['filepath']).name)
            logger.info(f"✅ Loaded active model: {active_model_meta['model_id']}")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None
    
    def set_active_model(self, model_id: str) -> bool:
        """
        Set a specific model as active
        
        Args:
            model_id: ID of the model to activate
        
        Returns:
            True if successful, False otherwise
        """
        for model in self.registry['models']:
            if model['model_id'] == model_id:
                self.registry['active_model'] = model_id
                self._save_registry()
                logger.info(f"✅ Active model changed to: {model_id}")
                return True
        
        logger.error(f"Model not found: {model_id}")
        return False
    
    def list_models(self, status: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered models with optional filtering
        
        Args:
            status: Filter by status (active, archived, etc.)
            tags: Filter by tags
        
        Returns:
            List of model metadata dictionaries
        """
        models = self.registry['models']
        
        if status:
            models = [m for m in models if m.get('status') == status]
        
        if tags:
            models = [m for m in models if any(tag in m.get('tags', []) for tag in tags)]
        
        return models
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific model
        
        Args:
            model_id: Model ID
        
        Returns:
            Model metadata dictionary or None
        """
        for model in self.registry['models']:
            if model['model_id'] == model_id:
                return model
        
        return None
    
    def archive_model(self, model_id: str) -> bool:
        """
        Archive a model (mark as inactive)
        
        Args:
            model_id: Model ID to archive
        
        Returns:
            True if successful, False otherwise
        """
        for model in self.registry['models']:
            if model['model_id'] == model_id:
                model['status'] = 'archived'
                model['archived_at'] = datetime.now().isoformat()
                self._save_registry()
                logger.info(f"✅ Model archived: {model_id}")
                return True
        
        return False
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the registry
        
        Returns:
            Summary dictionary
        """
        total_models = len(self.registry['models'])
        active_models = len([m for m in self.registry['models'] if m.get('status') == 'active'])
        archived_models = total_models - active_models
        
        return {
            'total_models': total_models,
            'active_models': active_models,
            'archived_models': archived_models,
            'current_active': self.registry.get('active_model'),
            'registry_path': str(self.registry_path)
        }

# Global registry instance
_registry = None

def get_registry() -> ModelRegistry:
    """Get or create global model registry instance"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
