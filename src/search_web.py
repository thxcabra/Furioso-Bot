import json
import logging
import os
import requests
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carrega a chave da Tavily
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Carrega os links confiáveis a partir do base.json
BASE_PATH = Path(__file__).resolve().parent / "base.json"
try:
    with open(BASE_PATH, "r", encoding="utf-8") as f:
        base_data = json.load(f)
        fontes = base_data.get("fontes_confiaveis", {})
        # A Tavily filtra por domínio (include_domains), não por URL
        dominios_confiaveis = sorted({urlparse(u).netloc.removeprefix("www.") for u in fontes.values()})
        logger.info("Domínios confiáveis usados: %s", dominios_confiaveis)
except Exception:
    logger.exception("Erro ao carregar base.json")
    dominios_confiaveis = []

def buscar_conteudo_web(pergunta: str) -> str:
    try:
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": pergunta,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False,
            "include_domains": dominios_confiaveis,
            "max_results": 5
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        resposta = data.get("answer", "").strip()
        if resposta and len(resposta.split()) >= 10:
            logger.info("Tavily retornou resposta direta")
            return resposta

        logger.info("Tavily sem resposta direta. Buscando snippets...")
        for r in data.get("results", []):
            content = r.get("content", "")
            if "furia" in content.lower():
                logger.info("Usando snippet com menção à FURIA")
                return content.strip()

        logger.warning("Nenhuma resposta confiável encontrada")
        return "Não encontrei nada confiável agora. Melhor conferir no site oficial da FURIA."

    except Exception:
        logger.exception("Erro ao chamar Tavily")
        return "A web hoje não colaborou... mas tô pronto pra próxima!"
