import asyncio
import os
from datetime import datetime

import ccxt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from telegram import Bot

from app.dashboard import update_bot_state

# Carica le variabili d'ambiente
load_dotenv()


class BitcoinTradingBot:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.binance_api_key = os.getenv("BINANCE_API_KEY")
        self.binance_api_secret = os.getenv("BINANCE_API_SECRET")

        # Inizializza l'exchange
        self.exchange = ccxt.binance(
            {
                "apiKey": self.binance_api_key,
                "secret": self.binance_api_secret,
                "enableRateLimit": True,
            }
        )

        # Parametri di trading
        self.leverage = int(os.getenv("LEVERAGE", "5"))
        self.stop_loss_percentage = float(os.getenv("STOP_LOSS_PERCENTAGE", "2"))
        self.take_profit_1_percentage = float(
            os.getenv("TAKE_PROFIT_1_PERCENTAGE", "2")
        )
        self.take_profit_2_percentage = float(
            os.getenv("TAKE_PROFIT_2_PERCENTAGE", "4")
        )

        # Inizializza il bot Telegram
        self.telegram_bot = Bot(token=self.telegram_token)

        # Stato del bot
        self.signals = []
        self.performance = {"total_signals": 0, "successful_trades": 0, "win_rate": 0}

    async def send_telegram_message(self, message: str):
        """Invia un messaggio su Telegram"""
        try:
            await self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id, text=message
            )
        except Exception as e:
            print(f"Errore nell'invio del messaggio Telegram: {str(e)}")

    def calculate_rsi(self, data, periods=14):
        """Calcola il RSI"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_ema(self, data, periods):
        """Calcola l'EMA"""
        return data.ewm(span=periods, adjust=False).mean()

    def calculate_bollinger_bands(self, data, window=20, num_std=2):
        """Calcola le Bollinger Bands"""
        rolling_mean = data.rolling(window=window).mean()
        rolling_std = data.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band

    def get_bitcoin_data(self):
        """Ottiene i dati di Bitcoin da Binance"""
        try:
            # Ottieni i dati OHLCV
            ohlcv = self.exchange.fetch_ohlcv("BTC/USDT", timeframe="4h", limit=100)

            # Crea DataFrame
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

            # Converti timestamp in datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # Calcola indicatori
            df["rsi"] = self.calculate_rsi(df["close"])
            df["ema_20"] = self.calculate_ema(df["close"], 20)
            df["ema_50"] = self.calculate_ema(df["close"], 50)

            # Bollinger Bands
            df["bb_upper"], df["bb_lower"] = self.calculate_bollinger_bands(df["close"])

            return df

        except Exception as e:
            print(f"Errore nel recupero dei dati: {str(e)}")
            return None

    def analyze_market(self, df):
        """Analizza il mercato e genera segnali"""
        if df is None or len(df) < 50:
            return None

        current_price = df["close"].iloc[-1]
        current_rsi = df["rsi"].iloc[-1]
        current_ema_20 = df["ema_20"].iloc[-1]
        current_ema_50 = df["ema_50"].iloc[-1]
        current_bb_upper = df["bb_upper"].iloc[-1]
        current_bb_lower = df["bb_lower"].iloc[-1]

        # Analisi trend
        trend = "ribassista" if current_ema_20 < current_ema_50 else "rialzista"

        # Genera segnali
        signal = None
        if (
            trend == "ribassista"
            and current_rsi > 70
            and current_price > current_bb_upper
        ):
            signal = {
                "type": "SHORT",
                "price": current_price,
                "stop_loss": current_price * (1 + self.stop_loss_percentage / 100),
                "take_profit_1": current_price
                * (1 - self.take_profit_1_percentage / 100),
                "take_profit_2": current_price
                * (1 - self.take_profit_2_percentage / 100),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        elif (
            trend == "rialzista"
            and current_rsi < 30
            and current_price < current_bb_lower
        ):
            signal = {
                "type": "LONG",
                "price": current_price,
                "stop_loss": current_price * (1 - self.stop_loss_percentage / 100),
                "take_profit_1": current_price
                * (1 + self.take_profit_1_percentage / 100),
                "take_profit_2": current_price
                * (1 + self.take_profit_2_percentage / 100),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        return signal

    async def run(self):
        """Esegue il bot di trading"""
        print("Bot di trading avviato...")
        await self.send_telegram_message(
            "🤖 Bot di trading avviato e pronto per l'analisi!"
        )

        while True:
            try:
                # Ottieni e analizza i dati
                df = self.get_bitcoin_data()
                signal = self.analyze_market(df)

                if signal:
                    # Aggiungi il segnale alla lista
                    self.signals.append(signal)
                    self.performance["total_signals"] += 1

                    # Formatta il messaggio
                    message = (
                        f"🎯 NUOVO SEGNALE DI TRADING\n\n"
                        f"Tipo: {signal['type']}\n"
                        f"Prezzo: ${signal['price']:,.2f}\n"
                        f"Stop Loss: ${signal['stop_loss']:,.2f}\n"
                        f"Take Profit 1: ${signal['take_profit_1']:,.2f}\n"
                        f"Take Profit 2: ${signal['take_profit_2']:,.2f}\n\n"
                        f"⚠️ Ricorda di gestire il rischio!"
                    )

                    # Invia il segnale
                    await self.send_telegram_message(message)

                # Aggiorna lo stato per la dashboard
                current_price = df["close"].iloc[-1] if df is not None else None
                update_bot_state(
                    price=current_price,
                    signals=self.signals[-10:],  # Ultimi 10 segnali
                    performance=self.performance,
                )

                # Attendi 5 minuti prima della prossima analisi
                await asyncio.sleep(300)

            except Exception as e:
                print(f"Errore durante l'esecuzione: {str(e)}")
                await asyncio.sleep(60)  # Attendi 1 minuto in caso di errore


async def main():
    bot = BitcoinTradingBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
