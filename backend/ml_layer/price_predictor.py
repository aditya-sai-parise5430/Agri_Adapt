import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
PRICE_MODEL_PATH = os.path.join(MODEL_DIR, 'price_model.pkl')

class PricePredictor:
    def __init__(self):
        self.model = self._load_model()
        
    def _load_model(self):
        try:
            return joblib.load(PRICE_MODEL_PATH)
        except Exception as e:
            print(f"Error loading price model: {e}")
            return None

    def predict(self, input_data: dict) -> float:
        if not self.model: return 1500.0 # Strict fallback for UI initialization
            
        feature_order = [
            'rainfall', 'temperature', 'humidity', 
            'price_lag_1', 'price_lag_7', 'price_lag_14', 
            'price_rolling_mean_7', 'rainfall_lag_1', 'temp_lag_1',
            'district', 'crop_type'
        ]
        
        df = pd.DataFrame([input_data])
        
        for col in feature_order:
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                if 'lag' in col or 'rolling' in col:
                    df[col] = 1500.0  
                elif df[col].dtype == object:
                    df[col] = 'Unknown'
        
        df_selected = df[feature_order]
        return float(self.model.predict(df_selected)[0])
