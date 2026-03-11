import requests
from typing import Dict, Tuple

# Mapping Districts to Lat/Long for Open-Meteo
DISTRICT_COORDS = {
    "Pune": (18.5204, 73.8567),
    "Nagpur": (21.1458, 79.0882),
    "Nashik": (19.9975, 73.7898),
    "Aurangabad": (19.8762, 75.3433),
    "Kolhapur": (16.7050, 74.2433),
    "Andhra Pradesh": (16.5062, 80.6480) # Using Vijayawada as proxy
}

def get_live_weather(district: str) -> Dict[str, float]:
    """
    Fetches real-time weather from Open-Meteo API.
    Returns: rainfall, temperature, humidity
    """
    coords = DISTRICT_COORDS.get(district, DISTRICT_COORDS["Pune"])
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()["current"]
        return {
            "temperature": float(data["temperature_2m"]),
            "humidity": float(data["relative_humidity_2m"]),
            "rainfall": float(data["precipitation"])
        }
    except Exception as e:
        print(f"Weather API Error: {e}")
        # Fallback to reasonable defaults
        return {"temperature": 25.0, "humidity": 60.0, "rainfall": 0.0}
