import re
import json

from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

class MultilingualIntelligenceCopilot:
    """
    NLP LAYER
    Integrates Translation (deep-translator), Intent Classification, and expanded RAG knowledge base.
    """
    def __init__(self):
        # B6/B14 fix: keys match exactly what the frontend sends
        self.supported_langs = ["English", "Hindi", "Telugu (తెలుగు)", "Tamil (தமிழ்)", "Kannada (ಕನ್ನಡ)", "Malayalam (മലയാളം)"]
        
        # ISO code → display name (as sent by frontend)
        self.lang_map = {
            "en": "English",
            "hi": "Hindi",
            "ta": "Tamil (தமிழ்)",
            "te": "Telugu (తెలుగు)",
            "kn": "Kannada (ಕನ್ನಡ)",
            "ml": "Malayalam (മലയാളം)"
        }
        
        # -------------------------------------------------------
        # EXPANDED RAG KNOWLEDGE BASE
        # Each key is a topic keyword; value is expert advisory text
        # -------------------------------------------------------
        self.rag_kb = {
            # ── Crop Rotation & Soil Health ──
            "rotation": (
                "Crop rotation is essential for sustainable yields. "
                "Rotate cereals (Wheat/Maize) with legumes (Soybean/Chickpea) every season. "
                "Legumes fix atmospheric nitrogen, reducing fertilizer costs by 20-30%. "
                "After cotton, plant a short-duration pulse like Moong Dal to restore soil microbiome."
            ),
            "soil": (
                "Soil health directly controls productivity. Test pH every season—optimal range is 6.0-7.5. "
                "Apply vermicompost at 2-3 tonnes/acre to improve water retention. "
                "Green manuring with Dhaincha or Sunhemp before the Kharif season enriches organic matter significantly."
            ),
            "fertilizer": (
                "Balanced fertilization using NPK (Nitrogen-Phosphorus-Potassium) is critical. "
                "For Wheat: apply 120:60:40 kg/ha. For Cotton: 150:60:60 kg/ha split in 3 doses. "
                "Avoid excess urea—it acidifies soil over time. Use neem-coated urea to slow nitrogen release."
            ),
            "compost": (
                "Organic composting reduces input costs and improves soil structure. "
                "Farm Yard Manure (FYM) at 10 tonnes/ha before sowing improves water-holding capacity by 15%. "
                "Vermicompost is 5× more nutritious than regular FYM and enhances microbial activity."
            ),

            # ── Irrigation & Water Management ──
            "irrigation": (
                "Drip irrigation saves 40-60% water compared to flood irrigation and improves crop yield by 20-50%. "
                "PM Sinchai Yojana provides 55% subsidy on drip/sprinkler systems—apply via your district agriculture office. "
                "For Wheat: 5-6 irrigations are sufficient. Avoid irrigation during grain-filling stage to prevent lodging."
            ),
            "drip": (
                "Drip irrigation is the most water-efficient method for cotton and vegetables. "
                "Fertigration (adding fertilizers through drip) saves labor and increases nutrient use efficiency by 30%. "
                "Government subsidy under PMKSY covers 55% cost for small/marginal farmers."
            ),
            "water": (
                "Water stress during critical stages causes significant yield loss: "
                "Wheat—tillering and grain filling; Rice—flowering; Cotton—boll formation. "
                "Install soil moisture sensors or use tensiometers to optimize irrigation scheduling. "
                "Check your district's groundwater level reports before drilling new borewells."
            ),
            "drought": (
                "During drought conditions: switch to drought-tolerant varieties like GW-496 (Wheat), "
                "NLR-34449 (Rice), or KDCH-9 (Cotton). Apply mulching to reduce soil evaporation by 30%. "
                "Use antitranspirants like Kaolin at 5% spray to reduce crop water loss. "
                "PMFBY (Pradhan Mantri Fasal Bima Yojana) provides compensation for rainfall below 50% of average."
            ),
            "flood": (
                "In waterlogging conditions: ensure proper field drainage with ridges/furrows system. "
                "Avoid sowing root crops like groundnut in flood-prone areas. "
                "Flood-tolerant rice varieties: Swarna Sub-1, FL478 can survive 17 days of submergence. "
                "Apply 25 kg of potash fertilizer after floodwater recedes to promote recovery."
            ),

            # ── Price Forecasting & Market ──
            "price": (
                "Crop price forecasting depends on supply-demand balance, MSP (Minimum Support Price), "
                "seasonal trends, and weather events. XGBoost models with 1, 7, and 14-day price lags "
                "achieve RMSE of 87 for Maharashtra crops. "
                "Current MSP (2024-25): Wheat ₹2275/qtl, Rice ₹2300/qtl, Soybean ₹4892/qtl, Cotton ₹7121/qtl. "
                "Sell through e-NAM (National Agriculture Market) portal for better price discovery."
            ),
            "market": (
                "APMC mandis operate under regulated market systems with licensed traders. "
                "Register on e-NAM portal (enam.gov.in) to access 1000+ markets digitally. "
                "Price variations between mandis can be 5-15%—compare before selling. "
                "Hold produce in cold storage during oversupply to sell during price-favorable periods."
            ),
            "sell": (
                "Best selling strategies: monitor AGMARKNET and eNAM for daily price signals. "
                "Cooperatives like IFFCO and Amul enable collective bargaining power. "
                "Contract farming with FPOs (Farmer Producer Organizations) ensures minimum price guarantees. "
                "Avoid selling during harvest peak when prices are 10-20% lower."
            ),
            "msp": (
                "Minimum Support Price (MSP) is declared by CCEA before each sowing season. "
                "2024-25 MSPs: Paddy ₹2300/qtl, Wheat ₹2275/qtl, Maize ₹2090/qtl, "
                "Soybean ₹4892/qtl, Groundnut ₹6783/qtl, Cotton ₹7121/qtl (medium staple). "
                "Procure through FCI or state agencies at MSP. Register on PM-KISAN portal."
            ),

            # ── Sowing & Crop Management ──
            "sow": (
                "Optimal sowing windows (Maharashtra): Kharif—June 15 to July 15 (post first good monsoon shower). "
                "Rabi—October 15 to November 15 for wheat; October for chickpea. "
                "Cotton: sow when soil temperature exceeds 25°C and pre-monsoon shower stabilizes topsoil moisture. "
                "Seed treatment with Thiram (2g/kg) + Carbendazim (1g/kg) prevents soil-borne diseases."
            ),
            "harvest": (
                "Harvesting at correct moisture content prevents post-harvest losses: "
                "Wheat—at 12-14% grain moisture; Rice—20-22% (then dry to 14%). "
                "Use combine harvesters for large farms to reduce losses to <3% vs 8-15% with manual harvesting. "
                "Avoid harvesting during rains to prevent aflatoxin contamination in groundnuts."
            ),
            "pest": (
                "Integrated Pest Management (IPM): use pheromone traps for bollworm in cotton. "
                "Spray Neem-based pesticides (Azadirachtin 1500 ppm) for sucking pests. "
                "For fall armyworm in maize: apply Emamectin Benzoate 5% SG @0.4g/litre at early instar stage. "
                "Chemical pesticide rotation prevents resistance buildup in pest populations."
            ),
            "disease": (
                "Common crop diseases and management: "
                "Wheat rust—spray Propiconazole 25% EC @0.1% at first sign; "
                "Rice blast—use Tricyclazole 75% WP @0.06%; "
                "Cotton wilt—use disease-resistant varieties and Carbendazim soil drench. "
                "Crop monitoring twice a week helps in early disease detection and prevention."
            ),

            # ── Government Schemes & Policy ──
            "subsidy": (
                "Key agricultural subsidies in India: "
                "1. PM-KISAN: ₹6000/year direct income support—enroll at pmkisan.gov.in. "
                "2. PMFBY (Crop Insurance): 2% premium for Kharif, 1.5% for Rabi—register through bank or CSC. "
                "3. Drip/Sprinkler Irrigation: 55% subsidy under PMKSY for small/marginal farmers. "
                "4. Kisan Credit Card: credit up to ₹3 lakh at 4% interest rate (after 2% subvention). "
                "5. Soil Health Card scheme: free soil testing every 2 years."
            ),
            "policy": (
                "Recent agricultural policy updates: "
                "PM-KISAN: farmers receive ₹2000 every 4 months (₹6000/year). "
                "e-NAM integration across 1000+ markets for transparent price discovery. "
                "PMFBY crop insurance covers losses from drought, flood, pest, and disease. "
                "Agri Infrastructure Fund: ₹1 lakh crore for post-harvest management. "
                "FPO policy: government targets 10,000 new Farmer Producer Organizations by 2027-28."
            ),
            "loan": (
                "Agricultural credit options: "
                "Kisan Credit Card (KCC): up to ₹3 lakh at 7% (net 4% with interest subvention). "
                "NABARD provides refinance to cooperative banks for long-term agricultural investments. "
                "PM-MUDRA: ₹50,000-₹10 lakh for agri-allied businesses without collateral. "
                "State Bank of India's Agri Gold Loan: quick credit against gold ornaments at 8.8% p.a."
            ),
            "government": (
                "Government support programs for farmers: "
                "PM-KISAN portal: pmkisan.gov.in for direct benefit registration. "
                "eNAM: enam.gov.in for digital mandi trading. "
                "Kisan Call Center: 1800-180-1551 (free) for agri expert advice. "
                "Soil Health Card: 2-year soil testing cycle by Agriculture Department. "
                "Agri Clinics Scheme: subsidized agri-consulting by trained entrepreneurs."
            ),
            "insurance": (
                "PMFBY (Pradhan Mantri Fasal Bima Yojana): "
                "Premium: 2% for Kharif, 1.5% for Rabi crops, 5% for cash crops. "
                "Covers: drought, flood, landslide, hailstorm, pest/disease outbreak. "
                "Claim settlement target: within 45 days of harvest. "
                "Enroll through nearest bank branch or CSC center before sowing season cutoff date."
            ),

            # ── Specific Crops ──
            "wheat": (
                "Wheat cultivation tips for Maharashtra: "
                "Sow HD-2967 or PBW-343 varieties in October-November. "
                "Apply 120-60-40 NPK kg/ha as basal and top-dress 60 kg N at tillering + jointing. "
                "Ideal rainfall: 45-75 cm; irrigation needed at crown-root initiation and heading stages. "
                "MSP 2024-25: ₹2275/qtl. Expected market premium post-harvest: 5-8%."
            ),
            "rice": (
                "Rice cultivation guidance: "
                "Transplanted paddy requires 20-25 days old seedlings for best results. "
                "SRI (System of Rice Intensification) method saves 40% water and boosts yield by 20-30%. "
                "Apply Zinc Sulphate (25 kg/ha) as basal—zinc deficiency is common in Maharashtra soils. "
                "MSP 2024-25: ₹2300/qtl for common grade. Sell to FCI procurement centers for guaranteed MSP."
            ),
            "cotton": (
                "Cotton management in Maharashtra's Vidarbha region: "
                "Use Bt cotton hybrids (JKCH-1947, RCH-2) for bollworm resistance. "
                "Apply 150-60-60 NPK kg/ha; avoid excess nitrogen—causes vegetative growth over boll formation. "
                "Critical irrigation periods: flowering and boll development. "
                "MSP 2024-25: ₹7121/qtl (medium staple). Avoid distress selling during harvest month."
            ),
            "soybean": (
                "Soybean agronomy for Kharif season: "
                "Use JS-335 or MACS-450 varieties; seed rate 70-80 kg/ha. "
                "Inoculate seeds with Bradyrhizobium japonicum for biological nitrogen fixation. "
                "Aerial topdressing N not required if well inoculated—saves ₹800-1200/ha in fertilizer. "
                "MSP 2024-25: ₹4892/qtl. Export to soy processing units in Latur/Nanded for premium prices."
            ),
            "maize": (
                "Maize (Corn) crop management: "
                "Hybrid varieties like DKC-9144, P-3522 yield 8-12 tonnes/ha under good management. "
                "Critical water need: tasseling and silking stage—water stress at this point reduces yield 50%. "
                "Apply 150-70-70 NPK kg/ha; topdress 60 kg urea at knee-high stage. "
                "MSP 2024-25: ₹2090/qtl. Sell to poultry feed and starch industry for 5-10% above MSP."
            ),
            "tomato": (
                "Tomato price volatility is driven by supply gluts and transport chain disruptions. "
                "Best months to grow: Oct-Feb (Rabi) for stable prices during April-June. "
                "Use drip fertigation and plastic mulch to achieve 40-60 tonne/ha yield. "
                "Join a Farmer Producer Organization (FPO) for collective market negotiation. "
                "Cold chain logistics can buffer 2-4 weeks of peak supply, stabilizing returns by 20-40%."
            ),

            # ── Climate Risk ──
            "risk": (
                "Climate risk in agriculture includes drought, flood, heatwave and frost events. "
                "Our Random Forest model detects drought risk when rainfall <0.5mm/day AND temperature >20°C. "
                "At >70% risk probability: switch to drought-tolerant varieties; activate PMFBY insurance claim. "
                "At 30-70% risk: monitor soil moisture weekly; install water-saving devices in advance."
            ),
            "climate": (
                "Climate change impacts on Maharashtra agriculture: "
                "Average temperature rise of 0.5-1.5°C increases water demand by 10-15%. "
                "Unseasonal rains and hailstorms are increasing—PMFBY covers these events. "
                "Recommended adaptation: shift to shorter-duration varieties, improve drainage, adopt zero-tillage. "
                "Carbon farming initiatives can earn ₹500-2000/acre/year through voluntary carbon credits."
            ),
            "weather": (
                "Real-time weather monitoring is essential for crop management planning. "
                "Open-Meteo API provides hourly temperature, rainfall, and humidity data for any district. "
                "Indian Meteorological Department's (IMD) agromet advisory: at imd.gov.in/pages/agrimet_main.php. "
                "Kisan Mausam Sewa app provides localized 5-day weather forecasts tailored for farmers."
            ),
        }

        # Follow-up guiding question (in English, gets back-translated below)
        self.followup_by_intent = {
            "Prediction": "Would you also like to know the drought risk for your region, or tips on the best selling time?",
            "Risk": "Would you like advice on drought-resistant varieties to plant, or information on crop insurance schemes?",
            "Policy": "Would you like to know how to enroll in PMFBY insurance, or check the current MSP for your crop?",
            "Advisory": "Can I provide more details on irrigation techniques, or help you plan the next sowing season?",
            "Knowledge": "Would you like to ask about government subsidies, or get a price forecast for your crop?",
            "Mixed": "Is there any other aspect — price, risk, irrigation, or subsidies — you would like to explore?",
        }
        
        # Suggested follow-ups per intent (clickable chips shown in UI)
        self.chips_by_intent = {
            "Prediction": ["Drought Risk?", "Best time to sell?", "Subsidies?", "Irrigation tips"],
            "Risk": ["Resistant varieties?", "Crop insurance?", "Irrigation scheme?", "Price forecast"],
            "Policy": ["Enroll in PMFBY?", "Current MSP?", "Kisan Credit Card?", "eNAM portal"],
            "Advisory": ["Sowing time?", "Fertilizer dose?", "Pest management?", "Market price"],
            "Knowledge": ["Subsidies?", "Price forecast?", "Drought risk?", "Crop rotation"],
            "Mixed": ["Price forecast?", "Drought risk?", "Subsidies?", "Irrigation"],
        }

    def detect_and_translate(self, text: str) -> tuple:
        """Uses deep-translator and langdetect to normalize input to English."""
        try:
            detected_iso = detect(text)
            lang_name = self.lang_map.get(detected_iso, "English")
            if detected_iso == "en":
                return "English", text
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            return lang_name, translated
        except:
            return "English", text

    def classify_intent(self, query: str) -> str:
        """Intent Classification Engine."""
        q = query.lower()
        if any(w in q for w in ["policy", "subsidy", "government", "scheme", "loan", "insurance", "pmfby", "pm-kisan", "kisan", "msp"]): return "Policy"
        if any(w in q for w in ["price", "cost", "forecast", "value", "sell", "market", "msp", "rate", "expensive", "cheap"]): return "Prediction"
        if any(w in q for w in ["risk", "drought", "flood", "weather", "rain", "climate", "temperature", "heatwave", "storm"]): return "Risk"
        if any(w in q for w in ["should i", "recommend", "advisory", "sow", "when to", "how much", "best time", "harvest"]): return "Advisory"
        if any(w in q for w in ["what is", "why", "meaning", "rotation", "how", "technique", "fertilizer", "pest", "disease", "irrigation"]): return "Knowledge"
        return "Mixed"

    def retrieve_rag_insight(self, query: str) -> str:
        """Match keywords in query against knowledge base and return best-matching insight."""
        q = query.lower()
        
        # Score each KB entry by number of keyword matches
        best_key, best_score = None, 0
        for key in self.rag_kb:
            if key in q:
                score = len(key)  # prefer longer/more specific key matches
                if score > best_score:
                    best_score = score
                    best_key = key
        
        if best_key:
            return self.rag_kb[best_key]
        
        # Fallback: scan for partial matches within the KB values
        for key, info in self.rag_kb.items():
            # Check if any word from the query appears in the KB key
            query_words = set(q.split())
            if query_words.intersection({key}):
                return info
        
        return (
            "Based on standard agronomy practices: maintain balanced soil nutrition, "
            "adopt Integrated Pest Management (IPM), use drought-tolerant varieties during water stress periods, "
            "and connect with the Kisan Call Center (1800-180-1551) for free expert advice tailored to your region."
        )

    def back_translate(self, english_text: str, target_lang: str) -> str:
        """Translates final reasoning back to farmer's native language via GoogleTranslator."""
        if target_lang == "English":
            return english_text
        
        lang_to_iso = {
            "Hindi": "hi",
            "Telugu (తెలుగు)": "te",
            "Tamil (தமிழ்)": "ta",
            "Kannada (ಕನ್ನಡ)": "kn",
            "Malayalam (മലയാളം)": "ml"
        }
        
        iso = lang_to_iso.get(target_lang)
        if iso:
            try:
                return GoogleTranslator(source='en', target=iso).translate(english_text)
            except Exception as e:
                print(f"[back_translate] Translation failed for {target_lang}: {e}")
        
        return english_text

    def process_query(self, query: str, language: str, context: dict, price_engine, risk_engine) -> dict:
        """Orchestrates ML inference + RAG reasoning -> Multilingual JSON response"""
        # 1. Detect & Translate input to English
        if language and language in self.supported_langs:
            lang = language
            if lang == "English":
                en_query = query
            else:
                try:
                    en_query = GoogleTranslator(source='auto', target='en').translate(query)
                except:
                    en_query = query
        else:
            lang, en_query = self.detect_and_translate(query)
        
        # 2. Intent Classification
        intent = self.classify_intent(en_query)
        confidence = 0.92

        # 3. Build ML inference payload from context
        crop = context.get("crop_type", "Wheat")
        district = context.get("district", "Pune")
        ml_payload = {
            "rainfall":    context.get("rainfall", 2.0),
            "temperature": context.get("temperature", 25.0),
            "humidity":    float(context.get("humidity", 60)),
            "district":    district,
            "crop_type":   crop
        }
        
        p_price = None
        r_score = None
        base_advisory = ""

        # 4. Run ML models based on intent
        if intent in ["Prediction", "Mixed", "Advisory"]:
            p_price = price_engine.predict(ml_payload)
            base_advisory += (
                f"📊 Market Intelligence: XGBoost forecasting models project the {crop} price in {district} "
                f"at ₹{p_price:.2f} per quintal next week. "
            )
            
        if intent in ["Risk", "Mixed", "Advisory"]:
            _, r_score = risk_engine.predict(ml_payload)
            if r_score >= 0.7:
                risk_label = "⚠️ HIGH HAZARD"
                risk_tip = "Activate PMFBY crop insurance claim and switch to drought-resistant varieties immediately."
            elif r_score >= 0.3:
                risk_label = "🔶 MODERATE RISK"
                risk_tip = "Monitor soil moisture weekly and prepare contingency irrigation plan."
            else:
                risk_label = "✅ STABLE"
                risk_tip = "Conditions are favorable. Proceed with standard crop management practices."
            base_advisory += (
                f"🌤️ Climate Assessment: Random Forest classifies the current climate as {risk_label} "
                f"(probability: {r_score*100:.1f}%). {risk_tip} "
            )

        # 5. Retrieve RAG knowledge insight
        if intent in ["Knowledge", "Policy", "Advisory", "Mixed", "Risk", "Prediction"]:
            rag_chunk = self.retrieve_rag_insight(en_query)
            base_advisory += f"📚 Expert Guidance: {rag_chunk}"
        
        if not base_advisory:
            base_advisory = (
                "I can help with crop price forecasts, drought risk analysis, government schemes, "
                "and farming best practices. Please ask a specific question about your crop or region."
            )
            
        # 6. Back-translate to farmer's native language
        localized_response = self.back_translate(base_advisory.strip(), lang)

        # 6. Append a conversational follow-up question (keep conversation going)
        followup_en = self.followup_by_intent.get(intent, "Is there anything else I can help you with?")
        followup_local = self.back_translate(followup_en, lang)
        full_response = localized_response + " " + followup_local

        # 7. Translate chips into the user's language
        chips_en = self.chips_by_intent.get(intent, ["Price forecast?", "Drought risk?", "Subsidies?"])
        if lang != "English":
            chips_local = []
            for chip in chips_en:
                try:
                    chips_local.append(self.back_translate(chip, lang))
                except:
                    chips_local.append(chip)
        else:
            chips_local = chips_en

        return {
            "language_detected": lang,
            "intent": intent,
            "predicted_price": float(p_price) if p_price is not None else None,
            "risk_score": float(r_score) if r_score is not None else None,
            "advisory": full_response,
            "confidence": confidence,
            "suggested_followups": chips_local,
        }
