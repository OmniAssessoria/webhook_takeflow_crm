from pydantic import BaseModel
from typing import Optional

class LeadWebhook(BaseModel):
    numero: str
    razao_cnpj: str
    pipeline_id: str
    stage_id: str
    