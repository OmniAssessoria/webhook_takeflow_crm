import re

def limpar_pontuacao(texto: str) -> str:
    """Remove qualquer caractere que não seja número."""
    if not texto:
        return ""
    return re.sub(r'\D', '', str(texto))

def formatar_cpf(cpf: str) -> str:
    limpo = limpar_pontuacao(cpf)
    if len(limpo) != 11:
        return limpo
    return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{2})', r'\1.\2.\3-\4', limpo)

def formatar_cnpj(cnpj: str) -> str:
    limpo = limpar_pontuacao(cnpj)
    if len(limpo) != 14:
        return limpo
    return re.sub(r'(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})', r'\1.\2.\3/\4-\5', limpo)

def formatar_telefone(numero: str) -> str:
    limpo = limpar_pontuacao(numero)
    if len(limpo) < 10 or len(limpo) > 11:
        return limpo
    
    ddd = limpo[:2]
    resto = limpo[2:]
    
    if len(resto) == 9:
        return f"+55 ({ddd}) {resto[:5]}-{resto[5:]}"
    return f"+55 ({ddd}) {resto[:4]}-{resto[4:]}"
