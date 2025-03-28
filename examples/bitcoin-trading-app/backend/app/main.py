from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.dashboard import DASHBOARD_HTML, websocket_endpoint, active_connections, bot_state, update_bot_state
import random
from datetime import datetime
import asyncio
import threading
import time
import pandas as pd
from .backtest import Backtest
from typing import Dict, List

app = FastAPI(
    title="Bitcoin Trading Bot",
    description="API per il trading automatico di Bitcoin",
    version="1.0.0",
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specificare i domini consentiti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variabile per controllare il thread dei segnali di test
test_signals_running = False

async def send_update_to_clients():
    for connection in active_connections:
        try:
            await connection.send_json(bot_state)
        except:
            active_connections.remove(connection)

def generate_test_signals():
    global test_signals_running
    while test_signals_running:
        current_price = random.uniform(60000, 70000)
        signal_type = random.choice(["LONG", "SHORT"])
        
        signal = {
            "type": signal_type,
            "price": current_price,
            "stop_loss": current_price * (0.98 if signal_type == "LONG" else 1.02),
            "take_profit_1": current_price * (1.02 if signal_type == "LONG" else 0.98),
            "take_profit_2": current_price * (1.04 if signal_type == "LONG" else 0.96),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Aggiorna lo stato del bot con il nuovo segnale
        if "signals" not in bot_state:
            bot_state["signals"] = []
        bot_state["signals"].append(signal)
        if len(bot_state["signals"]) > 10:
            bot_state["signals"] = bot_state["signals"][-10:]
        
        bot_state["price"] = current_price
        bot_state["performance"] = {
            "total_signals": len(bot_state["signals"]),
            "successful_trades": random.randint(0, len(bot_state["signals"])),
            "win_rate": random.randint(50, 80)
        }

        # Crea un nuovo event loop per l'invio asincrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_update_to_clients())
        loop.close()
        
        time.sleep(10)  # Genera un nuovo segnale ogni 10 secondi

@app.get("/", response_class=HTMLResponse)
async def root():
    return DASHBOARD_HTML


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "exchange": "connected"}


@app.get("/start-test-signals")
async def start_test_signals():
    global test_signals_running
    if not test_signals_running:
        test_signals_running = True
        threading.Thread(target=generate_test_signals, daemon=True).start()
        return {"status": "Test signals started"}
    return {"status": "Test signals already running"}


@app.get("/stop-test-signals")
async def stop_test_signals():
    global test_signals_running
    test_signals_running = False
    return {"status": "Test signals stopped"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
            # Invia lo stato corrente del bot
            await websocket.send_json(bot_state)
    except:
        active_connections.remove(websocket)

@app.post("/api/backtest")
async def run_backtest(data: Dict):
    try:
        # Converti i dati in DataFrame
        historical_data = pd.DataFrame(data['historical_data'])
        signals = pd.DataFrame(data['signals'])
        
        # Esegui il backtest
        backtest = Backtest()
        results = backtest.run(historical_data, signals)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
