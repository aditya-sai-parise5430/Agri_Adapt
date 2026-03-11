import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
PRICE_MODEL_PATH = os.path.join(MODEL_DIR, 'price_model.pkl')

class PricePredictor:
    def __init__(self):
        self.model = self._load_model()
        self.crop_seeds = {
            'Wheat': 2100.0,
            'Rice': 2300.0,
            'Cotton': 6200.0,
            'Soybean': 4500.0,
            'Maize': 1900.0,
            'Unknown': 1500.0
        }
        
    def _load_model(self):
        try:
            return joblib.load(PRICE_MODEL_PATH)
        except Exception as e:
            print(f"[PricePredictor] Model not found, using seed fallback: {e}")
            return None

    def predict(self, input_data: dict) -> float:
        crop = input_data.get('crop_type', 'Unknown')
        base_seed = self.crop_seeds.get(crop, 1500.0)

        # Graceful fallback when model is unavailable
        if self.model is None:
            return base_seed
            
        feature_order = [
            'rainfall', 'temperature', 'humidity', 
            'price_lag_1', 'price_lag_7', 'price_lag_14', 
            'price_rolling_mean_7', 'rainfall_lag_1', 'temp_lag_1',
            'district', 'crop_type'
        ]
        
        # Build a clean row dict with all features
        row = {col: input_data.get(col) for col in feature_order}
        
        # Fill missing values with sensible defaults (B1/B3 fix)
        for col in feature_order:
            val = row.get(col)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                if col in ('price_lag_1', 'price_lag_7', 'price_lag_14', 'price_rolling_mean_7'):
                    row[col] = base_seed
                elif col == 'rainfall_lag_1':
                    row[col] = input_data.get('rainfall', 2.0)
                elif col == 'temp_lag_1':
                    row[col] = input_data.get('temperature', 25.0)
                elif col in ('district', 'crop_type'):
                    row[col] = 'Unknown'
                else:
                    row[col] = 0.0

        df = pd.DataFrame([row])[feature_order]
        
        try:
            prediction = float(self.model.predict(df)[0])
            # Clamp to realistic range per paper methodology
            return max(base_seed * 0.7, min(prediction, base_seed * 1.3))
        except Exception as e:
            print(f"[PricePredictor] Prediction error, using seed: {e}")
            return base_seed
