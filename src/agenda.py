import re
from search_web import buscar_conteudo_web

def extrair_jogos(texto: str) -> str:
    """
    Extrai datas, adversários e horários de texto.
    Retorna resumo amigável.
    """
    linhas = texto.split("\n")
    eventos = []

    for linha in linhas:
        data = re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", linha)
        hora = re.search(r"\d{1,2}h\d{0,2}", linha)
        adversario = re.search(r"contra\s+([A-Z][a-zA-Z0-9\s]*)", linha)

        if data or hora or adversario:
            parte = []
            if data:
                parte.append(f"📅 {data.group()}")
            if hora:
                parte.append(f"🕒 {hora.group()}")
            if adversario:
                parte.append(f"⚔️ vs {adversario.group(1).strip()}")
            eventos.append(" | ".join(parte))

    if not eventos:
        return "Não achei nada certo na agenda ainda, mas fica de olho nos stories da FURIA!"

    return "\n\n".join(eventos[:3])  # Mostra no máximo 3 próximos jogos

def buscar_proximos_jogos() -> str:
    """
    Usa Tavily para buscar jogos futuros da FURIA.
    """
    consulta = "próximos jogos da FURIA Esports CS2 e Valorant"
    resultado = buscar_conteudo_web(consulta)
    return extrair_jogos(resultado)