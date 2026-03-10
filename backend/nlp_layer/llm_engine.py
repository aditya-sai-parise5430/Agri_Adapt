import re
import json

class MultilingualIntelligenceCopilot:
    """
    NLP LAYER
    Integrates Translation (IndicTrans/mT5 interface logic), Intent Classification, and RAG.
    """
    def __init__(self):
        # Universal Language Database
        self.supported_langs = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"]
        
        # Knowledge Base Mock (RAG Retrieval)
        self.rag_kb = {
            "rotation": "Crop rotation restores soil nitrogen organically. Soya beans alternate well with Maize to break pest cycles.",
            "subsidy": "Government drought subsidies (e.g., PMFBY in India) provide insurance compensation for rainfall deficits below 50% average.",
            "tomato": "Tomato price fluctuations currently map to transport-chain breakdowns resulting from regional floods causing severe supply decay.",
            "sow": "Sowing cotton relies heavily on preceding moisture levels. Wait until the first major pre-monsoon shower stabilizes topsoil."
        }

    def detect_and_translate(self, text: str) -> tuple:
        """
        Mocked IndicTrans / mT5 Layer: Detects South Asian input and normalizes to English.
        """
        # Very simplistic mock detection for demonstration in absence of live 3GB models
        if re.search(r'[\u0c00-\u0c7f]', text):
            return "Telugu", "Translated representation to English"
        elif re.search(r'[\u0b80-\u0bff]', text):
            return "Tamil", "Translated representation to English"
        elif re.search(r'[\u0c80-\u0cff]', text):
            return "Kannada", "Translated representation to English"
        elif re.search(r'[\u0d00-\u0d7f]', text):
            return "Malayalam", "Translated representation to English"
        elif re.search(r'[\u0900-\u097f]', text):
            return "Hindi", "Translated representation to English"
        else:
            return "English", text

    def classify_intent(self, query: str) -> str:
        """
        Intent Classification Engine (A, B, C, D, E).
        """
        q = query.lower()
        if "policy" in q or "subsidy" in q or "government" in q: return "Policy"
        if "price" in q or "cost" in q or "forecast" in q or "value" in q: return "Prediction"
        if "risk" in q or "drought" in q or "flood" in q or "weather" in q: return "Risk"
        if "should i" in q or "recommend" in q or "advisory" in q or "sow" in q: return "Advisory"
        if "what is" in q or "why" in q or "meaning" in q or "rotation" in q: return "Knowledge"
        
        # Mixed Intent fallback
        return "Mixed"

    def retrieve_rag_insight(self, query: str) -> str:
        """Fetch vectorized contextual awareness from Knowledge Base."""
        for key, info in self.rag_kb.items():
            if key in query.lower():
                return info
        return "Broad agricultural monitoring indicates standard protocols apply. Always test soil pH before altering nutrient inputs."

    def back_translate(self, english_text: str, target_lang: str) -> str:
        """Translates final LLM reasoning back to Farmer's native language."""
        if target_lang == "English": return english_text
        
        # Map simulated translations
        prefix = {
            "Hindi": "हिंदी (अनुवादित): ",
            "Telugu": "తెలుగు (అనువాదం): ",
            "Tamil": "தமிழ் (மொழிபெயர்ப்பு): ",
            "Kannada": "ಕನ್ನಡ (ಅನುವಾದ): ",
            "Malayalam": "മലയാളം (വിവർത്തനം): "
        }
        return f'{prefix.get(target_lang, "")}{english_text}'

    def process_query(self, query: str, context: dict, price_engine, risk_engine) -> dict:
        """Orchestrates ML limits + RAG reasoning -> Multilingual JSON"""
        # 1. Detect & Translate
        lang, en_query = self.detect_and_translate(query)
        
        # 2. Intent Pipeline
        intent = self.classify_intent(en_query)
        confidence = 0.92  # Dummy model confidence
        
        # ML Inference baseline
        ml_payload = {
            "rainfall": context.get("rainfall", 2.0),
            "temperature": context.get("temperature", 25.0),
            "humidity": float(context.get("humidity", 60)),
            "district": context.get("district", "Pune"),
            "crop_type": context.get("crop_type", "Wheat")
        }
        
        p_price = None
        r_score = None
        base_advisory = ""

        # Logic branching based on intent requirement
        if intent in ["Prediction", "Mixed", "Advisory"]:
            p_price = price_engine.predict(ml_payload)
            base_advisory += f"XGBoost forecasts predict {ml_payload['crop_type']} prices at ₹{p_price:.2f}. "
            
        if intent in ["Risk", "Mixed", "Advisory"]:
            _, r_score = risk_engine.predict(ml_payload)
            severity = "High Hazard" if r_score >= 0.7 else "Stable"
            base_advisory += f"Random Forest models assign a {severity} climate risk ({r_score*100:.1f}%). "

        if intent in ["Knowledge", "Policy", "Advisory", "Mixed"]:
            rag_chunk = self.retrieve_rag_insight(en_query)
            base_advisory += f"Expert Insight: {rag_chunk} "
            
        if not base_advisory:
            base_advisory = "I am unsure exactly what you need. Could you clarify your question?"
            
        # 5. Native Language Re-translation
        localized_response = self.back_translate(base_advisory.strip(), lang)

        return {
            "language_detected": lang,
            "intent": intent,
            "predicted_price": float(p_price) if p_price else None,
            "risk_score": float(r_score) if r_score else None,
            "advisory": localized_response,
            "confidence": confidence
        }
