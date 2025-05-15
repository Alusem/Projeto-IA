# app/services.py
import httpx
import asyncio
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any, Optional
import json # Para parsear selected_diseases_json

from .config import settings
from .schemas import AIServiceResult

async def call_ai_service(
    service_name: str,
    url: str,
    image_bytes: bytes,
    filename: str,
    additional_params: Optional[Dict[str, Any]] = None
) -> AIServiceResult:
    """
    Chama um único serviço de IA de forma assíncrona.
    Espera-se que o serviço de IA aceite 'multipart/form-data' com um campo 'image'.
    """
    files = {'image': (filename, image_bytes, 'image/jpeg')} # Ou 'image/png', etc.
    data_payload = additional_params if additional_params else {}

    async with httpx.AsyncClient(timeout=60.0) as client: # Timeout de 60s
        try:
            print(f"Calling AI service: {service_name} at {url} with params: {data_payload}")
            response = await client.post(url, files=files, data=data_payload)
            response.raise_for_status()  # Levanta exceção para respostas 4xx/5xx
            
            # Adapte esta parte conforme a resposta esperada do seu serviço de IA
            # Exemplo: {"condition_name": "pneumonia", "probability": 0.87}
            # Ou: {"prediction_text": "Idade óssea compatível com 10 anos..."}
            ai_response_data = response.json()

            return AIServiceResult(
                condition_name=ai_response_data.get("condition_name", service_name), # usa service_name como fallback
                probability=ai_response_data.get("probability"),
                prediction_text=ai_response_data.get("prediction_text")
            )
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP error {e.response.status_code} calling {service_name}: {e.response.text}"
            print(error_detail)
            return AIServiceResult(condition_name=service_name, error=error_detail)
        except httpx.RequestError as e:
            error_detail = f"Request error calling {service_name}: {str(e)}"
            print(error_detail)
            return AIServiceResult(condition_name=service_name, error=error_detail)
        except Exception as e: # Captura outros erros como JSONDecodeError
            error_detail = f"Unexpected error processing response from {service_name}: {str(e)}"
            print(error_detail)
            return AIServiceResult(condition_name=service_name, error=error_detail)


async def process_diagnosis(
    exam_type: str,
    image_file: UploadFile,
    patient_sex: Optional[str] = None,
    selected_diseases_json: Optional[str] = None
) -> List[AIServiceResult]:
    """
    Orquestra as chamadas para os serviços de IA relevantes.
    """
    if exam_type not in settings.EXAM_AI_MAPPING:
        raise HTTPException(status_code=400, detail=f"Tipo de exame '{exam_type}' não suportado.")

    ai_tasks = []
    image_bytes = await image_file.read()
    
    # Parsear selected_diseases_json se existir
    selected_diseases_list: Optional[List[str]] = None
    if selected_diseases_json:
        try:
            selected_diseases_list = json.loads(selected_diseases_json)
            if not isinstance(selected_diseases_list, list):
                raise ValueError("selected_diseases_json must be a JSON list of strings")
            for item in selected_diseases_list:
                if not isinstance(item, str):
                    raise ValueError("All items in selected_diseases_json list must be strings")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Formato inválido para selected_diseases_json: {e}")


    service_config_for_exam = settings.EXAM_AI_MAPPING[exam_type]
    
    for service_name, setting_attr_name in service_config_for_exam.items():
        # Se for tórax e houver doenças selecionadas, só chama os serviços selecionados
        if exam_type == "torax" and selected_diseases_list and service_name not in selected_diseases_list:
            continue

        service_url = getattr(settings, setting_attr_name, None)
        if not service_url:
            print(f"Aviso: URL para o serviço '{service_name}' (atributo '{setting_attr_name}') não configurada.")
            continue

        additional_params = {}
        if exam_type == "idade_ossea" and patient_sex:
            # Supõe que o serviço de IA de idade óssea aceita um parâmetro 'sex'
            additional_params["sex"] = patient_sex
        
        # Adicione aqui outros parâmetros específicos que cada IA possa precisar
        # Ex: additional_params["some_other_param"] = "value"

        ai_tasks.append(
            call_ai_service(service_name, service_url, image_bytes, image_file.filename, additional_params)
        )

    if not ai_tasks:
        if exam_type == "torax" and selected_diseases_list:
            raise HTTPException(status_code=400, detail=f"Nenhuma das doenças selecionadas ({selected_diseases_list}) está configurada para análise.")
        else:
            raise HTTPException(status_code=500, detail=f"Nenhum serviço de IA configurado ou selecionado para o tipo de exame '{exam_type}'.")

    results = await asyncio.gather(*ai_tasks)
    return results