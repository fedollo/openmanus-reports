import uvicorn
from app.main import app
from app.trading_bot import main as trading_bot_main
import asyncio
import threading

def run_trading_bot():
    asyncio.run(trading_bot_main())

if __name__ == "__main__":
    # Avvia il bot di trading in un thread separato
    trading_bot_thread = threading.Thread(target=run_trading_bot)
    trading_bot_thread.daemon = True
    trading_bot_thread.start()

    # Avvia il server FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000) 