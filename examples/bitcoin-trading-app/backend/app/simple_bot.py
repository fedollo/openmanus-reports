import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Carica le variabili d'ambiente
load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Ciao! Il tuo Chat ID è: {update.effective_chat.id}\n"
        "Usa questo ID nel file .env come TELEGRAM_CHAT_ID"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Il tuo Chat ID è: {update.effective_chat.id}\n"
        "Usa questo ID nel file .env come TELEGRAM_CHAT_ID"
    )


def main():
    # Ottieni il token
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato nel file .env")
        return

    # Crea l'applicazione
    application = Application.builder().token(token).build()

    # Aggiungi i gestori
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Avvia il bot
    print("Bot avviato! Invia un messaggio al bot per ottenere il tuo Chat ID")
    application.run_polling()


if __name__ == "__main__":
    main()
