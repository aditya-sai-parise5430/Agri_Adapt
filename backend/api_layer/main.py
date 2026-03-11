from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_layer.price_predictor import PricePredictor
from ml_layer.risk_predictor import RiskPredictor
from nlp_layer.llm_engine import MultilingualIntelligenceCopilot
# B5 fix: single consolidated import (removed duplicate on former line 3)
from api_layer.schemas import PredictionRequest, AskRequest, IntelligentResponse, PredictResponse
from services.advisory_generator import generate_advisory
from utils.weather_service import get_live_weather

# Core Architecture: API LAYER
app = FastAPI(
    title="AgriAdapt+ | Multilingual Intelligence Engine", 
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Injection Singletons
_price_model = PricePredictor()
_risk_model = RiskPredictor()
_nlp_copilot = MultilingualIntelligenceCopilot()

def get_price_model(): return _price_model
def get_risk_model(): return _risk_model
def get_nlp_copilot(): return _nlp_copilot

@app.get("/")
def health_status():
    return {"module": "API_LAYER", "status": "active"}

@app.get("/weather/{district}")
def fetch_weather(district: str):
    return get_live_weather(district)

@app.post("/predict", response_model=PredictResponse)
def run_raw_predictions(
    req: PredictionRequest,
    price_model: PricePredictor = Depends(get_price_model),
    risk_model: RiskPredictor = Depends(get_risk_model)
):
    """Raw inference endpoint bypassing NLP."""
    try:
        data = req.dict()
        pred_price = price_model.predict(data)
        risk_class, risk_prob = risk_model.predict(data)

        # Generate advisory
        advisory = generate_advisory(
            predicted_price=pred_price,
            risk_probability=risk_prob,
            crop_type=req.crop_type,
            language=req.language or "English"
        )

        return {
            "predicted_price": pred_price,
            "risk_classification": int(risk_class),
            "risk_probability": float(risk_prob),
            "advisory": advisory
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=IntelligentResponse)
def ask_universal_question(
    req: AskRequest,
    price_model: PricePredictor = Depends(get_price_model),
    risk_model: RiskPredictor = Depends(get_risk_model),
    copilot: MultilingualIntelligenceCopilot = Depends(get_nlp_copilot)
):
    """
    RAG-driven Multilingual Q&A Copilot processing intents:
    - Predictions, Risk, Advisory, Knowledge, Policy
    """
    try:
        response_data = copilot.process_query(
            query=req.query,
            language=req.language,
            context=req.context or {},
            price_engine=price_model,
            risk_engine=risk_model
        )
        return IntelligentResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP Layer Error: {str(e)}")
