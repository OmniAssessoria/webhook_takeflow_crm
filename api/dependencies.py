import os
from fastapi import Header, HTTPException

TOKEN_WEBHOOK = os.environ.get("TOKEN_WEBHOOK")

def validar_token(token_req: str = Header(..., alias="Authorization")):
    """
    Valida o token fixo vindo do header. 
    Aceita 'Bearer <TOKEN>' ou apenas '<TOKEN>'.
    """
    token_limpo = token_req.replace("Bearer ", "")
    if token_limpo != str(TOKEN_WEBHOOK):
        raise HTTPException(status_code=401, detail="Token Inválido")
    return True
