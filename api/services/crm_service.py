import httpx
import os
import json
from datetime import datetime

URL_OMNI_API = os.environ.get("CRM_API")
TOKEN_AXION = os.environ.get("TOKEN_CRM") 
PIPELINE_ID = os.environ.get("CRM_FUNIL_ID") 
STAGE_ID = os.environ.get("CRM_ETAPA_ID") 

def log_sync(mensagem: str):
    """Função simples para padronizar os logs com Data e Hora"""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{agora}] {mensagem}")

async def criar_lead_crm(empresa_dados: dict):
    """
    Monta o payload estrito com os dados que devem subir, 
    atribuindo o lead ao consultor que fez o disparo.
    """
    log_sync(f"Iniciando montagem de payload para CRM. Empresa: {empresa_dados.get('razao')}")
    
    contacts_payload = []
    linhas_dados = empresa_dados.get("servicos_operadora") or []
    if linhas_dados:
        contacts_payload.append({
            "name": "Linhas móveis da Empresa",
            "roleHint": "Linhas móveis Operadora",
            "isPrimary": True,
            "isDecisionMaker": False,
            "phones": [{"number": l.get('numero'), "label": l.get('plano', 'Linha')} for l in linhas_dados if l.get('numero')]
        })

    historico = empresa_dados.get("historico_disparos") or []
    email_responsavel = None
    if historico and len(historico) > 0:
        email_responsavel = historico[0].get("email_consultor")
        log_sync(f"Consultor identificado no histórico: {email_responsavel}")
    else:
        log_sync("Nenhum consultor encontrado no histórico de disparos.")

    servicos_claro = empresa_dados.get("servicos_claro") or []
    dt_fim_contrato = ""
    dt_inicio_contrato = "" 
    tempo_contrato = ""
    fixa = ""
    indicacao = ""
    observacao_servico = ""
    
    if servicos_claro and len(servicos_claro) > 0:
        servico_principal = servicos_claro[0]
        dt_fim_contrato = servico_principal.get('dt_fim_contrato') or ""
        fixa = servico_principal.get('fixa') or ""
        indicacao = servico_principal.get('indicacao') or ""
        observacao_servico = servico_principal.get('observacao') or ""

    info_decisor_str = ""
    decisor_numero = empresa_dados.get('decisor_numero')
    if decisor_numero:
        info_decisor_str = f"TELEFONES: {decisor_numero}"

    custom_fields = {
        "Origem": "Disparos Takeflow",
        "Endereço": empresa_dados.get("endereco") or "",
        "Carteira": empresa_dados.get("carteira") or "",
        "Observação de Disparo": "Lead gerado automaticamente por webhook.",
        "Inicio do Contrato": dt_inicio_contrato,
        "Final do Contrato": dt_fim_contrato,
        "Tempo de Contrato": tempo_contrato,
        "FIXA": fixa,
        "Observacao": observacao_servico,
        "Indicacao": indicacao,
        "Informações DECISOR (Possível decisor)": info_decisor_str,
        "Google Fontes Telefones": empresa_dados.get("google_fontes_telefones") or "",
        "Google Fontes Emails": empresa_dados.get("google_fontes_emails") or "",
        "Emails (Site da Empresa)": empresa_dados.get("site_empresarial_emails") or "",
        "Telefones (Site da Empresa)": empresa_dados.get("site_empresarial_telefones") or ""
    }
    
    custom_fields_limpo = {k: v for k, v in custom_fields.items() if v != ""}
    payload_creation = {
        "companyName": empresa_dados.get("razao"),
        "companyCnpj": empresa_dados.get("cnpj"),
        "value": 0,
        "pipelineId": PIPELINE_ID,
        "stageId": STAGE_ID,  
        "customFields": json.dumps(custom_fields_limpo),
        "contacts": contacts_payload
    }
    
    if email_responsavel:
        payload_creation["user"] = email_responsavel

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{URL_OMNI_API}/deals",
                json=payload_creation,
                headers={
                    "Authorization": f"Bearer {TOKEN_AXION}",
                    "Content-Type": "application/json"
                },
                timeout=15.0
            )
    
            response.raise_for_status() 
            deal_id = response.json().get("data", {}).get("id")

            if not deal_id:
                raise Exception("A API do CRM retornou 200, mas não enviou o ID do negócio criado (deal_id).")
                
            log_sync(f"Lead criado com sucesso no CRM. ID Retornado: {deal_id}")
            return deal_id
        
        except httpx.HTTPStatusError as e:
            log_sync(f"ERRO HTTP (CRM Rejeitou a requisição): {e.response.text}")
            raise Exception("Falha ao criar lead no CRM")
        except Exception as e:
            log_sync(f"ERRO DE SISTEMA/REDE: {e}")
            raise Exception("Erro de rede ao conectar ao CRM")
        