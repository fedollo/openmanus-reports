#!/usr/bin/env python
"""
Script per testare l'API di generazione report.
Esempio di utilizzo:
    python tools/test_report_api.py \
        --argomento "Costi servizi di trascrizione vocale" \
        --istruzioni "Stima il costo mensile di 200 conversazioni da 5 minuti con vari servizi di trascrizione"
"""
import argparse
import json
import os
import time
from typing import Any, Dict, Optional

import requests


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Testa l'API di generazione report")
    parser.add_argument(
        "--host", type=str, default="http://localhost:8001", help="Host dell'API"
    )
    parser.add_argument(
        "--argomento", type=str, required=True, help="Argomento del report"
    )
    parser.add_argument(
        "--istruzioni", type=str, required=True, help="Istruzioni per la generazione"
    )
    parser.add_argument(
        "--parametri",
        type=str,
        default=None,
        help="Parametri addizionali in formato JSON",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=5,
        help="Intervallo in secondi per controllare lo stato del report",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in secondi per la generazione del report",
    )
    return parser.parse_args()


def genera_report(
    host: str,
    argomento: str,
    istruzioni: str,
    parametri_addizionali: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Richiede la generazione di un report.

    Args:
        host: URL base dell'API
        argomento: Argomento del report
        istruzioni: Istruzioni per la generazione
        parametri_addizionali: Parametri aggiuntivi

    Returns:
        Risposta dell'API
    """
    url = f"{host}/genera-report"
    payload = {
        "argomento": argomento,
        "istruzioni": istruzioni,
    }

    if parametri_addizionali:
        payload["parametri_addizionali"] = parametri_addizionali

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def controlla_stato(host: str, report_id: str) -> Dict[str, Any]:
    """
    Controlla lo stato di avanzamento di un report.

    Args:
        host: URL base dell'API
        report_id: ID del report

    Returns:
        Stato attuale del report
    """
    url = f"{host}/stato-report/{report_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def attendi_completamento(
    host: str, report_id: str, poll_interval: int = 5, timeout: int = 600
) -> Dict[str, Any]:
    """
    Attende il completamento di un report, controllando periodicamente lo stato.

    Args:
        host: URL base dell'API
        report_id: ID del report
        poll_interval: Intervallo in secondi tra i controlli
        timeout: Timeout in secondi

    Returns:
        Stato finale del report
    """
    start_time = time.time()
    elapsed = 0

    print(f"Attendo il completamento del report {report_id}...")

    while elapsed < timeout:
        stato = controlla_stato(host, report_id)

        if stato["stato"] == "completato":
            print(f"\nReport completato in {elapsed:.1f} secondi!")
            return stato

        if stato["stato"] == "errore":
            print(
                f"\nErrore durante la generazione del report: {stato.get('errori', 'Errore sconosciuto')}"
            )
            return stato

        # Aggiorna la barra di progresso
        percentuale = stato["percentuale_completamento"]
        barra = "=" * int(percentuale / 2)
        spazi = " " * (50 - int(percentuale / 2))
        print(
            f"\r[{barra}{spazi}] {percentuale:.1f}% completato | {elapsed:.1f}s trascorsi",
            end="",
        )

        time.sleep(poll_interval)
        elapsed = time.time() - start_time

    print(f"\nTimeout dopo {timeout} secondi")
    return controlla_stato(host, report_id)


def main():
    """Funzione principale."""
    args = parse_args()

    # Converte parametri da stringa JSON a dizionario
    parametri_addizionali = None
    if args.parametri:
        try:
            parametri_addizionali = json.loads(args.parametri)
        except json.JSONDecodeError:
            print(
                f"Errore: Impossibile decodificare i parametri JSON: {args.parametri}"
            )
            return

    print(f"Richiedo la generazione di un report su: {args.argomento}")

    try:
        # Genera il report
        risultato = genera_report(
            args.host, args.argomento, args.istruzioni, parametri_addizionali
        )

        report_id = risultato["report_id"]
        cartella = risultato["cartella"]

        print(f"Report in generazione con ID: {report_id}")
        print(f"La cartella di destinazione sarà: {cartella}")

        # Attende il completamento
        stato_finale = attendi_completamento(
            args.host, report_id, args.poll_interval, args.timeout
        )

        # Visualizza informazioni finali
        if stato_finale["stato"] == "completato":
            print("\nFile generati:")
            for file in stato_finale["file_generati"]:
                print(f"  - {file}")

            print(
                f"\nPer aprire la cartella (se in locale): file://{os.path.abspath(cartella)}"
            )

    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta HTTP: {e}")
    except KeyboardInterrupt:
        print("\nOperazione interrotta dall'utente")
    except Exception as e:
        print(f"Errore imprevisto: {e}")


if __name__ == "__main__":
    main()
