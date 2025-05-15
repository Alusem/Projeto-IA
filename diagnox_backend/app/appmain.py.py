# app/main.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Para permitir requisições do front-end
from typing import Optional

from .schemas import DiagnosisResponse, DiagnosisRequestData
from .services import process_diagnosis
from .config import settings # Importa settings para que seja inicializado

app = FastAPI(title="Diagnox Backend API")

# Configuração do CORS (Cross-Origin Resource Sharing)
# Permite que seu front-end (rodando em localhost:3000, por exemplo) chame este backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, restrinja para os domínios do seu front-end
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_image_endpoint(
    # Os campos do DiagnosisRequestData são passados como Form data
    exam_type: str = Form(...),
    patient_sex: Optional[str] = Form(None),
    selected_diseases_json: Optional[str] = Form(None), # String JSON
    image: UploadFile = File(...)
):
    """
    Recebe uma imagem e os parâmetros do exame, encaminha para os
    serviços de IA apropriados e retorna os resultados consolidados.
    """
    # Validar os dados do formulário usando o Pydantic model (opcional, mas bom)
    try:
        request_data = DiagnosisRequestData(
            exam_type=exam_type,
            patient_sex=patient_sex,
            selected_diseases_json=selected_diseases_json
        )
    except Exception as e: # PydanticValidationError
        raise HTTPException(status_code=422, detail=str(e))

    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Apenas imagens são permitidas.")

    ai_results = await process_diagnosis(
        exam_type=request_data.exam_type,
        image_file=image,
        patient_sex=request_data.patient_sex,
        selected_diseases_json=request_data.selected_diseases_json
    )

    return DiagnosisResponse(
        original_filename=image.filename,
        exam_type=request_data.exam_type,
        results=ai_results,
        patient_sex_considered=request_data.patient_sex if request_data.exam_type == "idade_ossea" else None
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Diagnox Backend is running!"}

# Para rodar: uvicorn app.main:app --reload --port 8000
# (execute de dentro do diretório diagnox_backend/)