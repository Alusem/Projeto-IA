from fastapi import FastAPI, File, UploadFile, Form
import time
import random

app = FastAPI()

@app.post("/predict/pneumonia")
async def predict_pneumonia(image: UploadFile = File(...)):
    # Simula algum processamento
    time.sleep(random.uniform(0.5, 1.5))
    probability = random.uniform(0.05, 0.95)
    print(f"Mock Pneumonia Service: Received {image.filename}, predicting {probability*100:.2f}%")
    return {"condition_name": "pneumonia", "probability": probability}

# Para rodar: uvicorn mock_ai_services.mock_pneumonia_service:app --port 8001