import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException

def get_db_connection():
    """
    Injeção de dependência para conexão com PostgreSQL.
    Gerencia o ciclo de vida da conexão para a Vercel.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            cursor_factory=RealDictCursor
        )
        yield conn
    except Exception as e:
        print(f"Erro Crítico - Conexão Banco: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    finally:
        if conn:
            conn.close()
            