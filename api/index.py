from fastapi import FastAPI, Depends
from dotenv import load_dotenv 

load_dotenv() 

from api.schemas.webhooks import LeadWebhook
from api.dependencies import validar_token
from api.database.connection import get_db_connection
from api.database.repository import DbRepository
from api.services.crm_service import criar_lead_crm

app = FastAPI(title="Webhook Takeflow Integrador")

@app.post("/webhook/lead")
async def processar_lead(
    lead: LeadWebhook, 
    token_valido: bool = Depends(validar_token),
    db_conn = Depends(get_db_connection) 
):
    try:
        repo = DbRepository(db_conn)
        info_empresa = repo.buscar_info_lead(lead.cnpj, lead.razao)
        
        if not info_empresa:
             return {"status": False, "mensagem": "Empresa não encontrada no banco."}
         
        historico = info_empresa.get("historico_disparos") or []
        seq_consultor = historico[0].get("seq_consultor") if historico else None
        deal_id = await criar_lead_crm(info_empresa)
        
        if seq_consultor:
            repo.atualizar_lead_sucesso(info_empresa['seq_empresa'], seq_consultor) 
        
        repo.atualizar_disparo_sucesso(info_empresa['seq_empresa']) 
        
        return {
            "status": True, 
            "mensagem": f"Sucesso ao criar lead (ID: {deal_id}), transferir contato e atualizar status disparo."
        }
    
    except Exception as e:
        if 'info_empresa' in locals() and info_empresa:
            repo.atualizar_lead_falha(info_empresa['seq_empresa']) 
            repo.atualizar_disparo_falha(info_empresa['seq_empresa']) 
            
        print(f"Erro Crítico no processamento: {str(e)}")
        return {"status": False, "mensagem": f"Falha sistêmica no processamento: {str(e)}"}

@app.post("/webhook/lead-declinar")
async def declinar_lead(
    lead: LeadWebhook, 
    token_valido: bool = Depends(validar_token),
    db_conn = Depends(get_db_connection)
):
    try:
        repo = DbRepository(db_conn)
        info_empresa = repo.buscar_info_lead(lead.cnpj, lead.razao)
        
        if info_empresa:
            repo.atualizar_disparo_falha(info_empresa['seq_empresa'])
            repo.atualizar_lead_falha(info_empresa['seq_empresa'])
            
        return {"status": True, "mensagem": "Situação de disparo inativada/salva com sucesso."}
    except Exception as e:
        return {"status": False, "mensagem": f"Falha: {str(e)}"}

@app.get("/webhook/exec-status")
async def validar_api_status(token_valido: bool = Depends(validar_token)):
    """Rota direta para testar estabilidade do host Vercel e validade de Token"""
    return {"status": "ok", "mensagem": "Webhook Serverless Online."}
