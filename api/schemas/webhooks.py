from pydantic import BaseModel

class LeadWebhook(BaseModel):
    numero: str
    cnpj: str
    razao: str
