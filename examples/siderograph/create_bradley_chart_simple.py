import csv
import random
from datetime import datetime, timedelta


def create_bradley_points():
    """Crea i punti di inversione del Bradley Siderograph per il periodo 2025-2027"""
    bradley_points = [
        # 2025 - Punti di inversione
        {"date": "2025-01-24", "desc": "Congiunzione Venere-Saturno", "level": "ALTO"},
        {"date": "2025-03-10", "desc": "Quadratura Giove-Plutone", "level": "MEDIO"},
        {"date": "2025-04-23", "desc": "Congiunzione Marte-Saturno", "level": "ALTO"},
        {"date": "2025-06-15", "desc": "Trigono Giove-Urano", "level": "MEDIO"},
        {"date": "2025-08-07", "desc": "Opposizione Sole-Nettuno", "level": "BASSO"},
        {"date": "2025-09-21", "desc": "Congiunzione Mercurio-Marte", "level": "MEDIO"},
        {"date": "2025-11-14", "desc": "Quadratura Venere-Plutone", "level": "ALTO"},
        {"date": "2025-12-28", "desc": "Trigono Sole-Saturno", "level": "BASSO"},
        # 2026 - Punti di inversione
        {"date": "2026-02-03", "desc": "Congiunzione Giove-Nettuno", "level": "ALTO"},
        {"date": "2026-03-19", "desc": "Quadratura Marte-Urano", "level": "MEDIO"},
        {"date": "2026-05-05", "desc": "Opposizione Venere-Saturno", "level": "ALTO"},
        {"date": "2026-06-22", "desc": "Trigono Mercurio-Giove", "level": "BASSO"},
        {"date": "2026-08-09", "desc": "Congiunzione Sole-Marte", "level": "MEDIO"},
        {"date": "2026-09-27", "desc": "Quadratura Giove-Saturno", "level": "ALTO"},
        {"date": "2026-11-15", "desc": "Trigono Venere-Urano", "level": "MEDIO"},
        {
            "date": "2026-12-30",
            "desc": "Congiunzione Mercurio-Plutone",
            "level": "BASSO",
        },
        # 2027 - Punti di inversione
        {"date": "2027-01-18", "desc": "Opposizione Giove-Marte", "level": "ALTO"},
        {"date": "2027-03-04", "desc": "Quadratura Venere-Nettuno", "level": "MEDIO"},
        {"date": "2027-04-21", "desc": "Congiunzione Sole-Saturno", "level": "ALTO"},
        {"date": "2027-06-08", "desc": "Trigono Marte-Plutone", "level": "MEDIO"},
        {"date": "2027-07-25", "desc": "Opposizione Mercurio-Urano", "level": "BASSO"},
        {"date": "2027-09-11", "desc": "Congiunzione Venere-Giove", "level": "ALTO"},
        {"date": "2027-10-28", "desc": "Quadratura Sole-Plutone", "level": "MEDIO"},
        {"date": "2027-12-15", "desc": "Trigono Mercurio-Saturno", "level": "BASSO"},
    ]

    return bradley_points


def simulate_sp500_data():
    """Simula i dati dell'S&P500 per il periodo 2025-2027 su base settimanale"""
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2027, 12, 31)

    # Valore iniziale dell'S&P500 (valore ipotetico per inizio 2025)
    price = 5800

    # Parametri per la simulazione
    avg_weekly_growth = (
        0.08 / 52
    )  # 8% crescita annuale media, convertita in settimanale
    volatility = 0.15 / (52**0.5)  # 15% volatilità annuale, convertita in settimanale

    # Genera date settimanali e prezzi
    sp500_data = []
    current_date = start_date

    while current_date <= end_date:
        # Aggiungi un po' di casualità alla crescita settimanale
        random_return = random.normalvariate(avg_weekly_growth, volatility)
        price = price * (1 + random_return)

        # Calcola open, high, low, close con un po' di casualità aggiuntiva
        open_price = price * (1 + random.uniform(-0.01, 0.01))
        high_price = price * (1 + random.uniform(0, 0.02))
        low_price = price * (1 + random.uniform(-0.02, 0))
        close_price = price
        volume = random.randint(1000000, 5000000)

        # Aggiungi alla lista
        sp500_data.append(
            {
                "Date": current_date.strftime("%Y-%m-%d"),
                "Open": round(open_price, 2),
                "High": round(high_price, 2),
                "Low": round(low_price, 2),
                "Close": round(close_price, 2),
                "Volume": volume,
            }
        )

        # Avanza di una settimana
        current_date += timedelta(days=7)

    return sp500_data


def save_to_csv():
    """Salva i dati generati in file CSV"""
    # Crea i dati
    bradley_points = create_bradley_points()
    sp500_data = simulate_sp500_data()

    # Salva i punti di inversione Bradley in CSV
    with open("examples/siderograph/bradley_points.csv", "w", newline="") as csvfile:
        fieldnames = ["date", "desc", "level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for point in bradley_points:
            writer.writerow(point)

    # Salva i dati dell'S&P500 in CSV
    with open("examples/siderograph/sp500_simulation.csv", "w", newline="") as csvfile:
        fieldnames = ["Date", "Open", "High", "Low", "Close", "Volume"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for day_data in sp500_data:
            writer.writerow(day_data)

    print("Dati generati con successo!")
    print(
        "Punti di inversione Bradley salvati in: examples/siderograph/bradley_points.csv"
    )
    print("Dati S&P500 simulati salvati in: examples/siderograph/sp500_simulation.csv")
    print("\nInformazioni per la creazione del grafico:")
    print("- Usare un grafico a candele per i dati S&P500")
    print("- Aggiungere linee verticali colorate in base al livello di importanza")
    print("  - ALTO: linee rosse")
    print("  - MEDIO: linee arancioni")
    print("  - BASSO: linee verdi")
    print("- Includere etichette per i punti di inversione importanti (ALTO)")
    print("- Aggiungere un disclaimer che le date sono approssimative e il grafico")
    print("  indica solo potenziali punti di inversione, non la direzione del mercato")


if __name__ == "__main__":
    try:
        save_to_csv()
    except Exception as e:
        print(f"Errore durante la generazione dei dati: {e}")
