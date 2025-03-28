#!/usr/bin/env python3

import random
from datetime import datetime, timedelta

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

# Impostazioni per il grafico di alta qualità
plt.rcParams["figure.figsize"] = (16, 12)
plt.rcParams["figure.dpi"] = 300
plt.rcParams["font.family"] = "Helvetica"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
plt.style.use("fivethirtyeight")


# Funzione per convertire data in formato stringa a datetime
def convert_date_range(date_range_str):
    # Esempio: "15-20 Gennaio 2025"
    parts = date_range_str.split(" ")
    day_range = parts[0].split("-")
    mid_day = (int(day_range[0]) + int(day_range[1])) // 2
    month_str = parts[1]
    year = parts[2]

    month_map = {
        "Gennaio": 1,
        "Febbraio": 2,
        "Marzo": 3,
        "Aprile": 4,
        "Maggio": 5,
        "Giugno": 6,
        "Luglio": 7,
        "Agosto": 8,
        "Settembre": 9,
        "Ottobre": 10,
        "Novembre": 11,
        "Dicembre": 12,
    }

    month_num = month_map[month_str]
    return datetime(int(year), month_num, mid_day)


# Classe per rappresentare un punto di inversione
class InversionPoint:
    def __init__(self, date_range, level, description, is_major=False):
        self.date = convert_date_range(date_range)
        self.level = level  # "ALTO", "MEDIO", "BASSO"
        self.description = description
        self.is_major = is_major

        # Impostare colore e spessore in base al livello
        if level == "ALTO":
            self.color = "red"
            self.linewidth = 1.5
        elif level == "MEDIO":
            self.color = "orange"
            self.linewidth = 1.2
        else:  # "BASSO"
            self.color = "green"
            self.linewidth = 1.0

        # Se è un evento maggiore, aumenta lo spessore
        if is_major:
            self.linewidth *= 2

    def __str__(self):
        return f"{self.date.strftime('%d-%m-%Y')} [{self.level}]: {self.description}"


# Definizione dei punti di inversione Bradley Siderograph
def create_bradley_points():
    points = []

    # 2025
    points.append(
        InversionPoint(
            "15-20 Gennaio 2025",
            "ALTO",
            "Congiunzione Mercurio-Plutone + Quadratura Marte-Saturno",
        )
    )
    points.append(
        InversionPoint(
            "10-15 Febbraio 2025",
            "MEDIO",
            "Trigono Giove-Saturno (aspetto positivo, possibile ripresa)",
        )
    )
    points.append(
        InversionPoint(
            "20-25 Marzo 2025",
            "ALTO",
            "Quadratura Giove-Plutone (influenza forte sui mercati finanziari)",
        )
    )
    points.append(
        InversionPoint(
            "5-10 Aprile 2025",
            "MEDIO",
            "Congiunzione Venere-Urano (volatilità improvvisa)",
        )
    )
    points.append(
        InversionPoint(
            "15-20 Maggio 2025",
            "ALTO",
            "Opposizione Marte-Saturno + Quadratura Giove-Urano",
        )
    )
    points.append(
        InversionPoint(
            "10-15 Giugno 2025",
            "BASSO",
            "Trigono multiplo tra pianeti veloci (periodo favorevole)",
        )
    )
    points.append(
        InversionPoint(
            "20-25 Luglio 2025", "ALTO", "Quadratura Saturno-Urano (tensione economica)"
        )
    )
    points.append(
        InversionPoint(
            "15-20 Agosto 2025",
            "MEDIO",
            "Opposizione Sole-Nettuno + aspetti multipli di Mercurio",
        )
    )
    points.append(
        InversionPoint(
            "10-15 Settembre 2025",
            "ALTO",
            "Congiunzione Marte-Plutone (potenziale forte inversione)",
        )
    )
    points.append(
        InversionPoint(
            "5-10 Ottobre 2025",
            "BASSO",
            "Trigono Giove-Plutone (opportunità di crescita)",
        )
    )
    points.append(
        InversionPoint(
            "18-25 Novembre 2025",
            "ALTO",
            "Quadratura multipla tra pianeti lenti e veloci",
        )
    )
    points.append(
        InversionPoint(
            "15-20 Dicembre 2025",
            "MEDIO",
            "Congiunzione Mercurio-Saturno (rallentamento)",
        )
    )

    # 2026
    points.append(
        InversionPoint(
            "10-15 Gennaio 2026",
            "ALTO",
            "Quadratura Giove-Nettuno (illusione nei mercati)",
        )
    )
    points.append(
        InversionPoint(
            "5-10 Febbraio 2026", "MEDIO", "Congiunzione Venere-Marte (energia mista)"
        )
    )
    points.append(
        InversionPoint(
            "20-25 Marzo 2026",
            "ALTO",
            "Opposizione Giove-Saturno (punto di inversione MAGGIORE)",
            True,
        )
    )
    points.append(
        InversionPoint(
            "10-15 Aprile 2026", "BASSO", "Trigono multiplo tra pianeti veloci"
        )
    )
    points.append(
        InversionPoint(
            "1-5 Maggio 2026",
            "ALTO",
            "Quadratura Marte-Plutone (tensione intensificata)",
        )
    )
    points.append(
        InversionPoint(
            "15-20 Giugno 2026",
            "MEDIO",
            "Congiunzione Giove-Urano (innovazione/volatilità)",
        )
    )
    points.append(
        InversionPoint(
            "5-10 Luglio 2026",
            "ALTO",
            "Quadratura multipla tra Sole, Marte e pianeti esterni",
        )
    )
    points.append(
        InversionPoint(
            "15-20 Agosto 2026",
            "BASSO",
            "Trigono Venere-Giove-Saturno (periodo favorevole)",
        )
    )
    points.append(
        InversionPoint(
            "20-25 Settembre 2026",
            "ALTO",
            "Opposizione Marte-Urano + aspetti di Mercurio",
        )
    )
    points.append(
        InversionPoint(
            "5-10 Ottobre 2026",
            "MEDIO",
            "Congiunzione Venere-Saturno (cautela nei mercati)",
        )
    )
    points.append(
        InversionPoint(
            "15-20 Novembre 2026",
            "ALTO",
            "Quadratura Giove-Plutone (forte tensione, possibile crisi)",
        )
    )
    points.append(
        InversionPoint(
            "10-15 Dicembre 2026",
            "BASSO",
            "Trigono multiplo (stabilizzazione temporanea)",
        )
    )

    # 2027
    points.append(
        InversionPoint(
            "5-10 Gennaio 2027",
            "MEDIO",
            "Congiunzione Mercurio-Marte (volatilità a breve termine)",
        )
    )
    points.append(
        InversionPoint(
            "20-25 Febbraio 2027",
            "ALTO",
            "Quadratura Giove-Saturno (tensione economica)",
        )
    )
    points.append(
        InversionPoint(
            "15-20 Marzo 2027",
            "ALTO",
            "CONGIUNZIONE SATURNO-NETTUNO (EVENTO RARO/MAGGIORE)",
            True,
        )
    )
    points.append(
        InversionPoint(
            "10-15 Aprile 2027", "MEDIO", "Multipli aspetti di pianeti veloci"
        )
    )
    points.append(
        InversionPoint(
            "1-5 Maggio 2027", "BASSO", "Trigono Giove-Plutone (opportunità nascoste)"
        )
    )
    points.append(
        InversionPoint(
            "15-20 Giugno 2027",
            "ALTO",
            "OPPOSIZIONE GIOVE-URANO (punto di inversione forte)",
            True,
        )
    )
    points.append(
        InversionPoint(
            "5-10 Luglio 2027",
            "MEDIO",
            "Congiunzione Venere-Marte (energia contrastante)",
        )
    )
    points.append(
        InversionPoint(
            "20-25 Agosto 2027", "BASSO", "Trigono Sole-Saturno (stabilità temporanea)"
        )
    )
    points.append(
        InversionPoint(
            "10-15 Settembre 2027",
            "ALTO",
            "Quadratura multipla tra pianeti veloci e lenti",
        )
    )
    points.append(
        InversionPoint(
            "5-10 Ottobre 2027",
            "ALTO",
            "MULTIPLI ASPETTI SIMULTANEI (punto di svolta MAGGIORE)",
            True,
        )
    )
    points.append(
        InversionPoint(
            "15-20 Novembre 2027",
            "MEDIO",
            "Opposizione Marte-Saturno (tensione prolungata)",
        )
    )
    points.append(
        InversionPoint(
            "10-15 Dicembre 2027",
            "BASSO",
            "Trigono Giove-Saturno (miglioramento delle condizioni)",
        )
    )

    return points


# Fornisci dati simulati per il NASDAQ per il periodo 2025-2027
def get_nvidia_data():
    try:
        print("Utilizzo dati simulati per una migliore visualizzazione...")

        # Creiamo un DataFrame con dati simulati dal 2020 ad oggi
        dates = pd.date_range(start="2020-01-01", end=datetime.now(), freq="W")
        np.random.seed(42)

        # Simuliamo i dati storici
        prices = []
        volumes = []
        current_price = 200  # Prezzo iniziale nel 2020

        for _ in range(len(dates)):
            # Aggiungiamo crescita e volatilità
            random_return = np.random.normal(
                0.02, 0.05
            )  # 2% crescita media settimanale, 5% volatilità
            current_price *= 1 + random_return
            prices.append(current_price)
            volumes.append(np.random.normal(50000000, 10000000))  # Volume medio tipico

        # Creiamo DataFrame con i dati storici
        historical_df = pd.DataFrame(
            {
                "Open": prices,
                "High": [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
                "Low": [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
                "Close": prices,
                "Volume": volumes,
            },
            index=dates,
        )

        # Creiamo date future per la proiezione
        projection_start = datetime.now()
        projection_end = datetime(2027, 12, 31)
        weeks_in_projection = int((projection_end - projection_start).days / 7) + 1
        projection_dates = [
            projection_start + timedelta(weeks=i) for i in range(weeks_in_projection)
        ]

        # Inizializziamo valori proiettati
        current_price = float(historical_df["Close"].iloc[-1])
        print(f"\nPrezzo attuale simulato: ${current_price:,.2f}")

        projection_close = []
        projection_open = []
        projection_high = []
        projection_low = []
        projection_volume = []

        # Parametri per la proiezione
        annual_growth = 0.15  # 15% crescita annuale
        weekly_growth = (1 + annual_growth) ** (1 / 52) - 1
        weekly_volatility = 0.05  # 5% volatilità settimanale

        for i in range(weeks_in_projection):
            # Aggiungiamo crescita e volatilità
            random_return = np.random.normal(weekly_growth, weekly_volatility)

            # Cicli simulati di mercato
            cycle1 = 0.02 * np.sin(2 * np.pi * i / 52)  # ~1 anno
            cycle2 = 0.04 * np.sin(2 * np.pi * i / (52 * 4))  # ~4 anni
            cycle3 = 0.06 * np.sin(2 * np.pi * i / (52 * 8))  # ~8 anni

            # Combiniamo crescita, volatilità e cicli
            price_change = random_return + cycle1 + cycle2 + cycle3
            new_price = current_price * (1 + price_change)

            # Aggiungiamo variazione per OHLC
            daily_volatility = weekly_volatility / np.sqrt(5)
            open_price = new_price * (1 + np.random.normal(0, daily_volatility / 2))
            high_price = max(new_price, open_price) * (
                1 + abs(np.random.normal(0, daily_volatility))
            )
            low_price = min(new_price, open_price) * (
                1 - abs(np.random.normal(0, daily_volatility))
            )

            # Volume con trend e casualità
            base_volume = 50000000  # Volume medio tipico
            volume = base_volume * (1 + 0.8 * np.random.normal())

            # Aggiungiamo i valori alle liste
            projection_close.append(new_price)
            projection_open.append(open_price)
            projection_high.append(high_price)
            projection_low.append(low_price)
            projection_volume.append(max(0, volume))

            current_price = new_price

        # Creiamo DataFrame della proiezione
        projection_df = pd.DataFrame(
            {
                "Open": projection_open,
                "High": projection_high,
                "Low": projection_low,
                "Close": projection_close,
                "Volume": projection_volume,
            },
            index=projection_dates,
        )

        # Combiniamo dati storici e proiezione
        combined_df = pd.concat([historical_df, projection_df])

        # Calcoliamo MA sul dataset completo
        combined_df["MA20"] = combined_df["Close"].rolling(window=20).mean()
        combined_df["MA50"] = combined_df["Close"].rolling(window=50).mean()

        return combined_df

    except Exception as e:
        print(f"Errore nella generazione dei dati simulati: {e}")
        return None


# Formatta numeri grandi con suffissi K, M, B
def format_large_number(x, pos):
    if x >= 1e9:
        return f"{x/1e9:.1f}B"
    elif x >= 1e6:
        return f"{x/1e6:.1f}M"
    elif x >= 1e3:
        return f"{x/1e3:.1f}K"
    else:
        return f"{x:.0f}"


# Funzione principale per creare il grafico
def create_bradley_chart():
    # Otteniamo dati e punti di inversione
    nvidia_data = get_nvidia_data()
    bradley_points = create_bradley_points()

    # Creiamo figura e layout con più spazio tra i subplot
    fig = plt.figure(figsize=(16, 12), dpi=300)
    gs = GridSpec(4, 1, height_ratios=[3, 1, 0.8, 0.8], figure=fig)
    gs.update(hspace=0.4)  # Aumentiamo lo spazio tra i subplot

    # Grafico principale
    ax1 = fig.add_subplot(gs[0])
    ax1.set_title(
        "BRADLEY SIDEROGRAPH 2025-2027 & NASDAQ", fontsize=18, weight="bold", pad=20
    )
    ax1.set_xlabel("")
    ax1.set_ylabel("NASDAQ", fontsize=14)

    # Plot dei dati candlestick simulati
    for i in range(len(nvidia_data)):
        date = nvidia_data.index[i]
        open_price = float(nvidia_data["Open"].iloc[i])
        close_price = float(nvidia_data["Close"].iloc[i])
        high_price = float(nvidia_data["High"].iloc[i])
        low_price = float(nvidia_data["Low"].iloc[i])

        # Colore del candlestick
        if close_price >= open_price:
            color = "green"
            body_bottom = open_price
            body_height = close_price - open_price
        else:
            color = "red"
            body_bottom = close_price
            body_height = open_price - close_price

        # Plot del corpo principale
        rect = Rectangle(
            (mdates.date2num(date) - 0.3, body_bottom),  # Centrato sulla data
            0.6,
            body_height,
            edgecolor=color,
            facecolor=color,
            alpha=0.8,
        )
        ax1.add_patch(rect)

        # Plot della shadow
        ax1.plot(
            [mdates.date2num(date), mdates.date2num(date)],
            [low_price, high_price],
            color="black",
            linewidth=1.0,
        )

    # Plot delle medie mobili
    ax1.plot(
        nvidia_data.index,
        nvidia_data["MA20"],
        color="blue",
        linewidth=1.5,
        label="MA20",
    )
    ax1.plot(
        nvidia_data.index,
        nvidia_data["MA50"],
        color="red",
        linewidth=1.5,
        label="MA50",
    )

    # Formatta l'asse Y con i prezzi
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))

    # Formatta l'asse X
    ax1.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")

    # Plot dei punti di inversione
    for point in bradley_points:
        color = point.color
        linewidth = point.linewidth

        # Ottieni limiti degli assi per linee verticali
        ymin, ymax = ax1.get_ylim()
        height = ymax - ymin

        # Plot della linea verticale
        ax1.axvline(
            x=point.date, color=color, linewidth=linewidth, alpha=0.7, linestyle="--"
        )

        # Etichetta semplificata
        if point.is_major:
            # Per eventi maggiori, aggiungiamo un'etichetta più prominente
            label_y = ymin + height * 0.97
            label_text = point.description.split("(")[0].strip()
            ax1.annotate(
                label_text,
                xy=(point.date, label_y),
                xytext=(0, 10),
                textcoords="offset points",
                fontsize=8,
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, alpha=0.8),
            )

    # Grafico del volume
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.bar(nvidia_data.index, nvidia_data["Volume"], color="darkblue", alpha=0.5)
    ax2.set_ylabel("Volume", fontsize=12)
    ax2.yaxis.set_major_formatter(FuncFormatter(format_large_number))

    # Pannello per eventi MAGGIORI
    ax3 = fig.add_subplot(gs[2])
    ax3.set_title("EVENTI MAGGIORI", fontsize=14, pad=20)
    ax3.axis("off")

    # Lista degli eventi maggiori
    major_events = [p for p in bradley_points if p.is_major]

    # Disegna una timeline degli eventi maggiori
    ax3.axhline(y=0.5, color="gray", linewidth=1.5, alpha=0.5)

    # Calcola le posizioni x per gli eventi maggiori
    x_positions = np.linspace(0.1, 0.9, len(major_events))

    for i, event in enumerate(major_events):
        # Colore in base al livello
        marker_color = event.color

        # Plot del punto
        ax3.plot(x_positions[i], 0.5, marker="o", markersize=10, color=marker_color)

        # Etichetta con data e descrizione
        date_str = event.date.strftime("%d %b %Y")
        description = event.description.split("(")[
            0
        ].strip()  # Prendiamo solo la prima parte

        # Alterna posizione sopra/sotto e aumenta la distanza
        y_offset = 0.4 if i % 2 == 0 else -0.4
        ax3.annotate(
            f"{date_str}\n{description}",
            xy=(x_positions[i], 0.5),
            xytext=(0, y_offset * 100),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),
            arrowprops=dict(
                arrowstyle="->", connectionstyle="arc3,rad=0", color="gray"
            ),
        )

    # Legenda
    ax4 = fig.add_subplot(gs[3])
    ax4.axis("off")

    legend_elements = [
        Line2D(
            [0],
            [0],
            color="red",
            linewidth=2,
            linestyle="--",
            label="ALTO: Aspetti forti tra pianeti lenti",
        ),
        Line2D(
            [0],
            [0],
            color="orange",
            linewidth=2,
            linestyle="--",
            label="MEDIO: Mix di aspetti",
        ),
        Line2D(
            [0],
            [0],
            color="green",
            linewidth=2,
            linestyle="--",
            label="BASSO: Principalmente aspetti favorevoli",
        ),
        Line2D([0], [0], color="blue", linewidth=2, label="Media Mobile 20 settimane"),
        Line2D([0], [0], color="red", linewidth=2, label="Media Mobile 50 settimane"),
    ]

    ax4.legend(
        handles=legend_elements,
        loc="center",
        ncol=3,
        fontsize=10,
        frameon=True,
        facecolor="white",
        edgecolor="gray",
    )

    plt.figtext(
        0.5,
        0.02,
        "Le date sono approssimative (±5 giorni). Questo grafico mostra SOLO potenziali PUNTI DI INVERSIONE, non la DIREZIONE del mercato.",
        ha="center",
        fontsize=10,
        style="italic",
        bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="orange", alpha=0.8),
    )

    # Salva immagine e PDF
    plt.savefig(
        "examples/siderograph/bradley_siderograph_nasdaq.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.savefig(
        "examples/siderograph/bradley_siderograph_nasdaq.pdf", bbox_inches="tight"
    )

    print("Grafico generato e salvato con successo!")
    print("- examples/siderograph/bradley_siderograph_nasdaq.png")
    print("- examples/siderograph/bradley_siderograph_nasdaq.pdf")


# Esegui la funzione principale
if __name__ == "__main__":
    create_bradley_chart()
