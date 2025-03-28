import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot

# Carica le variabili d'ambiente
load_dotenv()


async def get_chat_id():
    # Ottieni il token
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato nel file .env")
        return

    try:
        # Inizializza il bot
        bot = Bot(token=token)

        # Ottieni le informazioni del bot
        bot_info = await bot.get_me()
        print(f"\nBot info:")
        print(f"Username: @{bot_info.username}")
        print(f"Name: {bot_info.first_name}")

        # Ottieni gli aggiornamenti
        updates = await bot.get_updates()

        if updates:
            print("\nChat IDs trovati:")
            for update in updates:
                if update.message:
                    chat_id = update.message.chat.id
                    username = update.message.from_user.username
                    print(f"Chat ID: {chat_id}")
                    print(f"Username: @{username}")
                    print("---")
        else:
            print("\nNessun messaggio trovato. Invia un messaggio al bot e riprova.")

    except Exception as e:
        print(f"❌ Errore: {str(e)}")


if __name__ == "__main__":
    asyncio.run(get_chat_id())
