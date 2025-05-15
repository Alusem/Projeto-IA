# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DiagnosisRequestData(BaseModel):
    # Estes virão como Form data junto com o arquivo
    exam_type: str  # e.g., "torax", "abdomen", "idade_ossea", "fraturas"
    patient_sex: Optional[str] = None # e.g., "feminino", "masculino" (relevante para idade óssea)
    # Para o tórax, o front-end pode enviar uma lista de doenças específicas para análise,
    # ou se não enviar, analisamos todas as configuradas para tórax.
    # Enviado como string JSON no Form data, pois listas não são bem suportadas diretamente.
    selected_diseases_json: Optional[str] = None # Ex: '["pneumonia", "derrame_pleural"]'


class AIServiceResult(BaseModel):
    condition_name: str
    probability: Optional[float] = None # Para classificações
    prediction_text: Optional[str] = None # Para resultados como idade óssea
    error: Optional[str] = None


class DiagnosisResponse(BaseModel):
    original_filename: str
    exam_type: str
    results: List[AIServiceResult]
    # Podemos incluir dados adicionais se necessário
    patient_sex_considered: Optional[str] = None