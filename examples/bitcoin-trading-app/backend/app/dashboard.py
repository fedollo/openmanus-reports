import asyncio
import json
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from plotly.subplots import make_subplots

app = FastAPI()

# Stato globale del bot
bot_state = {
    "price": None,
    "signals": [],
    "performance": {"total_signals": 0, "successful_trades": 0, "win_rate": 0},
}

# Lista delle connessioni WebSocket attive
active_connections = []

# HTML per la dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Bitcoin Trading Bot Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-container {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .signals {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .signal {
            border-bottom: 1px solid #eee;
            padding: 10px 0;
        }
        .signal:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bitcoin Trading Bot Dashboard</h1>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Prezzo Bitcoin</h3>
                <p id="price">Caricamento...</p>
            </div>
            <div class="stat-card">
                <h3>Segnali Totali</h3>
                <p id="total-signals">0</p>
            </div>
            <div class="stat-card">
                <h3>Win Rate</h3>
                <p id="win-rate">0%</p>
            </div>
        </div>

        <div class="chart-container">
            <h3>Prezzo Bitcoin</h3>
            <div id="price-chart"></div>
        </div>

        <div class="signals">
            <h3>Ultimi Segnali</h3>
            <div id="signals-list"></div>
        </div>
    </div>

    <script>
        let ws = new WebSocket("ws://" + window.location.host + "/ws");
        let priceData = [];

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        function updateDashboard(data) {
            // Aggiorna prezzo
            document.getElementById("price").textContent =
                data.price ? "$" + data.price.toLocaleString() : "N/A";

            // Aggiorna statistiche
            document.getElementById("total-signals").textContent =
                data.performance.total_signals;
            document.getElementById("win-rate").textContent =
                data.performance.win_rate + "%";

            // Aggiorna grafico
            if (data.price) {
                priceData.push({
                    time: new Date(),
                    price: data.price
                });
                if (priceData.length > 100) priceData.shift();
                updateChart();
            }

            // Aggiorna lista segnali
            const signalsList = document.getElementById("signals-list");
            signalsList.innerHTML = data.signals.map(signal => `
                <div class="signal">
                    <strong>${signal.type}</strong> - ${signal.timestamp}<br>
                    Prezzo: $${signal.price.toLocaleString()}<br>
                    Stop Loss: $${signal.stop_loss.toLocaleString()}<br>
                    Take Profit 1: $${signal.take_profit_1.toLocaleString()}<br>
                    Take Profit 2: $${signal.take_profit_2.toLocaleString()}
                </div>
            `).join("");
        }

        function updateChart() {
            const times = priceData.map(d => d.time);
            const prices = priceData.map(d => d.price);

            const trace = {
                x: times,
                y: prices,
                type: 'scatter',
                mode: 'lines',
                name: 'Prezzo Bitcoin'
            };

            const layout = {
                title: 'Prezzo Bitcoin in Tempo Reale',
                xaxis: { title: 'Tempo' },
                yaxis: { title: 'Prezzo (USD)' },
                height: 400
            };

            Plotly.newPlot('price-chart', [trace], layout);
        }

        // Richiedi aggiornamenti ogni 5 secondi
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send("update");
            }
        }, 5000);
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return DASHBOARD_HTML


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Gestisce le connessioni WebSocket per gli aggiornamenti in tempo reale"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)


def update_bot_state(price=None, signals=None, performance=None):
    """Aggiorna lo stato globale del bot"""
    global bot_state
    if price is not None:
        bot_state["price"] = price
    if signals is not None:
        bot_state["signals"] = signals
    if performance is not None:
        bot_state["performance"] = performance
