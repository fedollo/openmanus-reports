import os

from dotenv import load_dotenv
from telegram import Bot

# Carica le variabili d'ambiente
load_dotenv()


async def test_telegram():
    # Ottieni token e chat_id
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Errore: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID non trovati nel file .env")
        return

    try:
        # Inizializza il bot
        bot = Bot(token=token)

        # Invia un messaggio di test
        message = await bot.send_message(
            chat_id=chat_id,
            text="🟢 Test di connessione riuscito!\nIl bot è pronto per inviare segnali di trading.",
        )

        print("✅ Test completato con successo!")
        print(f"Messaggio inviato: {message.text}")

    except Exception as e:
        print(f"❌ Errore durante il test: {str(e)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_telegram())
