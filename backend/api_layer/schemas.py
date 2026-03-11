from pydantic import BaseModel, Field
from typing import Optional, Dict

class PredictionRequest(BaseModel):
    rainfall: float = Field(..., description="Rainfall amount in mm")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    district: str = Field(..., description="Geographical district")
    crop_type: str = Field(..., description="Name of the crop")
    language: Optional[str] = "English"
    
    # Lag features
    price_lag_1: Optional[float] = None
    price_lag_7: Optional[float] = None
    price_lag_14: Optional[float] = None
    price_rolling_mean_7: Optional[float] = None
    rainfall_lag_1: Optional[float] = None
    temp_lag_1: Optional[float] = None

class AskRequest(BaseModel):
    query: str
    language: Optional[str] = "English"
    context: Optional[Dict] = None

class IntelligentResponse(BaseModel):
    language_detected: str
    intent: str
    predicted_price: Optional[float] = None
    risk_score: Optional[float] = None
    advisory: str
    confidence: float
    suggested_followups: list[str] = []

class PredictResponse(BaseModel):
    predicted_price: float
    risk_classification: int
    risk_probability: float
    advisory: str
