# AgriAdapt+: Climate–Weather–Market Intelligent Advisory System

AgriAdapt+ is a comprehensive Multilingual AI ecosystem designed to provide farmers with real-time crop price forecasts, drought risk assessments, and expert agricultural advisories. It aligns with the research methodology outlined in the **AgriAdapt** paper, utilizing XGBoost for market trends and Random Forest for climate risk.

---

## 🛠️ Tech Stack & Data Sources

| Component | Technology | Source / API |
| :--- | :--- | :--- |
| **Backend** | FastAPI (Python 3.11+) | RESTful API Layer |
| **Frontend** | React + Vite | Tailwind-inspired Glassmorphism UI |
| **Weather** | **Open-Meteo API** | Real-time Rainfall, Temp, Humidity |
| **ML Models** | XGBoost & Random Forest | Trained on historical Maharashtra data |
| **NLP/Translation** | Deep-Translator & LangDetect | Multilingual Support (6 languages) |
| **Database** | CSV + Joblib Serialized Models | Local persistence for speed |

---

## ✅ Progress & Features Implemented

### 1. **Core Machine Learning Layer**
- [x] **XGBoost Price Predictor**: Time-series forecasting for Wheat, Rice, Cotton, Soybean, and Maize.
- [x] **Random Forest Risk Classifier**: Drought probability detection based on meteorological thresholds.
- [x] **Price Logic Fix**: Integrated crop-specific seed prices to ensure realistic market baselines (e.g., Cotton ~₹6200, Wheat ~₹2100).

### 2. **Multilingual NLP Engine**
- [x] **Real-time Translation**: Integrated `deep-translator` to support English, Hindi, Telugu, Tamil, Kannada, and Malayalam.
- [x] **Intent Classification**: Detects if a user is asking about Price, Risk, Policy, or Knowledge.
- [x] **Localized Advisories**: Automated generation of native-script advice (e.g., Telugu/Hindi) based on ML outputs.

### 3. **Live Data Integration**
- [x] **Weather Sync**: Auto-fetching live weather from Open-Meteo based on the selected District (Pune, Nagpur, Nashik, etc.).
- [x] **Geo-Mapping**: Coordinates mapping for Maharashtra districts to enable precise API calls.

### 4. **Modern UI/UX & Interactive Chatbot**
- [x] **React Dashboard**: A high-performance, glassmorphic dashboard with parameter sliders and a hybrid Chat/Advisory terminal.
- [x] **Fully Localized UI**: All frontend labels, dropdowns, and buttons dynamically translate to native scripts (e.g., தமிழ், తెలుగు) via a robust UI mapping table.
- [x] **Conversational AI**: The bot appends native-language follow-up questions to keep the farmer engaged.
- [x] **Suggestion Chips**: Clickable quick-action chips (e.g., [Price forecast?], [Subsidies?]) generate dynamically based on conversation intent, allowing one-tap interactions.

---

## ⏳ Pending / Future Roadmap
- [ ] **Advanced RAG**: Transition from mock Knowledge Base to a vector database (ChromaDB/FAISS) for deeper policy retrieval.
- [ ] **Data Visualization**: Implement D3.js or Chart.js in `Graphs.jsx` for historical price trend visualization.
- [ ] **Mobile App**: Porting the React frontend to a Capacitor/React Native shell for mobile deployment (as per paper goals).
- [ ] **Cloud Deployment**: Finalizing Docker configurations for Render (Backend) and Vercel (Frontend).

---

## 🚀 Execution Instructions

### 1. Requirements & Model Training
Ensure you have Python 3.10 or 3.11 installed.
```bash
cd backend
pip install -r requirements.txt

# CRITICAL: You MUST run train_models.py on your machine first
# to generate the .pkl model files required by the API.
python train_models.py
```

### 2. Start Backend API
```bash
python -m uvicorn api_layer.main:app --reload --port 8000
```
*The API will be available at `http://127.0.0.1:8000`. You can view the docs at `/docs`.*

### 3. Start Frontend Dashboard
Open a **new terminal window**:
```bash
cd frontend
npm install
npm run dev -- --port 5173
```
*Access the dashboard at `http://localhost:5173`.*

### 3. Streamlit (Alternative UI)
```bash
cd frontend_st
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧬 Methodology (Per Paper)
- **Price Forecasting**: Evaluates `XGBRegressor` using multi-lag features (1, 7, 14 days) and rolling means.
- **Risk Evaluation**: Classifies drought thresholds (Rainfall < 0.5mm & Temp > 20°C) using `RandomForestClassifier` with balanced class weights.
- **Multilingual Pipeline**: Detect -> Translate -> Intent -> ML Inference -> Back-Translate -> Farmer Delivery.
