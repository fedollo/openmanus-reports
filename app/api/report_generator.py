import asyncio
import datetime
import io
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from app.agent.manus import Manus
from app.config import config
from app.logger import logger
from app.utils.image_utils import resize_image
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel


class ReportRequest(BaseModel):
    """Schema per la richiesta di generazione di report."""

    argomento: str
    istruzioni: str
    parametri_addizionali: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    """Schema per la risposta alla richiesta di generazione di report."""

    report_id: str
    cartella: str
    stato: str
    file_generati: Optional[List[str]] = None


class ReportStatus(BaseModel):
    """Schema per lo stato di avanzamento del report."""

    report_id: str
    stato: str
    percentuale_completamento: float = 0
    file_generati: List[str] = []
    errori: Optional[List[str]] = None


# Dizionario per tenere traccia dello stato di avanzamento dei report
report_status: Dict[str, ReportStatus] = {}


app = FastAPI(
    title="OpenManus Report Generator",
    description="API per generare report automatici utilizzando OpenManus",
    version="1.0.0",
)

# Monta la cartella workspace per servire i file statici
app.mount("/workspace", StaticFiles(directory="workspace"), name="workspace")


@app.get("/")
async def root():
    """Endpoint principale che fornisce informazioni sull'API."""
    return {
        "servizio": "OpenManus Report Generator",
        "versione": "1.0.0",
        "descrizione": "API per generare report automatici utilizzando OpenManus",
        "endpoints": [
            {"path": "/", "method": "GET", "descrizione": "Informazioni sull'API"},
            {
                "path": "/genera-report",
                "method": "POST",
                "descrizione": "Genera un nuovo report",
            },
            {
                "path": "/stato-report/{report_id}",
                "method": "GET",
                "descrizione": "Controlla lo stato di un report",
            },
            {
                "path": "/lista-report",
                "method": "GET",
                "descrizione": "Elenca tutti i report disponibili",
            },
        ],
    }


@app.post("/genera-report", response_model=ReportResponse)
async def genera_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    Genera un nuovo report basato sull'argomento e le istruzioni fornite.

    Args:
        request: La richiesta contenente argomento e istruzioni
        background_tasks: Per eseguire la generazione in background

    Returns:
        Informazioni sul report generato
    """
    # Validazione dell'input
    if not request.argomento or not request.istruzioni:
        raise HTTPException(
            status_code=400, detail="Argomento e istruzioni sono obbligatori"
        )

    # Rimuovi caratteri non validi per il nome cartella
    argomento_sicuro = "".join(
        c if c.isalnum() or c in [" ", "_", "-"] else "_" for c in request.argomento
    )
    report_id = f"{argomento_sicuro.replace(' ', '_').lower()}_{hash(request.istruzioni) % 10000}"

    # Crea la cartella per il report
    cartella_report = os.path.join(
        config.workspace_root, argomento_sicuro.replace(" ", "_").lower()
    )

    # Verifica se la cartella esiste già
    if os.path.exists(cartella_report):
        # Aggiungi un suffisso numerico per evitare sovrascritture
        i = 1
        while os.path.exists(f"{cartella_report}_{i}"):
            i += 1
        cartella_report = f"{cartella_report}_{i}"
        report_id = f"{report_id}_{i}"

    os.makedirs(cartella_report, exist_ok=True)

    # Inizializza lo stato del report
    report_status[report_id] = ReportStatus(
        report_id=report_id,
        stato="in_coda",
        percentuale_completamento=0,
        file_generati=[],
    )

    # Avvia la generazione in background
    background_tasks.add_task(
        genera_report_in_background,
        report_id=report_id,
        cartella_report=cartella_report,
        argomento=request.argomento,
        istruzioni=request.istruzioni,
        parametri_addizionali=request.parametri_addizionali,
    )

    return ReportResponse(
        report_id=report_id, cartella=cartella_report, stato="in_coda"
    )


@app.get("/stato-report/{report_id}", response_model=ReportStatus)
async def stato_report(report_id: str):
    """
    Controlla lo stato di avanzamento di un report.

    Args:
        report_id: L'ID del report da controllare

    Returns:
        Lo stato attuale del report
    """
    if report_id not in report_status:
        raise HTTPException(
            status_code=404, detail=f"Report con ID {report_id} non trovato"
        )

    return report_status[report_id]


@app.get("/lista-report", response_model=List[ReportStatus])
async def lista_report():
    """
    Elenca tutti i report disponibili.

    Returns:
        Lista di tutti i report con il loro stato
    """
    return list(report_status.values())


@app.delete("/elimina-report/{report_id}")
async def elimina_report(report_id: str):
    """
    Elimina un report esistente.

    Args:
        report_id: L'ID del report da eliminare

    Returns:
        Conferma dell'eliminazione
    """
    if report_id not in report_status:
        raise HTTPException(
            status_code=404, detail=f"Report con ID {report_id} non trovato"
        )

    stato = report_status[report_id]

    # Controlla se il report è ancora in generazione
    if stato.stato == "in_elaborazione":
        raise HTTPException(
            status_code=400,
            detail="Non è possibile eliminare un report in elaborazione",
        )

    # Trova e elimina la cartella del report se esiste
    cartella = None
    for key, value in report_status.items():
        if key == report_id:
            cartella = Path(value.cartella)
            break

    if cartella and cartella.exists():
        try:
            shutil.rmtree(cartella)
        except Exception as e:
            logger.error(f"Errore durante l'eliminazione della cartella: {e}")
            raise HTTPException(
                status_code=500, detail=f"Errore durante l'eliminazione: {str(e)}"
            )

    # Rimuovi il report dallo stato
    del report_status[report_id]

    return {
        "status": "success",
        "message": f"Report {report_id} eliminato con successo",
    }


def format_instructions(
    argomento: str,
    istruzioni: str,
    parametri_addizionali: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Formatta le istruzioni in modo da renderle più efficaci per Manus,
    ma senza vincolare troppo la struttura dei file da generare.
    """
    # Data corrente
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    # Template per le istruzioni formattate
    formatted_instructions = f"""
{argomento.upper()} - REPORT GENERATOR INSTRUCTIONS

Location: {config.workspace_root}

----------------------------------------------------------
CONTENUTO RICHIESTO
----------------------------------------------------------

{istruzioni}

----------------------------------------------------------
INFORMAZIONI AGGIUNTIVE
----------------------------------------------------------

- Genera file HTML ben formattati con stile moderno e professionale
- Sei libero di creare il numero di file che ritieni necessario
- Usa tabelle, visualizzazioni e formattazione avanzata per rendere i dati comprensibili
- Assicurati che il contenuto sia strutturato in modo logico e facilmente navigabile
- I nomi dei file dovrebbero riflettere il loro contenuto

Data di generazione: {now}
"""

    # Aggiungi parametri addizionali se presenti
    if parametri_addizionali:
        formatted_instructions += "\nPARAMETRI AGGIUNTIVI:\n"
        for key, value in parametri_addizionali.items():
            formatted_instructions += f"- {key}: {value}\n"

    return formatted_instructions


async def genera_report_in_background(
    report_id: str,
    cartella_report: str,
    argomento: str,
    istruzioni: str,
    parametri_addizionali: Optional[Dict[str, Any]] = None,
):
    try:
        # Aggiorna lo stato
        report_status[report_id].stato = "in_elaborazione"
        report_status[report_id].percentuale_completamento = 10
        logger.info(f"Inizio generazione report {report_id}")

        # Crea la cartella se non esiste
        os.makedirs(cartella_report, exist_ok=True)
        logger.info(f"Cartella creata: {cartella_report}")

        # Crea il file di istruzioni.txt
        istruzioni_file = os.path.join(cartella_report, "istruzioni.txt")
        async with aiofiles.open(istruzioni_file, "w") as f:
            await f.write(
                f"# Istruzioni per la generazione di report su {argomento}\n\n"
            )
            await f.write(f"{istruzioni}\n\n")
            if parametri_addizionali:
                await f.write("## Parametri addizionali:\n")
                for key, value in parametri_addizionali.items():
                    await f.write(f"- {key}: {value}\n")

        logger.info("File istruzioni.txt creato")
        report_status[report_id].file_generati.append("istruzioni.txt")
        report_status[report_id].percentuale_completamento = 20

        # Genera index.html
        index_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{argomento}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1 {{ color: #2c3e50; }}
                .nav {{
                    background: #f8f9fa;
                    padding: 10px;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    border: 1px solid #ddd;
                }}
                th {{ background: #f4f4f4; }}
            </style>
        </head>
        <body>
            <div class="nav">
                <a href="index.html">Home</a> |
                <a href="comparison.html">Confronto</a> |
                <a href="conclusions.html">Conclusioni</a>
            </div>
            <h1>{argomento}</h1>
            <div id="content">
                <h2>Introduzione</h2>
                <p>Questo report analizza {argomento} secondo i criteri specificati.</p>
            </div>
        </body>
        </html>
        """

        index_file = os.path.join(cartella_report, "index.html")
        async with aiofiles.open(index_file, "w") as f:
            await f.write(index_content)

        logger.info("File index.html creato")
        report_status[report_id].file_generati.append("index.html")
        report_status[report_id].percentuale_completamento = 50

        # Genera comparison.html
        comparison_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confronto - {argomento}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1 {{ color: #2c3e50; }}
                .nav {{
                    background: #f8f9fa;
                    padding: 10px;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    border: 1px solid #ddd;
                }}
                th {{ background: #f4f4f4; }}
            </style>
        </head>
        <body>
            <div class="nav">
                <a href="index.html">Home</a> |
                <a href="comparison.html">Confronto</a> |
                <a href="conclusions.html">Conclusioni</a>
            </div>
            <h1>Analisi Comparativa</h1>
            <table>
                <tr>
                    <th>Criterio</th>
                    <th>Valutazione</th>
                    <th>Note</th>
                </tr>
                <tr>
                    <td>Esempio Criterio 1</td>
                    <td>Valutazione 1</td>
                    <td>Note dettagliate...</td>
                </tr>
            </table>
        </body>
        </html>
        """

        comparison_file = os.path.join(cartella_report, "comparison.html")
        async with aiofiles.open(comparison_file, "w") as f:
            await f.write(comparison_content)

        logger.info("File comparison.html creato")
        report_status[report_id].file_generati.append("comparison.html")
        report_status[report_id].percentuale_completamento = 75

        # Genera conclusions.html
        conclusions_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Conclusioni - {argomento}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1 {{ color: #2c3e50; }}
                .nav {{
                    background: #f8f9fa;
                    padding: 10px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="nav">
                <a href="index.html">Home</a> |
                <a href="comparison.html">Confronto</a> |
                <a href="conclusions.html">Conclusioni</a>
            </div>
            <h1>Conclusioni</h1>
            <div id="content">
                <h2>Riepilogo</h2>
                <p>Conclusioni dell'analisi di {argomento}...</p>
            </div>
        </body>
        </html>
        """

        conclusions_file = os.path.join(cartella_report, "conclusions.html")
        async with aiofiles.open(conclusions_file, "w") as f:
            await f.write(conclusions_content)

        logger.info("File conclusions.html creato")
        report_status[report_id].file_generati.append("conclusions.html")
        report_status[report_id].percentuale_completamento = 100
        report_status[report_id].stato = "completato"

        logger.info(f"Report {report_id} completato con successo")

    except Exception as e:
        logger.error(f"Errore durante la generazione del report {report_id}: {e}")
        report_status[report_id].stato = "errore"
        report_status[report_id].errori = [str(e)]
