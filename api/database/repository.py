from api.services.formatters import formatar_cnpj

class DbRepository:
    def __init__(self, conn):
        self.conn = conn

    def commit(self):
        self.conn.commit()

    def buscar_info_lead(self, cnpj_bruto: str, razao_bruta: str):
        cnpj_formatado = formatar_cnpj(cnpj_bruto)
        razao_maiuscula = str(razao_bruta).upper()

        with self.conn.cursor() as cur:
            query = """
            SELECT 
                -- 1. Dados Principais da Empresa (e)
                e.seq_empresa,
                e.cnpj,
                e.razao,
                e.seq_decisor,
                e.carteira,
                e.endereco,

                -- 2. Dados do Decisor (d)
                d.numero AS decisor_numero,
                d.google_fontes_emails,
                d.google_fontes_telefones,
                d.site_empresarial_telefones,
                d.site_empresarial_emails,

                -- 3. Subbusca: Serviços Claro (sc)
                (
                    SELECT jsonb_agg(jsonb_build_object(
                        'indicacao', sc.indicacao,
                        'observacao', sc.observacao,
                        'dt_fim_contrato', sc.dt_fim_contrato,
                        'classificacao_contrato', sc.classificacao_contrato,
                        'fixa', sc.fixa
                    ))
                    FROM omni.servico_claro sc
                    WHERE sc.seq_empresa = e.seq_empresa
                ) AS servicos_claro,

                -- 4. Subbusca: Serviços Operadora (so)
                (
                    SELECT jsonb_agg(jsonb_build_object(
                        'numero', so.numero_linha,
                        'plano', so.plano,
                        'valor', so.valor
                    ))
                    FROM omni.servico_operadora so
                    WHERE so.seq_empresa = e.seq_empresa
                ) AS servicos_operadora,

                -- 5. Subbusca: Disparos Whatsapp (dw) + Consultor (c)
                (
                    SELECT jsonb_agg(jsonb_build_object(
                        'numero_disparado', dw.numero,
                        'dt_disparo', dw.dt_disparo,
                        'seq_consultor', c.seq_consultor,
                        'email_consultor', c.email
                    ))
                    FROM omni.disparo_whatsapp dw
                    INNER JOIN omni.consultor c ON c.seq_consultor = dw.seq_consultor
                    WHERE dw.seq_empresa = e.seq_empresa
                ) AS historico_disparos

            FROM omni.empresa e
            LEFT JOIN omni.decisor d ON d.seq_decisor = e.seq_decisor
            WHERE e.cnpj = %s OR UPPER(e.razao) = %s;
            """
            cur.execute(query, (cnpj_formatado, razao_maiuscula))
            return cur.fetchone()

    def atualizar_lead_sucesso(self, seq_empresa: int, seq_consultor: int):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE omni.servico_claro 
                SET crm = true, seq_consultor = %s 
                WHERE seq_empresa = %s
            """, (seq_consultor, seq_empresa))
            self.commit()

    def atualizar_disparo_sucesso(self, seq_empresa: int):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE omni.disparo_whatsapp 
                SET situacao = 'SUCESSO' 
                WHERE seq_empresa = %s
            """, (seq_empresa,))
            self.commit()

    def atualizar_lead_falha(self, seq_empresa: int):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE omni.servico_claro 
                SET crm = false, seq_consultor = null 
                WHERE seq_empresa = %s
            """, (seq_empresa,))
            self.commit()

    def atualizar_disparo_falha(self, seq_empresa: int):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE omni.disparo_whatsapp 
                SET situacao = 'FALHA' 
                WHERE seq_empresa = %s
            """, (seq_empresa,))
            self.commit()

    def buscar_infor_consultor(self, seq_consultor: int):
        with self.conn.cursor() as cur:
            cur.execute("SELECT email FROM omni.consultor WHERE seq_consultor = %s", (seq_consultor,))
            return cur.fetchone()
