import os
import joblib
import pandas as pd

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
        """
        Takes raw features, evaluates with the pipeline, 
        and predictions target price.
        """
        if not self.model:
            raise ValueError("Price model failed to load.")
            
        # The model expects a Pandas DataFrame structure matching the training features
        # Features map defined strictly in backend.services.train_models
        feature_order = [
            'rainfall', 'temperature', 'humidity', 
            'price_lag_1', 'price_lag_7', 'price_lag_14', 
            'price_rolling_mean_7', 'rainfall_lag_1', 'temp_lag_1',
            'district', 'crop_type'
        ]
        
        # We fill missing lags/aggregates dynamically with sensible defaults based on historical or simple heuristics
        # if not supplied via request context
        df = pd.DataFrame([input_data])
        
        for col in feature_order:
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                # Simple fallback: numeric ones fallback to 0 or arbitrary safe mean, categorical to 'Unknown'
                if col in ['price_lag_1', 'price_lag_7', 'price_lag_14', 'price_rolling_mean_7']:
                    df[col] = 1500.0  # Safe base fallback for price metrics visually
                elif col in ['rainfall_lag_1', 'temp_lag_1']:
                    df[col] = df['rainfall'].iloc[0] if 'rainfall' in col else df['temperature'].iloc[0]
                elif df[col].dtype == object:
                    df[col] = 'Unknown'
        
        # Isolate exactly the ordered features
        df_selected = df[feature_order]
        
        pred = self.model.predict(df_selected)[0]
        return float(pred)
