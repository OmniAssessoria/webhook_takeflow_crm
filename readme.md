# Planejamento

## Ferramentas
Hospedagem: Vercel
Linguagem: Python
Banco: POstgress
Integração: CRM OMNI

## Estrutura projeto
webhook_disparo_takeflow
│
├── api/                        # Obrigatório para Vercel Serverless Functions
│   ├── index.py                # Ponto de entrada (App FastAPI e Rotas)
│   ├── dependencies.py         # Injeção de dependências (ex: validar token, injetar banco)
│   ├── schemas/                # Modelos Pydantic (validação de entrada/saída)
│   │   ├── __init__.py
│   │   └── webhooks.py         # Seu LeadWebhook ficará aqui
│   ├── services/               # Lógica de negócio (O seu OperadorCrm em TS vai virar Python aqui)
│   │   ├── __init__.py
│   │   ├── crm_service.py      # Funções como criar_lead, chamadas Axios -> Httpx
│   │   └── formatters.py       # Funções como limparPontuacao, formatarCPF, etc.
│   └── database/               # Camada de Dados (O seu DbConexao)
│       ├── __init__.py
│       ├── connection.py       # O pooler de conexão (crucial para serverless)
│       └── repository.py       # Consultas SQL (select, update, insert)
│
├── .env                        # Variáveis locais (Nunca faça commit)
├── .gitignore                  # Ignorar .env, venv/, __pycache__/
├── requirements.txt            # Dependências Python (fastapi, psycopg2-binary, httpx, etc)
├── vercel.json                 # Configuração de deploy da Vercel
└── README.md

## executar
python3 -m venv venv

source venv/bin/activate

uvicorn api.index:app --reload --port 8888
