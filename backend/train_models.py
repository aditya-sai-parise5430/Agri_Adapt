import os
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# -------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'price_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'backend', 'models')

# Create model directory if it doesn't exist
os.makedirs(MODEL_DIR, exist_ok=True)

# Define thresholds for Climate Risk
RAINFALL_THRESHOLD = 0.5    # mm - example threshold for dry day
TEMPERATURE_THRESHOLD = 20.0 # Celsius - example threshold for hot day

def load_and_preprocess_data(filepath):
    """Loads CSV data and handles missing values properly using interpolation."""
    print("Loading data...")
    df = pd.read_csv(filepath)
    
    # Sort by date for proper time-series splits
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['district', 'crop_type', 'date']).reset_index(drop=True)
    
    # Handle missing values using interpolation (forward fill backward fill as fallback)
    print("Handling missing values...")
    cols_to_impute = ['price', 'rainfall', 'temperature', 'humidity']
    for col in cols_to_impute:
        if col in df.columns:
            # Interpolate per group to prevent data leakage across different districts/crops
            df[col] = df.groupby(['district', 'crop_type'])[col].transform(lambda x: x.interpolate(method='linear', limit_direction='both'))
            # Fallback for completely missing groups
            df[col] = df[col].fillna(df[col].mean()) 
            
    return df

def feature_engineering_price(df):
    """Creates lag features and rolling means grouped by geographical/crop segments."""
    print("Creating features for Price Forecasting...")
    df_feat = df.copy()
    
    group_cols = ['district', 'crop_type']
    
    # 1-day, 7-day, 14-day lag features for price
    df_feat['price_lag_1'] = df_feat.groupby(group_cols)['price'].shift(1)
    df_feat['price_lag_7'] = df_feat.groupby(group_cols)['price'].shift(7)
    df_feat['price_lag_14'] = df_feat.groupby(group_cols)['price'].shift(14)
    
    # 7-day rolling mean for price (calculate on shift(1) to avoid data leakage)
    df_feat['price_rolling_mean_7'] = df_feat.groupby(group_cols)['price'].transform(
        lambda x: x.shift(1).rolling(window=7, min_periods=1).mean()
    )
    
    # Optional weather lags could be added here
    df_feat['rainfall_lag_1'] = df_feat.groupby(group_cols)['rainfall'].shift(1)
    df_feat['temp_lag_1'] = df_feat.groupby(group_cols)['temperature'].shift(1)
    
    # Drop rows with NaN values created by shifting/lagging
    df_feat.dropna(inplace=True)
    
    # Re-sort temporally to maintain strict time-series ordering for split
    return df_feat.sort_values('date').reset_index(drop=True)

def prepare_risk_target(df):
    """Creates the drought risk classification target based on temperature and rainfall thresholds."""
    print("Creating target for Climate Risk...")
    df_risk = df.copy()
    # Target rule: rainfall < threshold AND temperature > threshold
    df_risk['drought_risk'] = np.where(
        (df_risk['rainfall'] < RAINFALL_THRESHOLD) & (df_risk['temperature'] > TEMPERATURE_THRESHOLD),
        1, 0
    )
    return df_risk

def time_series_split(df, target_col):
    """Splits data strictly by chronological order (80-20 default). NO random shuffle."""
    split_idx = int(len(df) * 0.8)
    
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]
    
    return train, test

def train_price_model(df):
    """Trains and returns price forecasting regression models."""
    print("\n" + "="*50)
    print("TASK 1: Price Forecasting Model")
    print("="*50)
    
    df_price = feature_engineering_price(df)
    
    features = [
        'rainfall', 'temperature', 'humidity', 
        'price_lag_1', 'price_lag_7', 'price_lag_14', 
        'price_rolling_mean_7', 'rainfall_lag_1', 'temp_lag_1',
        'district', 'crop_type'
    ]
    target = 'price'
    
    train, test = time_series_split(df_price, target)
    print(f"Train size: {len(train)}, Test size: {len(test)}")
    
    X_train, y_train = train[features], train[target]
    X_test, y_test = test[features], test[target]
    
    # Preprocessing Pipeline (Standardization + OneHotEncoding)
    numeric_features = [f for f in features if f not in ['district', 'crop_type']]
    categorical_features = ['district', 'crop_type']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ])
    
    # Definition: XGBoost Regressor
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, n_jobs=-1))
    ])
    
    # Definition: Baseline Linear Regression
    lr_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', LinearRegression())
    ])
    
    print("Training Baseline Linear Regression...")
    lr_pipeline.fit(X_train, y_train)
    lr_preds = lr_pipeline.predict(X_test)
    
    print("Training XGBoost Regressor...")
    xgb_pipeline.fit(X_train, y_train)
    xgb_preds = xgb_pipeline.predict(X_test)
    
    # Metric Evaluation
    def evaluate(y_true, y_pred, model_name):
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        mape = mean_absolute_percentage_error(y_true, y_pred)
        print(f"[{model_name}] RMSE: {rmse:.4f}, MAE: {mae:.4f}, MAPE: {mape:.4f}")
        return rmse, mae, mape
    
    evaluate(y_test, lr_preds, "Baseline Linear Regression")
    evaluate(y_test, xgb_preds, "XGBoost Regressor")
    
    # Save best model
    model_path = os.path.join(MODEL_DIR, 'price_model.pkl')
    joblib.dump(xgb_pipeline, model_path)
    print(f"Saved Price Model to {model_path}")
    
    # Plotting Actual vs Predicted (Advanced Options)
    plot_actual_vs_predicted(y_test, xgb_preds, 'Price Forecasting: Actual vs Predicted (XGBoost)', 'price_predictions.png')
    plot_feature_importance(xgb_pipeline, categorical_features, numeric_features, 'price_feature_importance.png')

    return xgb_pipeline

def train_risk_model(df):
    """Trains and returns climate risk classification model."""
    print("\n" + "="*50)
    print("TASK 2: Climate Risk Classification Model")
    print("="*50)
    
    df_risk = prepare_risk_target(df)
    
    features = ['rainfall', 'temperature', 'humidity', 'district', 'crop_type']
    target = 'drought_risk'
    
    # Keep time chronologically aligned
    train, test = time_series_split(df_risk, target)
    print(f"Train size: {len(train)}, Test size: {len(test)}")
    
    X_train, y_train = train[features], train[target]
    X_test, y_test = test[features], test[target]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['rainfall', 'temperature', 'humidity']),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['district', 'crop_type'])
        ])
    
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced', n_jobs=-1))
    ])
    
    print("Training Random Forest Classifier...")
    rf_pipeline.fit(X_train, y_train)
    rf_preds = rf_pipeline.predict(X_test)
    rf_probs = rf_pipeline.predict_proba(X_test)[:, 1] if len(np.unique(y_train)) > 1 else np.zeros(len(y_test))
    
    acc = accuracy_score(y_test, rf_preds)
    f1 = f1_score(y_test, rf_preds, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_test, rf_probs)
    except ValueError:
        roc_auc = 0.0 # Guard in case testing split lacks diverse classes
        
    print(f"[Random Forest] Accuracy: {acc:.4f}, F1-score: {f1:.4f}, ROC-AUC: {roc_auc:.4f}")
    
    model_path = os.path.join(MODEL_DIR, 'risk_model.pkl')
    joblib.dump(rf_pipeline, model_path)
    print(f"Saved Risk Model to {model_path}")
    
    return rf_pipeline

def plot_actual_vs_predicted(y_true, y_pred, title, filename):
    """Plots actual vs predicted target values, saving to model dir."""
    plt.figure(figsize=(12, 6))
    
    # Plotting first 150 points for visual clarity
    limit = min(150, len(y_true))
    y_true_plot = y_true.iloc[:limit].values if isinstance(y_true, pd.Series) else y_true[:limit]
    
    plt.plot(range(limit), y_true_plot, label='Actual', marker='o', markersize=4, linestyle='solid')
    plt.plot(range(limit), y_pred[:limit], label='Predicted', marker='x', markersize=4, linestyle='dashed', alpha=0.8)
    
    plt.title(title)
    plt.xlabel("Sample Index (Chronological time steps)")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, filename), dpi=150)
    plt.close()
    print(f"Saved actual vs predicted graph: {filename}")

def plot_feature_importance(pipeline, cat_feats, num_feats, filename):
    """Plots top feature importances using tree model property."""
    try:
        ohe_cols = pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(cat_feats)
        all_features = num_feats + list(ohe_cols)
        importances = pipeline.named_steps['model'].feature_importances_
        
        # Plot top 10 features
        indices = np.argsort(importances)[::-1][:10]
        plt.figure(figsize=(10,6))
        plt.title("Top 10 Feature Importances")
        plt.bar(range(10), importances[indices], align="center", color='skyblue', edgecolor='black')
        plt.xticks(range(10), [all_features[i] for i in indices], rotation=45, ha='right')
        plt.ylabel("Importance Score")
        plt.tight_layout()
        plt.savefig(os.path.join(MODEL_DIR, filename), dpi=150)
        plt.close()
        print(f"Saved feature importance graph: {filename}")
    except Exception as e:
        print(f"Feature importance rendering skipped: {e}")

# -------------------------------------------------------------
# NLP ADVISORY GENERATOR
# -------------------------------------------------------------
def generate_advisory(predicted_price: float, risk_probability: float, crop_type: str) -> str:
    """
    Generates a farmer-friendly advisory sentence based on market and climate predictions.
    Uses templated heuristic rules based on risk levels.
    """
    advisory_parts = []
    
    # Dynamic Advisory Text Generation
    if risk_probability >= 0.7:
        advisory_parts.append(f"High drought risk expected.")
        advisory_parts.append(f"Consider drought-resistant {crop_type} varieties and secure early irrigation resources.")
    elif risk_probability >= 0.3:
        advisory_parts.append(f"Moderate weather risk observed.")
        advisory_parts.append(f"Monitor soil moisture levels closely for your {crop_type} fields.")
    else:
        advisory_parts.append(f"Favorable climate conditions expected for planting and managing {crop_type}.")
        
    advisory_parts.append(f"Market price predicted to be around ₹{predicted_price:.2f} per quintal next week.")
    
    return " ".join(advisory_parts)

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print(f"Error: dataset missing at {DATA_PATH}")
    else:
        df = load_and_preprocess_data(DATA_PATH)
        
        # Trigger model training execution
        train_price_model(df)
        train_risk_model(df)
        
        print("\n" + "="*50)
        print("TASK 7: Testing NLP Advisory Generator")
        print("="*50)
        
        # Sample parameters mock test
        example_price = 2155.80
        example_risk = 0.85
        example_crop = "Wheat"
        print(f"Input: Price={example_price}, Risk={example_risk}, Crop={example_crop}")
        print(f"Result:\n-> {generate_advisory(example_price, example_risk, example_crop)}\n")
        print("Pipeline Execution Completed.")
