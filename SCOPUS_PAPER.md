# AgriAdapt+: Climate–Weather–Market Intelligent Advisory System

## 1. Introduction
Agricultural decision-making represents a multi-dimensional challenge characterized by high volatility in market prices and accelerating climatic irregularities. This repository presents **AgriAdapt+**, a scalable, decoupled Machine Learning framework built to quantify climatic risks (e.g., probability of droughts) alongside robust time-series price projections, rendering actionable heuristics through a streamlined API.

## 2. System Architecture
AgriAdapt+ enforces an n-tier architecture emphasizing Separation of Concerns (SoC) and robust Dependency Injection, allowing independent scaling of inferential microservices. 

The framework is structurally decoupled into five primary layers:

### 2.1. Data Layer (`/data/` & `train_models.py`)
Responsible for data harmonization, missing value imputation (via localized linear interpolation to avoid cross-domain leakage), and temporal orchestration. The engine executes chronologically-constrained splits ensuring validation metrics reflect out-of-time forecasting precision. Feature engineering creates lag components (`price_lag_n`) and rolling aggregates dynamically bounding geographic boundaries.

### 2.2. ML Layer (`/backend/services/price_predictor.py` & `risk_predictor.py`)
Encapsulates algorithmic processing through serialized `.pkl` ensembles.
- **Price Forecasting (Regression)**: Deploys `XGBRegressor` evaluated iteratively against baseline linear bounds. Measured reliably offline using RMSE, MAE, and MAPE.
- **Climate Risk Assessment (Classification)**: Utilizes a heavily cross-validated `RandomForestClassifier` targeting Boolean climatic boundaries triggered via deterministic formulas (Rainfall $< T_{r}$ AND Temp $> T_{c}$). 

### 2.3. NLP Layer (`/backend/services/advisory_generator.py`)
A computationally inexpensive Generation Engine. Bypassing unconstrained LLM hallucinations mathematically, this module implements rule-based generative templates binding quantified algorithmic thresholds (predicted risk classes) to specific agronomic intervention strategies. 

### 2.4. API Layer (`/backend/main.py`)
Orchestrated via FastAPI. The system establishes endpoints incorporating built-in validation via `Pydantic`. Structural injection (`Depends()`) serves pre-loaded Singleton ML models to the endpoints, maintaining sub-millisecond route resolutions natively devoid of cold-starts.

### 2.5. Presentation Layer (`/frontend_st/app.py`)
Streamlit-based reactive visual framework binding the backend ecosystem to the user interface safely avoiding synchronous blockages. Presents interactive data visualisations dynamically generating projection curves and bounding box metrics. 

## 3. Deployment
The ecosystem supports autonomous scaling natively:
- **API Engine (Render)**: Deploy `backend/main.py` configuring native Uvicorn ASGI workers.
- **Interactive UI (Streamlit Community Cloud)**: Attach decoupled front-end binding the REST URL payload directly.

Both endpoints utilize completely independent constraints mapping `requirements.txt`.

## 4. Methodological Reproducibility 
Code for replicating feature-importances, temporal dataset distributions, algorithm benchmarks, and error diagnostics resides directly within `backend/train_models.py`.

*Note: Authored to meet constraints regarding high-scalability production pipelines without integrated monolithic conversational APIs.*
