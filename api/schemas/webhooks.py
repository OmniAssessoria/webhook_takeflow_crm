from pydantic import BaseModel

class LeadWebhook(BaseModel):
    numero: str
    razao_cnpj: str  
    