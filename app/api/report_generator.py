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

        # Ridimensiona le immagini nella cartella del report se esistono
        for file in os.listdir(cartella_report):
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                image_path = os.path.join(cartella_report, file)
                try:
                    resize_image(
                        image_path, max_size_mb=4
                    )  # Ridimensiona a max 4MB per essere sicuri
                except Exception as e:
                    logger.warning(
                        f"Errore nel ridimensionamento dell'immagine {file}: {e}"
                    )

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

        report_status[report_id].file_generati.append("istruzioni.txt")
        report_status[report_id].percentuale_completamento = 20

        # CSS da incorporare direttamente nei file HTML
        css_styles = """
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }

        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            font-size: 2.2em;
            margin-top: 20px;
        }

        h2 {
            color: #2c3e50;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
            font-size: 1.8em;
        }

        h3 {
            color: #34495e;
            margin-top: 25px;
            font-size: 1.4em;
        }

        p {
            margin: 15px 0;
            text-align: justify;
            font-size: 16px;
        }

        ul, ol {
            margin: 20px 0;
            padding-left: 25px;
        }

        li {
            margin-bottom: 10px;
        }

        a {
            color: #3498db;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 3px rgba(0,0,0,0.1);
        }

        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 12px;
            text-align: left;
        }

        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }

        tr:nth-child(even) {
            background-color: #f2f2f2;
        }

        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            background-color: white;
        }

        .highlight {
            background-color: #f8f9f9;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }

        .pro-con {
            display: flex;
            margin: 20px 0;
            gap: 20px;
        }

        .pros, .cons {
            flex: 1;
            padding: 15px;
            border-radius: 8px;
        }

        .pros {
            background-color: #e9f7ef;
            border: 1px solid #27ae60;
        }

        .cons {
            background-color: #fdedec;
            border: 1px solid #e74c3c;
        }

        .nav-menu {
            background-color: #2c3e50;
            padding: 15px;
            border-radius: 5px;
            position: sticky;
            top: 0;
            margin-bottom: 20px;
            z-index: 100;
        }

        .nav-menu a {
            color: white;
            margin-right: 15px;
            padding: 5px 10px;
            text-decoration: none;
        }

        .nav-menu a:hover {
            background-color: #34495e;
            border-radius: 3px;
        }

        .section {
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .feature-list {
            list-style-type: none;
            padding: 0;
        }

        .feature-list li {
            padding: 10px 15px;
            margin-bottom: 5px;
            background-color: #f8f9f9;
            border-left: 3px solid #3498db;
        }

        blockquote {
            font-style: italic;
            border-left: 4px solid #ccc;
            margin-left: 0;
            padding-left: 15px;
            color: #555;
        }

        .pricing-table {
            width: 100%;
            border-collapse: collapse;
        }

        .pricing-table th, .pricing-table td {
            text-align: center;
        }

        .pricing-table .feature {
            text-align: left;
        }

        .price {
            font-weight: bold;
            color: #16a085;
        }

        .screenshot {
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            display: block;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #eee;
            height: 400px;
            line-height: 400px;
            text-align: center;
            color: #777;
        }

        .footnote {
            font-size: 0.9em;
            color: #777;
            border-top: 1px solid #eee;
            margin-top: 30px;
            padding-top: 10px;
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .pro-con {
                flex-direction: column;
            }

            .nav-menu {
                position: static;
            }
        }
        """

        # Sovrascrive la classe StrReplaceEditor per migliorare l'HTML
        from app.tool.str_replace_editor import StrReplaceEditor

        original_execute = StrReplaceEditor.execute

        async def fixed_execute(
            self,
            *,
            command: str,
            path: str,
            file_text: str | None = None,
            view_range: list[int] | None = None,
            old_str: str | None = None,
            new_str: str | None = None,
            insert_line: int | None = None,
            **kwargs: Any,
        ) -> str:
            # Se stiamo creando un file che termina con .html, miglioriamo l'HTML
            if command == "create" and path.endswith(".html"):
                import html
                import re

                # Decodifica le entità HTML
                if file_text:
                    content = html.unescape(file_text)

                    # Rimuovi eventuali tag HTML esistenti
                    content = re.sub(r"<[^>]*>", "", content)

                    # Crea un titolo dal nome del file
                    title = (
                        os.path.basename(path)
                        .replace(".html", "")
                        .replace("_", " ")
                        .title()
                    )

                    # Costruisci la navigazione
                    nav_items = []
                    files = [
                        f for f in os.listdir(cartella_report) if f.endswith(".html")
                    ]
                    for file in files:
                        name = file.replace(".html", "").replace("_", " ").title()
                        nav_items.append(f'<a href="{file}">{name}</a>')

                    nav_menu = (
                        '<div class="nav-menu">\n    '
                        + "\n    ".join(nav_items)
                        + "\n</div>"
                    )

                    # Crea un HTML ben formattato con CSS incorporato
                    template = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Report {argomento}</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    {nav_menu}
    <div class="section">
        {content}
    </div>
    <div class="footnote">
        Report generato il {datetime.datetime.now().strftime('%d/%m/%Y')} - OpenManus Report Generator
    </div>
</body>
</html>"""
                    file_text = template

            # Utilizziamo il metodo originale con i parametri aggiornati
            return await original_execute(
                self,
                command=command,
                path=path,
                file_text=file_text,
                view_range=view_range,
                old_str=old_str,
                new_str=new_str,
                insert_line=insert_line,
                **kwargs,
            )

        # Applica la patch alla classe
        StrReplaceEditor.execute = fixed_execute

        # Crea l'istanza di Manus
        agent = Manus()

        # Componi un prompt più dettagliato per contenuti migliori
        prompt = f"""
        Sei un esperto di reportistica professionale. Genera un report completo e approfondito su '{argomento}'.

        ISTRUZIONI DETTAGLIATE:
        {istruzioni}

        FORMATO DEL REPORT:
        - Crea diversi file HTML per organizzare il contenuto in modo logico (almeno index.html più altri file tematici)
        - Usa una struttura ben organizzata con titoli, sottotitoli e sezioni
        - I file saranno migliorati automaticamente con stili CSS professionali

        QUALITÀ DEL CONTENUTO:
        - Conduci una ricerca MOLTO APPROFONDITA sull'argomento
        - Offri informazioni dettagliate, specifiche e pratiche
        - Includi dati, statistiche e specifiche tecniche precise
        - Crea tabelle comparative dettagliate con colonne per caratteristiche, prezzi, pro/contro
        - Descrivi funzionalità specifiche con esempi concreti

        ELEMENTI DA INCLUDERE:
        - Tabelle comparative ben strutturate
        - Liste di funzionalità e caratteristiche
        - Analisi dei prezzi e modelli di business
        - Vantaggi e svantaggi di ciascuna soluzione
        - Raccomandazioni specifiche per diversi casi d'uso

        IMPORTANTE:
        - Salva tutti i file nella cartella corrente
        - Assicurati che ogni file HTML abbia un titolo principale e una struttura logica
        - I file saranno resi graficamente più attraenti automaticamente
        - Concentrati sulla qualità, profondità e struttura del CONTENUTO
        """

        # Imposta la directory di lavoro corrente alla cartella del report
        original_dir = os.getcwd()
        os.chdir(cartella_report)

        # Esegui l'agente Manus
        report_status[report_id].percentuale_completamento = 30
        await agent.run(prompt)

        # Torna alla directory originale
        os.chdir(original_dir)

        # Ripristina il metodo originale
        StrReplaceEditor.execute = original_execute

        # Aggiorna la lista dei file generati
        files = os.listdir(cartella_report)
        report_status[report_id].file_generati = files

        # Aggiorna lo stato
        report_status[report_id].stato = "completato"
        report_status[report_id].percentuale_completamento = 100

        logger.info(f"Report {report_id} generato con successo")

    except Exception as e:
        logger.error(f"Errore durante la generazione del report {report_id}: {e}")

        # Aggiorna lo stato con l'errore
        report_status[report_id].stato = "errore"
        report_status[report_id].errori = [str(e)]

        # Se la cartella è vuota o contiene solo istruzioni.txt, eliminiamo la cartella
        try:
            files = os.listdir(cartella_report)
            if not files or (len(files) == 1 and "istruzioni.txt" in files):
                shutil.rmtree(cartella_report)
                logger.info(
                    f"Cartella {cartella_report} eliminata perché vuota dopo un errore"
                )
        except Exception as cleanup_error:
            logger.error(f"Errore durante la pulizia: {cleanup_error}")
