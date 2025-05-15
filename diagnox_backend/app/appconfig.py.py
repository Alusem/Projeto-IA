# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Exemplo para serviços de Tórax
    AI_PNEUMONIA_URL: str = "http://localhost:8001/predict/pneumonia"
    AI_DERRAME_PLEURAL_URL: str = "http://localhost:8002/predict/pleural_effusion"
    AI_PNEUMOTORAX_URL: str = "http://localhost:8003/predict/pneumothorax"
    AI_EDEMA_PULMONAR_URL: str = "http://localhost:8004/predict/pulmonary_edema"

    # Exemplo para Abdômen
    AI_ABDOMEN_MODELO1_URL: str = "http://localhost:8005/predict/abdomen_tipo1"
    AI_ABDOMEN_MODELO2_URL: str = "http://localhost:8006/predict/abdomen_tipo2"

    # Exemplo para Idade Óssea
    AI_IDADE_OSSEA_URL: str = "http://localhost:8007/predict/bone_age"

    # Exemplo para Fraturas
    AI_FRATURAS_URL: str = "http://localhost:8008/predict/fracture"

    # Mapeamento de tipos de exame para os modelos de IA relevantes
    # Cada chave é o 'exam_type' vindo do front-end.
    # O valor é um dicionário onde a chave é o nome da condição/modelo e o valor é o atributo da URL em Settings.
    EXAM_AI_MAPPING: dict = {
        "torax": {
            "pneumonia": "AI_PNEUMONIA_URL",
            "derrame_pleural": "AI_DERRAME_PLEURAL_URL",
            "pneumotorax": "AI_PNEUMOTORAX_URL",
            "edema_pulmonar": "AI_EDEMA_PULMONAR_URL",
        },
        "abdomen": {
            "modelo1_abdomen": "AI_ABDOMEN_MODELO1_URL",
            "modelo2_abdomen": "AI_ABDOMEN_MODELO2_URL",
        },
        "idade_ossea": {
            "default": "AI_IDADE_OSSEA_URL",
        },
        "fraturas": {
            "default": "AI_FRATURAS_URL",
        }
    }

    class Config:
        env_file = ".env" # Carrega variáveis de um arquivo .env se existir
        extra = 'ignore'

settings = Settings()