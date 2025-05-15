from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import time
import random

app = FastAPI()

@app.post("/predict/bone_age")
async def predict_bone_age(image: UploadFile = File(...), sex: Optional[str] = Form(None)):
    # Simula algum processamento
    time.sleep(random.uniform(1, 2))
    age = random.randint(5, 15)
    sex_info = f"para o sexo {sex}" if sex else "sem informação de sexo"
    prediction_text = f"Idade óssea compatível com {age} anos, {sex_info} (mock)."
    print(f"Mock Bone Age Service: Received {image.filename}, Sex: {sex}, predicting: {prediction_text}")
    return {"condition_name": "idade_ossea", "prediction_text": prediction_text}

# Para rodar: uvicorn mock_ai_services.mock_bone_age_service:app --port 8007