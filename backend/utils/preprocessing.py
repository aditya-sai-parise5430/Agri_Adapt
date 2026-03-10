from pydantic import BaseModel, Field
from typing import Optional, Dict

class PredictionRequest(BaseModel):
    rainfall: float = Field(..., description="Rainfall amount in mm")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    district: str = Field(..., description="Geographical district")
    crop_type: str = Field(..., description="Name of the crop")
    language: str = Field("English", description="Requested Advisory Output Language")
    
    price_lag_1: Optional[float] = Field(None, description="Previous day price")
    price_lag_7: Optional[float] = Field(None, description="Price 7 days ago")
    price_lag_14: Optional[float] = Field(None, description="Price 14 days ago")
    price_rolling_mean_7: Optional[float] = Field(None, description="7-day rolling mean of price")
    rainfall_lag_1: Optional[float] = Field(None, description="Previous day rainfall")
    temp_lag_1: Optional[float] = Field(None, description="Previous day temperature")

class PredictionResponse(BaseModel):
    predicted_price: float
    risk_probability: float
    risk_classification: int
    advisory: str

class AskRequest(BaseModel):
    query: str
    context: Optional[Dict] = None

class AskResponse(BaseModel):
    predicted_price: Optional[float] = None
    risk_score: Optional[float] = None
    advisory: str
