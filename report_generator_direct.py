#!/usr/bin/env python3
import asyncio
import datetime
import io
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import aiohttp
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("report_generator")

# Configurazione OpenAI API
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logger.warning(
        "OPENAI_API_KEY non impostata nell'ambiente. La generazione di report potrebbe fallire."
    )

# Configurazione dell'app FastAPI
app = FastAPI(title="OpenManus Report Generator API", version="1.0.0")

# Abilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modello per la richiesta di generazione di report
class ReportRequest(BaseModel):
    """Schema per la richiesta di generazione di report."""

    argomento: str
    istruzioni: str
    parametri_addizionali: Optional[Dict[str, Any]] = None


# Modello per lo stato di un report
class ReportStatus:
    """Classe per tenere traccia dello stato di generazione di un report."""

    def __init__(self):
        self.stato = "in_attesa"  # in_attesa, in_elaborazione, completato, errore
        self.percentuale_completamento = 0
        self.file_generati = []
        self.errori = []


# Dizionario per tenere traccia dello stato dei report
report_status = {}

# Directory di lavoro per i report
REPORT_DIR = os.environ.get("REPORT_DIR", "/app/workspace")
os.makedirs(REPORT_DIR, exist_ok=True)


def resize_image(image_path, max_size_mb=4):
    """Ridimensiona un'immagine perché sia sotto il limite specificato di dimensione."""
    from PIL import Image

    target_size = max_size_mb * 1024 * 1024  # Conversione in byte

    # Controlla la dimensione attuale
    current_size = os.path.getsize(image_path)
    if current_size <= target_size:
        return  # L'immagine è già sotto il limite

    # Apri l'immagine
    with Image.open(image_path) as img:
        # Calcola il fattore di riduzione
        reduction_factor = (target_size / current_size) ** 0.5

        # Calcola le nuove dimensioni
        new_width = int(img.width * reduction_factor)
        new_height = int(img.height * reduction_factor)

        # Ridimensiona l'immagine
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        # Salva l'immagine ridimensionata
        resized_img.save(image_path, optimize=True, quality=85)


async def html_content_to_file(
    content, filepath, title, cartella_report, argomento, css_styles
):
    """Converte del contenuto HTML in un file HTML completo con stili."""
    # Rimuovi eventuali tag HTML esistenti
    import html
    import re

    content = html.unescape(content)
    content = re.sub(r"<[^>]*>", "", content)

    # Costruisci la navigazione
    nav_items = []
    files = [f for f in os.listdir(cartella_report) if f.endswith(".html")]
    for file in files:
        name = file.replace(".html", "").replace("_", " ").title()
        nav_items.append(f'<a href="{file}">{name}</a>')

    nav_menu = '<div class="nav-menu">\n    ' + "\n    ".join(nav_items) + "\n</div>"

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
        <h1>{title}</h1>
        {content}
    </div>
    <div class="footnote">
        Report generato il {datetime.datetime.now().strftime('%d/%m/%Y')} - OpenManus Report Generator
    </div>
</body>
</html>"""

    async with aiofiles.open(filepath, "w") as f:
        await f.write(template)

    return filepath


async def call_openai_api(prompt, model="gpt-4o"):
    """Chiama l'API di OpenAI per generare contenuti."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Sei un esperto di reportistica professionale che genera contenuti dettagliati, accurati e ben strutturati.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(
                    f"Errore nell'API OpenAI: {response.status} - {error_text}"
                )

            result = await response.json()
            return result["choices"][0]["message"]["content"]


async def genera_report_in_background(
    report_id: str,
    cartella_report: str,
    argomento: str,
    istruzioni: str,
    parametri_addizionali: Optional[Dict[str, Any]] = None,
):
    """Genera un report in background utilizzando direttamente l'API OpenAI."""
    try:
        # Aggiorna lo stato
        report_status[report_id].stato = "in_elaborazione"
        report_status[report_id].percentuale_completamento = 10

        # Ridimensiona le immagini nella cartella del report se esistono
        for file in os.listdir(cartella_report):
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                image_path = os.path.join(cartella_report, file)
                try:
                    resize_image(image_path, max_size_mb=4)
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

        # Imposta la directory di lavoro corrente alla cartella del report
        original_dir = os.getcwd()
        os.chdir(cartella_report)

        # Fase 1: Pianifica la struttura del report
        report_status[report_id].percentuale_completamento = 30
        planning_prompt = f"""
        Sei un esperto di reportistica professionale. Devi pianificare un report completo su '{argomento}'.

        ISTRUZIONI SPECIFICHE:
        {istruzioni}

        Per favore, crea un piano dettagliato per il report che includa:
        1. Il titolo principale del report
        2. Un elenco di 4-6 sezioni/capitoli da includere nel report
        3. Per ogni sezione, fornisci una breve descrizione di cosa dovrebbe coprire
        4. Suggerisci nomi di file HTML separati per ogni sezione principale (es. index.html, capitolo1.html, etc.)

        Il tuo output deve essere in formato JSON come il seguente:
        {{
            "titolo_report": "Titolo principale",
            "sezioni": [
                {{
                    "nome_file": "index.html",
                    "titolo": "Introduzione",
                    "descrizione": "Questa sezione introdurrà l'argomento e darà una panoramica"
                }},
                ...
            ]
        }}

        IMPORTANTE: Rispondi SOLO con il JSON, senza spiegazioni o testo aggiuntivo.
        """

        try:
            structure_json = await call_openai_api(planning_prompt)
            # Trova dove inizia e finisce il JSON nella risposta
            json_start = structure_json.find("{")
            json_end = structure_json.rfind("}")

            if json_start >= 0 and json_end >= 0:
                structure_json = structure_json[json_start : json_end + 1]
                structure = json.loads(structure_json)
            else:
                # Fallback se non riusciamo a estrarre il JSON
                structure = {
                    "titolo_report": argomento,
                    "sezioni": [
                        {
                            "nome_file": "index.html",
                            "titolo": "Introduzione",
                            "descrizione": "Panoramica generale dell'argomento",
                        },
                        {
                            "nome_file": "analisi.html",
                            "titolo": "Analisi Dettagliata",
                            "descrizione": "Analisi approfondita dell'argomento",
                        },
                        {
                            "nome_file": "conclusioni.html",
                            "titolo": "Conclusioni",
                            "descrizione": "Riassunto e considerazioni finali",
                        },
                    ],
                }
        except Exception as e:
            logger.error(f"Errore durante la pianificazione del report: {e}")
            # Utilizziamo una struttura di default in caso di errore
            structure = {
                "titolo_report": argomento,
                "sezioni": [
                    {
                        "nome_file": "index.html",
                        "titolo": "Introduzione",
                        "descrizione": "Panoramica generale dell'argomento",
                    },
                    {
                        "nome_file": "analisi.html",
                        "titolo": "Analisi Dettagliata",
                        "descrizione": "Analisi approfondita dell'argomento",
                    },
                    {
                        "nome_file": "conclusioni.html",
                        "titolo": "Conclusioni",
                        "descrizione": "Riassunto e considerazioni finali",
                    },
                ],
            }

        # Fase 2: Generazione di ogni sezione del report
        report_status[report_id].percentuale_completamento = 40
        total_sections = len(structure["sezioni"])
        progress_per_section = (
            50 / total_sections
        )  # Dividiamo il restante 50% tra le sezioni

        for i, section in enumerate(structure["sezioni"]):
            section_prompt = f"""
            Sei un esperto di reportistica professionale. Genera un contenuto dettagliato per la sezione "{section['titolo']}" di un report su '{argomento}'.

            INFORMAZIONI GENERALI:
            - Questo contenuto farà parte di un report più ampio intitolato "{structure['titolo_report']}"
            - La sezione deve coprire: {section['descrizione']}

            ISTRUZIONI SPECIFICHE DEL CLIENTE:
            {istruzioni}

            REQUISITI DI QUALITÀ:
            - Contenuto dettagliato e approfondito (almeno 1000 parole)
            - Utilizza sottotitoli (h2, h3) per organizzare il contenuto
            - Includi dati specifici, statistiche e riferimenti concreti
            - Crea tabelle comparative dove utile
            - Usa elenchi puntati per elencare caratteristiche o elementi
            - Per la prima sezione, includi un'introduzione al report completo
            - Se appropriato, includi una descrizione delle metodologie o delle fonti utilizzate

            FORMATO DI OUTPUT:
            - Contenuto in formato HTML semplice (solo tag h1, h2, h3, p, ul, li, table, etc.)
            - Non includere l'intestazione HTML, solo il contenuto
            """

            try:
                content = await call_openai_api(section_prompt)
                file_path = os.path.join(cartella_report, section["nome_file"])
                await html_content_to_file(
                    content,
                    file_path,
                    section["titolo"],
                    cartella_report,
                    argomento,
                    css_styles,
                )
                report_status[report_id].file_generati.append(section["nome_file"])

                # Aggiorna la percentuale di completamento
                current_progress = 40 + (i + 1) * progress_per_section
                report_status[report_id].percentuale_completamento = int(
                    current_progress
                )
            except Exception as e:
                logger.error(
                    f"Errore durante la generazione della sezione {section['titolo']}: {e}"
                )
                # Continua con la prossima sezione anche se questa fallisce

        # Torna alla directory originale
        os.chdir(original_dir)

        # Verifica se sono stati generati file HTML
        html_files = [f for f in os.listdir(cartella_report) if f.endswith(".html")]
        if not html_files:
            raise Exception("Nessun file HTML è stato generato durante il processo")

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


@app.post("/generate", status_code=202)
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Endpoint per la generazione di un nuovo report."""
    # Crea un ID univoco per il report
    report_id = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Crea una cartella per il report
    cartella_report = os.path.join(REPORT_DIR, report_id)
    os.makedirs(cartella_report, exist_ok=True)

    # Inizializza lo stato del report
    report_status[report_id] = ReportStatus()

    # Avvia la generazione del report in background
    background_tasks.add_task(
        genera_report_in_background,
        report_id,
        cartella_report,
        request.argomento,
        request.istruzioni,
        request.parametri_addizionali,
    )

    return {"report_id": report_id, "stato": "in_attesa"}


@app.get("/status/{report_id}")
async def get_report_status(report_id: str):
    """Endpoint per ottenere lo stato di avanzamento di un report."""
    if report_id not in report_status:
        raise HTTPException(status_code=404, detail="Report non trovato")

    status = report_status[report_id]
    return {
        "report_id": report_id,
        "stato": status.stato,
        "percentuale_completamento": status.percentuale_completamento,
        "file_generati": status.file_generati,
        "errori": status.errori,
    }


@app.get("/reports")
async def list_reports():
    """Endpoint per ottenere la lista di tutti i report."""
    return {
        "reports": [
            {
                "report_id": report_id,
                "stato": status.stato,
                "percentuale_completamento": status.percentuale_completamento,
            }
            for report_id, status in report_status.items()
        ]
    }


@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Endpoint per eliminare un report."""
    if report_id not in report_status:
        raise HTTPException(status_code=404, detail="Report non trovato")

    # Rimuovi la cartella del report
    cartella_report = os.path.join(REPORT_DIR, report_id)
    if os.path.exists(cartella_report):
        try:
            shutil.rmtree(cartella_report)
        except Exception as e:
            logger.error(
                f"Errore durante l'eliminazione della cartella {cartella_report}: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Errore durante l'eliminazione del report: {str(e)}",
            )

    # Rimuovi lo stato del report
    del report_status[report_id]

    return {"report_id": report_id, "stato": "eliminato"}


# Monta la directory dei file statici
app.mount("/files", StaticFiles(directory=REPORT_DIR), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
