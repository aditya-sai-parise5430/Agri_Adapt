import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
RISK_MODEL_PATH = os.path.join(MODEL_DIR, 'risk_model.pkl')

class RiskPredictor:
    def __init__(self):
        self.model = self._load_model()
        
    def _load_model(self):
        try:
            return joblib.load(RISK_MODEL_PATH)
        except Exception as e:
            print(f"Error loading risk model: {e}")
            return None

    def predict(self, input_data: dict) -> tuple:
        """
        Takes raw climate features and outputs binary risk + probability.
        """
        if not self.model:
            raise ValueError("Risk model failed to load.")
            
        # The model expects exactly these features
        feature_order = ['rainfall', 'temperature', 'humidity', 'district', 'crop_type']
        
        df = pd.DataFrame([input_data])
        
        # Ensure correct column ordering
        df_selected = df[feature_order]
        
        pred = self.model.predict(df_selected)[0]
        prob = self.model.predict_proba(df_selected)[0, 1] if hasattr(self.model, 'predict_proba') else float(pred)
        
        return int(pred), float(prob)
