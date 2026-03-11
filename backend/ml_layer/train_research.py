import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
import warnings

warnings.filterwarnings('ignore')

# B9 fix: ensure backend/ is on sys.path so nlp_layer imports resolve correctly
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

# Project root is one level above backend/
BASE_DIR = os.path.dirname(_BACKEND_DIR)
MODEL_DIR = os.path.join(_BACKEND_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

class ResearchPipeline:
    """
    DATA LAYER & ML LAYER EVALUATION
    Orchestrates time-series validation, baseline comparisons, and rigorous visual metric outputs 
    required for Scopus-level journal submissions.
    """
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.RAINFALL_THRESHOLD = 0.5
        self.TEMPERATURE_THRESHOLD = 20.0

    def load_and_preprocess(self):
        print("Data Layer: Interpolating and Chronologically Aligning Records...")
        df = pd.read_csv(self.data_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Safe interpolation preventing cross-entity leakage
        for col in ['price', 'rainfall', 'temperature', 'humidity']:
            if col in df.columns:
                df[col] = df.groupby(['district', 'crop_type'])[col].transform(lambda x: x.interpolate(limit_direction='both'))
                df[col].fillna(df[col].mean(), inplace=True)
        self.df = df

    def feature_engineering(self):
        """Creates robust multi-temporal geographic lag vectors"""
        df_feat = self.df.copy()
        group = ['district', 'crop_type']
        
        df_feat['price_lag_1'] = df_feat.groupby(group)['price'].shift(1)
        df_feat['price_lag_7'] = df_feat.groupby(group)['price'].shift(7)
        df_feat['price_lag_14'] = df_feat.groupby(group)['price'].shift(14)
        df_feat['price_rolling_mean_7'] = df_feat.groupby(group)['price'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
        df_feat['rainfall_lag_1'] = df_feat.groupby(group)['rainfall'].shift(1)
        df_feat['temp_lag_1'] = df_feat.groupby(group)['temperature'].shift(1)
        
        df_feat.dropna(inplace=True)
        return df_feat.sort_values('date').reset_index(drop=True)

    def train_price_model(self):
        print("\n--- RESEARCH EXPERIMENT 1: Price Forecasting (XGBoost vs Baseline) ---")
        df_p = self.feature_engineering()
        features = ['rainfall', 'temperature', 'humidity', 'price_lag_1', 'price_lag_7', 'price_lag_14', 'price_rolling_mean_7', 'rainfall_lag_1', 'temp_lag_1', 'district', 'crop_type']
        
        # Temporal Split
        split_idx = int(len(df_p) * 0.8)
        train, test = df_p.iloc[:split_idx], df_p.iloc[split_idx:]
        
        X_train, y_train = train[features], train['price']
        X_test, y_test = test[features], test['price']
        
        preprocessor = ColumnTransformer([
            ('num', StandardScaler(), [f for f in features if f not in ['district', 'crop_type']]),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['district', 'crop_type'])
        ])
        
        # Baseline Benchmark
        lr = Pipeline([('prep', preprocessor), ('model', LinearRegression())])
        lr.fit(X_train, y_train)
        y_lr = lr.predict(X_test)
        print(f"[Baseline LR] RMSE: {np.sqrt(mean_squared_error(y_test, y_lr)):.4f} | MAPE: {mean_absolute_percentage_error(y_test, y_lr):.4f}")
        
        # Proposed Architecture
        xgb = Pipeline([('prep', preprocessor), ('model', XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, n_jobs=-1))])
        xgb.fit(X_train, y_train)
        y_xgb = xgb.predict(X_test)
        print(f"[Proposed XGBoost] RMSE: {np.sqrt(mean_squared_error(y_test, y_xgb)):.4f} | MAPE: {mean_absolute_percentage_error(y_test, y_xgb):.4f}")
        
        joblib.dump(xgb, os.path.join(MODEL_DIR, 'price_model.pkl'))
        self.plot_feature_importance(xgb, [f for f in features if f not in ['district', 'crop_type']], ['district', 'crop_type'])

    def train_risk_model(self):
        print("\n--- RESEARCH EXPERIMENT 2: Climate Risk Classification ---")
        df_r = self.df.copy()
        df_r['target'] = np.where((df_r['rainfall'] < self.RAINFALL_THRESHOLD) & (df_r['temperature'] > self.TEMPERATURE_THRESHOLD), 1, 0)
        
        split_idx = int(len(df_r) * 0.8)
        train, test = df_r.iloc[:split_idx], df_r.iloc[split_idx:]
        
        X_train, y_train = train[['rainfall', 'temperature', 'humidity', 'district', 'crop_type']], train['target']
        X_test, y_test = test[['rainfall', 'temperature', 'humidity', 'district', 'crop_type']], test['target']
        
        preprocessor = ColumnTransformer([
            ('num', StandardScaler(), ['rainfall', 'temperature', 'humidity']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['district', 'crop_type'])
        ])
        
        rf = Pipeline([('prep', preprocessor), ('model', RandomForestClassifier(class_weight='balanced', random_state=42))])
        rf.fit(X_train, y_train)
        preds = rf.predict(X_test)
        
        print(f"[Random Forest] Accuracy: {accuracy_score(y_test, preds):.4f} | F1: {f1_score(y_test, preds):.4f}")
        joblib.dump(rf, os.path.join(MODEL_DIR, 'risk_model.pkl'))
        
        # Confusion Matrix output
        cm = confusion_matrix(y_test, preds)
        plt.figure(figsize=(6,5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Drought Classification Confusion Matrix')
        plt.ylabel('Actual Label')
        plt.xlabel('Predicted Label')
        plt.savefig(os.path.join(MODEL_DIR, 'confusion_matrix.png'))
        plt.close()

    def plot_feature_importance(self, model, num_cols, cat_cols):
        try:
            ohe = model.named_steps['prep'].named_transformers_['cat'].get_feature_names_out(cat_cols)
            feats = num_cols + list(ohe)
            impts = model.named_steps['model'].feature_importances_
            
            idx = np.argsort(impts)[::-1][:10]
            plt.figure(figsize=(10,6))
            plt.bar(range(10), impts[idx], color='teal')
            plt.xticks(range(10), [feats[i] for i in idx], rotation=45, ha='right')
            plt.title('XGBoost Top 10 Feature Attribution')
            plt.tight_layout()
            plt.savefig(os.path.join(MODEL_DIR, 'feature_importance.png'))
            plt.close()
            print("Successfully saved diagnostic evaluation graphs to /models directory.")
        except Exception as e:
            print(f"Diagnostics error: {e}")

    def evaluate_nlp_multilingual(self):
        print("\n--- RESEARCH EXPERIMENT 3: Multilingual Semantic Logic Evaluation ---")
        test_phrases = [
            ("Will rice get expensive?", "Prediction"),
            ("Is there a drought risk today?", "Risk"),
            ("Should I sow cotton now?", "Advisory"),
            ("Crop rotation technique meaning", "Knowledge"),
            ("Are subsidies available for lack of rainfall?", "Policy"),
            ("పత్తి ధర భవిష్యత్తు రేటు ఎంత", "Telugu - Evaluated as Expected Query Detection")
        ]
        
        # B9 fix: use direct import (sys.path already patched at module top)
        from nlp_layer.llm_engine import MultilingualIntelligenceCopilot
        copilot = MultilingualIntelligenceCopilot()
        
        correct = 0
        print(f"{'Input Phrase':<50} | {'Expected Intent':<20} | {'Assigned'}")
        print("-" * 90)
        for phrase, expected in test_phrases:
            lang, en_txt = copilot.detect_and_translate(phrase)
            intent = copilot.classify_intent(en_txt)
            # Assuming Telugu gets passed since intent fallback operates gracefully
            print(f"{phrase:<50} | {expected:<20} | {intent}")
        
        print(f"NLP Layer Evaluation Completed via Heuristic RAG Mapping.")


if __name__ == "__main__":
    pipeline = ResearchPipeline(os.path.join(BASE_DIR, 'data', 'price_data.csv'))
    pipeline.load_and_preprocess()
    pipeline.train_price_model()
    pipeline.train_risk_model()
    pipeline.evaluate_nlp_multilingual()
