import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="AgriAdapt+ | Multilingual Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
    .metric-box { background-color: #1e293b; border-radius: 10px; padding: 20px; text-align: center; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;}
    .value { font-size: 2.2rem; font-weight: 700; color: #10b981; }
    .value.danger { color: #ef4444; }
    .advisory-box { background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 20px; border-radius: 0 10px 10px 0; margin-top: 10px; font-size: 1.1rem; }
    .debug-badge { background: #334155; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin-right: 8px;}
</style>
""", unsafe_allow_html=True)

# SIDEBAR: Parameters
st.sidebar.title("🌍 Simulation Context")
selected_crop = st.sidebar.selectbox("Crop Type", ["Wheat", "Rice", "Cotton", "Soybean", "Maize"])
selected_district = st.sidebar.selectbox("District", ["Hyderabad", "Bengaluru", "Chennai", "Thiruvananthapuram", "Vijayawada"])
rainfall = st.sidebar.number_input("Rainfall (mm)", min_value=0.0, value=2.0, step=0.1)
temperature = st.sidebar.number_input("Temperature (°C)", min_value=-10.0, max_value=60.0, value=28.0, step=0.5)

st.title("🌾 AgriAdapt+ Intelligence Terminal")
st.markdown("Multilingual Query Engine powered by Localized NLP and Predictive Machine Learning.")

st.markdown("---")

def draw_visuals(price, r_score):
    if price and r_score is not None:
        col1, col2 = st.columns(2)
        with col1:
             st.markdown(f"<div class='metric-box'><div style='color:white;margin-bottom:10px'>Price Forecast (Target)</div><div class='value'>₹{price:.2f}</div></div>", unsafe_allow_html=True)
        with col2:
             risk_class = "danger" if r_score >= 0.7 else "value"
             st.markdown(f"<div class='metric-box'><div style='color:white;margin-bottom:10px'>Climate Hazard</div><div class='value {risk_class}'>{(r_score*100):.1f}%</div></div>", unsafe_allow_html=True)
             
        # Mock time-series projection chart
        dates = pd.date_range(start="2026-03-01", periods=14)
        prices_sim = np.random.normal(loc=price, scale=price*0.04, size=14)
        st.line_chart(pd.DataFrame({'Market Value (₹)': prices_sim}, index=dates))

# CHA_BOT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("E.g: Will rice price increase next month? | తదుపరి నెలలో పత్తి ధర పెరుగుతుందా?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Executing Intelligent Language Processing & Algorithm Retrieval..."):
        try:
            payload = {
                "query": prompt,
                "context": {
                    "rainfall": rainfall,
                    "temperature": temperature,
                    "district": selected_district,
                    "crop_type": selected_crop
                }
            }
            res = requests.post(f"{API_URL}/ask", json=payload)
            res.raise_for_status()
            inference = res.json()
            
            # Formatting Response Output beautifully
            resp_str = f"""
            <span class='debug-badge'>🌏 Lang: {inference['language_detected']}</span> 
            <span class='debug-badge'>🧠 Intent: {inference['intent']}</span>
            <span class='debug-badge'>🎯 Confidence: {inference['confidence']*100}%</span>
            \n<div class='advisory-box'>{inference['advisory']}</div>
            """
            
            # Display
            with st.chat_message("assistant"):
                st.markdown(resp_str, unsafe_allow_html=True)
                draw_visuals(inference.get('predicted_price'), inference.get('risk_score'))
                
            st.session_state.messages.append({"role": "assistant", "content": resp_str})

        except requests.exceptions.RequestException as e:
            err_msg = f"⚠️ Infrastructure unreachable. Please test API deployment."
            st.chat_message("assistant").markdown(err_msg)
            st.session_state.messages.append({"role": "assistant", "content": err_msg})
