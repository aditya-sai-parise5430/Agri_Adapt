import os
import joblib
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
RISK_MODEL_PATH = os.path.join(MODEL_DIR, 'risk_model.pkl')

class RiskPredictor:
    def __init__(self):
        self.model = self._load_model()
        
    def _load_model(self):
        try:
            return joblib.load(RISK_MODEL_PATH)
        except Exception as e:
            print(f"[RiskPredictor] Model not found, using fallback: {e}")
            return None

    def predict(self, input_data: dict) -> tuple:
        # B4: Graceful fallback when model is unavailable
        if self.model is None:
            return 0, 0.05

        feature_order = ['rainfall', 'temperature', 'humidity', 'district', 'crop_type']
        
        # Build row with safe defaults for missing fields
        row = {
            'rainfall':    input_data.get('rainfall', 2.0),
            'temperature': input_data.get('temperature', 25.0),
            'humidity':    float(input_data.get('humidity', 60.0)),
            'district':    input_data.get('district', 'Pune'),
            'crop_type':   input_data.get('crop_type', 'Wheat'),
        }
        
        df = pd.DataFrame([row])[feature_order]
        
        try:
            pred = self.model.predict(df)[0]
            prob = self.model.predict_proba(df)[0, 1] if hasattr(self.model, 'predict_proba') else float(pred)
            return int(pred), float(prob)
        except Exception as e:
            print(f"[RiskPredictor] Prediction error, using fallback: {e}")
            return 0, 0.05
