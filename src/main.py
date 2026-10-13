from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import logging
import os
import random
from dotenv import load_dotenv
from pathlib import Path

# Configurado antes dos módulos locais, que já registram logs ao serem importados
logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
# O httpx registra a URL de cada chamada à API do Telegram, que contém o token
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

from agent import responder_mensagem  # noqa: E402
from agenda import buscar_proximos_jogos  # noqa: E402

# Carrega variáveis de ambiente
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_firstname = update.effective_user.first_name
    msg = (
        f"Salve, {user_firstname}! 👊 Eu sou o FURIOSO, o bot mais apaixonado pela FURIA Esports.\n\n"
        "🔥 Pode me perguntar sobre qualquer coisa da FURIA: CS2, Valorant, LoL, R6, camisa nova, técnico, histórico... tudo mesmo!\n\n"
        "📌 Comandos disponíveis:\n"
        "• /menu → ver exemplos do que você pode perguntar\n"
        "• /agenda → próximos jogos da FURIA\n"
        "• /resenha → curiosidade ou zoeira aleatória do torcedor\n\n"
        "🗣️ Ou só manda tua pergunta direto aqui, como num grupo de torcida!\n"
        "Bora trocar essa ideia 🔥"
    )
    await update.message.reply_text(msg)

# Comando /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opcoes = (
        "🎯 O que você pode perguntar pro FURIOSO:\n\n"
        "📌 Escalações:\n"
        "- Quem tá na line do CS2?\n"
        "- Qual o time feminino do Valorant?\n\n"
        "📌 Técnicos e histórico:\n"
        "- Quem é o técnico do LoL?\n"
        "- Quais títulos a FURIA ganhou no R6?\n\n"
        "📌 Curiosidades e infos práticas:\n"
        "- Quando é o próximo jogo?\n"
        "- Tem camisa nova na loja?\n"
        "- Onde fica a Arena FURIA?\n\n"
        "👊 Pode perguntar tudo, na resenha ou na pressão!"
    )
    await update.message.reply_text(opcoes)

# Comando /agenda
async def agenda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        aguardando = await update.message.reply_text("⏳ Deixa eu puxar os jogos da semana...")

        resposta = buscar_proximos_jogos()
        await update.message.reply_text(resposta)
        await aguardando.delete()

    except Exception:
        logger.exception("Erro no comando /agenda")
        await update.message.reply_text("⚠️ Não consegui puxar a tabela agora... Mas tamo em campo sempre!")

# Comando /resenha
async def resenha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resenhas = [
        "O dia que o chelo fizer clutch de scout eu tatuo o logo da FURIA na testa 😤",
        "FURIA no Major é tipo final de novela: a gente grita, sofre, chora e acredita até o fim.",
        "Lembro daquele 16x2 que a gente passou o trator. O adversário deve tá traumatizado até hoje 😂",
        "Se o arT rushar mid no primeiro round, é porque hoje tem massacre 🔥",
        "Tem jogo da FURIA hoje? Já separei energético, camisa e grito entalado 😤",
        "A torcida da FURIA empurra até no Discord, irmão. Aqui é grito no fone e alma no clutch!",
    ]
    await update.message.reply_text(random.choice(resenhas))

# Handler para mensagens comuns
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text
        user_id = update.effective_user.id
        logger.info("[%s] Pergunta: %s", user_id, user_input)

        carregando_msg = await update.message.reply_text("⏳ Calma aí que tô puxando essa info...")

        resposta = responder_mensagem(user_input)
        await update.message.reply_text(resposta)
        await carregando_msg.delete()

    except Exception:
        logger.exception("Erro no handle_message")
        await update.message.reply_text("⚠️ Deu ruim aqui, mas logo volto com a zoeira 🔧")

# Inicializa o bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("agenda", agenda))
    app.add_handler(CommandHandler("resenha", resenha))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot está rodando... Ctrl+C para parar.")
    app.run_polling()

if __name__ == "__main__":
    main()
