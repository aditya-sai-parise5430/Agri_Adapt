# AgriAdapt+: Climate–Weather–Market Intelligent Advisory System

AgriAdapt+ is a comprehensive Machine Learning ecosystem designed to generate reliable insights on crop prices and climate hazards (e.g., droughts), leveraging time-series forecasting, predictive modelling, and Generative NLP heuristics.

## 📦 Project Structure
```text
agriadapt/
│
├── backend/                  # FastAPI Application Core
│   ├── main.py               # Routes: /predict and /ask
│   ├── models/               # Auto-saved Joblib .pkl architectures (XGBoost & RandomForest)
│   ├── services/
│   │   ├── price_predictor.py    # XGBoost execution logic
│   │   ├── risk_predictor.py     # Probability classification logic
│   │   ├── advisory_generator.py # Heuristic rules advisory logic
│   │   ├── llm_service.py        # Chatbot RAG heuristic pipeline for Q&A
│   │   └── train_models.py       # Full reproducibility pipeline (Task 1 & 2 logic)
│   ├── utils/
│   │   └── preprocessing.py      # Powerful Pydantic schema validation wrappers
│   └── requirements.txt
│
├── frontend_st/              # Streamlit Web Application  
│   └── app.py                # Single-page dashboard + Chat UI
│
├── data/
│   └── price_data.csv        # Contains chronological multi-feature weather+crop stats
│
└── config/                   # Configuration parameters
```

## 🚀 Execution Instructions

### 1. Training The Models
If you want to re-train the Models from scratch utilizing your `price_data.csv` dataset, maintaining chronological Time-Series constraints alongside R&D graphs:
```bash
cd backend
python ml_layer/train_research.py
```
*Outputs `price_model.pkl` and `risk_model.pkl` alongside diagnostic visual evaluation graphs inside `backend/models/`.*

### 2. Launch The Backend API
We utilize FastAPI linked with `uvicorn` due to its blinding inference speed and validation handling.
```bash
cd backend
pip install -r requirements.txt
python api_layer/main.py
```
*(Alternative: `uvicorn api_layer.main:app --reload`)*

### 3. Launch The Frontend Dashboard
Following modern Python full-stack requests, the dashboard is operated in Streamlit.
```bash
cd frontend_st
pip install streamlit
streamlit run app.py
```
*Access your browser via `http://localhost:8501` to use the Dashboard.*

---

## ☁️ Deployment Instructions

### Deploying the Backend on Render
1. Create a `Render Web Service`.
2. Link your GitHub Repository.
3. **Build Command:** `pip install -r backend/requirements.txt`
4. **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Deploying the Frontend on Streamlit Cloud
1. Create a `Streamlit Community Cloud` account.
2. Link your GitHub Repository.
3. Define the Main file path as: `frontend_st/app.py`.
4. Ensure `streamlit` and `requests` are listed in your active constraints file or the `requirements.txt` uploaded.

---
## 🧬 Methodology Used

- **Price Forecasting**: Evaluates `XGBRegressor` against Baseline Linear Regressions enforcing localized cross-sectional lag features, scoring on RMSE and MAPE. Interpolation mappings enforce strictly zero geographical data leakage.
- **Risk Evaluation**: Classifies drought thresholds using highly unbalanced-weighted `RandomForestClassifier`.
- **RAG NLP Inference**: Integrates a functional `query->intent` detector and `knowledge base` injector, satisfying JSON LLM heuristic generation standards.
