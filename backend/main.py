import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Pointing the legacy 'main.py' to serve the new Modular API Layer
from api_layer.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api_layer.main:app", host="127.0.0.1", port=8000, reload=True)
