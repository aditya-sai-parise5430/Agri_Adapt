import os
import json
import logging

try:
    from langchain.llms import HuggingFaceHub
    from langchain.prompts import PromptTemplate
except ImportError:
    pass

class LLMAdvisoryService:
    def __init__(self):
        # Initializing generic LLM heuristic handler
        # In complete production with api keys, you would load local or cloud models here:
        # e.g., self.llm = HuggingFaceHub(repo_id="mistralai/Mistral-7B-v0.1")
        self.knowledge_base = {
            "drought": "For sudden drought spikes, consider planting drought-resistant crops (e.g., Sorghum/Maize) and utilize deep drip irrigation methods to conserve surface evaporation.",
            "flood": "In extreme rainfall conditions, manage field drainage and avoid planting root crops that are highly susceptible to prolonged submerged rot.",
            "price": "When prices are forecasted to dip, consider utilizing cold-storage to delay market supply or negotiate pre-harvest contract pricing.",
        }

    def determine_intent(self, query: str) -> str:
        """Simple rules-based intent detection engine for NLP."""
        q = query.lower()
        if any(w in q for w in ["price", "cost", "market", "sell", "buy", "profit", "forecast"]):
            return "price"
        elif any(w in q for w in ["risk", "drought", "flood", "rain", "weather", "temperature", "climate"]):
            return "climate"
        elif any(w in q for w in ["how", "what", "why", "best", "should", "recommend"]):
            return "knowledge"
        return "general"

    def retrieve_knowledge(self, intent: str) -> str:
        """Mock RAG (Retrieval-Augmented Generation) lookup."""
        if intent in self.knowledge_base:
            return self.knowledge_base[intent]
        
        # Fallback multi-step reasoning look
        return "Combine mixed cropping techniques. Check real-time soil moisture parameters before committing to major pesticide applications."

    def generate_response(self, query: str, context: dict, price_model, risk_model) -> dict:
        """
        Creates intelligently framed advisory combining RAG text with actual ML execution limits.
        """
        intent = self.determine_intent(query)
        
        # Build strict parameters from context
        # Safely enforce base conditions so models don't crash
        ML_payload = {
            "rainfall": context.get("rainfall", 2.0),
            "temperature": context.get("temperature", 25.0),
            "humidity": context.get("humidity", 60),
            "district": context.get("district", "Pune"),
            "crop_type": context.get("crop_type", "Wheat")
        }
        
        # Execute Live Models
        pred_price = price_model.predict(ML_payload)
        risk_class, risk_prob = risk_model.predict(ML_payload)
        
        # Fetch Contextual RAG info
        rag_text = self.retrieve_knowledge(intent)
        
        # Format the output prompt response
        if intent == "price":
            advisory = f"Our XGBoost forecasting engines project a valuation of ₹{pred_price:.2f} for {ML_payload['crop_type']} in {ML_payload['district']}. Market Strategy: {rag_text}"
        elif intent == "climate":
            risk_cat = "SEVERE" if risk_class == 1 else "SAFE"
            advisory = f"Climate models indicate a {risk_cat} weather situation (Probability: {risk_prob*100:.1f}%). Risk Mitigation Protocol: {rag_text}"
        else:
            advisory = f"General Advisory for your {ML_payload['crop_type']} farm: {rag_text} Overall conditions appear optimal."
        
        # Deliver requested JSON architecture format
        return {
            "predicted_price": round(pred_price, 2),
            "risk_score": round(risk_prob, 2),
            "advisory": advisory
        }
