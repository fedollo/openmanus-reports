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

    # Aggiungi struttura ai contenuti con analisi delle sezioni
    content_sections = []
    lines = content.split("\n")
    current_section = ""
    current_title = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Identifica i titoli di sezione (righe più corte e non terminanti con punto)
        if (
            len(line) < 60
            and not line.endswith(".")
            and not line.endswith("?")
            and not line.endswith("!")
        ):
            if current_section:
                content_sections.append((current_title, current_section))
                current_section = ""
            current_title = line
        else:
            if current_title and not current_section:
                current_section = line
            else:
                current_section += "\n<p>" + line + "</p>"

    # Aggiungi l'ultima sezione
    if current_section:
        content_sections.append((current_title, current_section))

    # Formatta i contenuti in HTML strutturato
    formatted_content = ""
    for i, (section_title, section_content) in enumerate(content_sections):
        section_id = f"section-{i+1}"
        formatted_content += f"""
        <div class="content-section" id="{section_id}">
            <h2>{section_title}</h2>
            <div class="section-content">
                {section_content}
            </div>
        </div>
        """

    # Se non ci sono sezioni, usa il contenuto originale
    if not content_sections:
        formatted_content = f"<div class='content-section'><div class='section-content'>{content}</div></div>"

    # Costruisci la navigazione
    nav_items = []
    files = [f for f in os.listdir(cartella_report) if f.endswith(".html")]
    for file in files:
        name = file.replace(".html", "").replace("_", " ").title()
        nav_items.append(f'<a href="{file}">{name}</a>')

    nav_menu = '<div class="nav-menu">\n    ' + "\n    ".join(nav_items) + "\n</div>"

    # Costruisci la navigazione interna
    toc_items = []
    for i, (section_title, _) in enumerate(content_sections):
        section_id = f"section-{i+1}"
        toc_items.append(f'<li><a href="#{section_id}">{section_title}</a></li>')

    table_of_contents = ""
    if toc_items:
        table_of_contents = f"""
        <div class="table-of-contents">
            <h3>Indice dei contenuti</h3>
            <ul>
                {"".join(toc_items)}
            </ul>
        </div>
        """

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
    <header>
        <div class="header-content">
            <h1>{argomento}</h1>
            <p class="report-subtitle">{title}</p>
        </div>
    </header>

    {nav_menu}

    <div class="main-container">
        <div class="report-content">
            {table_of_contents}
            {formatted_content}
        </div>
    </div>

    <div class="footnote">
        Report generato il {datetime.datetime.now().strftime('%d/%m/%Y')} - OpenManus Report Generator
    </div>

    <script>
        // Script per abilitare il toggle delle sezioni
        document.addEventListener('DOMContentLoaded', function() {{
            const sections = document.querySelectorAll('.content-section h2');
            sections.forEach(section => {{
                section.addEventListener('click', function() {{
                    this.parentElement.classList.toggle('collapsed');
                }});
            }});

            // Evidenzia la voce di menu attiva
            const currentPage = window.location.pathname.split('/').pop();
            const menuItems = document.querySelectorAll('.nav-menu a');
            menuItems.forEach(item => {{
                if (item.getAttribute('href') === currentPage) {{
                    item.classList.add('active');
                }}
            }});
        }});
    </script>
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
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Playfair+Display:wght@400;700&display=swap');

        :root {
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --accent-color: #e74c3c;
            --background-color: #f9f9f9;
            --content-bg: #ffffff;
            --text-color: #333333;
            --border-color: #dddddd;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
            --radius: 8px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Roboto', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
            padding: 0;
            margin: 0;
        }

        header {
            background-color: var(--secondary-color);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        .header-content h1 {
            font-family: 'Playfair Display', serif;
            font-size: 2.5rem;
            margin: 0;
            padding: 0;
            color: white;
            border: none;
        }

        .report-subtitle {
            font-size: 1.2rem;
            font-weight: 300;
            margin-top: 0.5rem;
            opacity: 0.9;
        }

        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .report-content {
            background-color: var(--content-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 2rem;
        }

        .table-of-contents {
            background-color: rgba(52, 152, 219, 0.1);
            border-left: 4px solid var(--primary-color);
            padding: 1.5rem;
            margin-bottom: 2rem;
            border-radius: 0 var(--radius) var(--radius) 0;
        }

        .table-of-contents h3 {
            margin-top: 0;
            color: var(--secondary-color);
            font-size: 1.3rem;
        }

        .table-of-contents ul {
            margin: 1rem 0 0 1.5rem;
        }

        .table-of-contents a {
            text-decoration: none;
            color: var(--primary-color);
            font-weight: 500;
            display: block;
            padding: 0.3rem 0;
            transition: all 0.2s ease;
        }

        .table-of-contents a:hover {
            color: var(--secondary-color);
            transform: translateX(5px);
        }

        .content-section {
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }

        .content-section:last-child {
            border-bottom: none;
        }

        .content-section h2 {
            color: var(--secondary-color);
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            margin-bottom: 1.2rem;
            border-left: 4px solid var(--primary-color);
            padding-left: 1rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .content-section h2:after {
            content: "−";
            font-size: 1.5rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .content-section.collapsed h2:after {
            content: "+";
        }

        .content-section.collapsed .section-content {
            display: none;
        }

        .section-content {
            padding-left: 1rem;
        }

        h3 {
            color: var(--secondary-color);
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-size: 1.4rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }

        p {
            margin: 1rem 0;
            text-align: justify;
            font-size: 1rem;
            line-height: 1.8;
        }

        ul, ol {
            margin: 1.5rem 0 1.5rem 2rem;
        }

        li {
            margin-bottom: 0.5rem;
            line-height: 1.6;
        }

        a {
            color: var(--primary-color);
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        blockquote {
            font-style: italic;
            border-left: 4px solid var(--primary-color);
            margin: 1.5rem 0;
            padding: 0.5rem 0 0.5rem 1.5rem;
            background-color: rgba(52, 152, 219, 0.05);
        }

        code {
            font-family: monospace;
            background-color: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: var(--radius);
            overflow: hidden;
        }

        th {
            background-color: var(--primary-color);
            color: white;
            font-weight: 500;
            padding: 1rem;
            text-align: left;
        }

        td {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
        }

        tr:nth-child(even) {
            background-color: rgba(0,0,0,0.02);
        }

        tr:last-child td {
            border-bottom: none;
        }

        .nav-menu {
            background-color: var(--secondary-color);
            padding: 1rem;
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .nav-menu a {
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: var(--radius);
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .nav-menu a:hover, .nav-menu a.active {
            background-color: var(--primary-color);
        }

        .footnote {
            text-align: center;
            padding: 2rem;
            font-size: 0.9rem;
            color: #777;
            border-top: 1px solid var(--border-color);
            margin-top: 3rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .main-container {
                padding: 1rem;
            }

            header {
                padding: 1.5rem 1rem;
            }

            .header-content h1 {
                font-size: 2rem;
            }

            .report-content {
                padding: 1.5rem;
            }

            .content-section h2 {
                font-size: 1.5rem;
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

    # Crea il link per controllare lo stato del report
    base_url = os.environ.get("BASE_URL", "http://152.42.131.39:8001")
    status_url = f"{base_url}/status/{report_id}"

    return {"report_id": report_id, "stato": "in_attesa", "status_url": status_url}


@app.get("/status/{report_id}")
async def get_report_status(report_id: str):
    """Endpoint per ottenere lo stato di avanzamento di un report."""
    if report_id not in report_status:
        raise HTTPException(status_code=404, detail="Report non trovato")

    status = report_status[report_id]

    # Genera URL per ogni file HTML generato
    report_links = []
    base_url = os.environ.get("BASE_URL", "http://152.42.131.39:8001")

    for file in status.file_generati:
        if file.endswith(".html"):
            file_url = f"{base_url}/files/{report_id}/{file}"
            report_links.append(
                {
                    "nome": file.replace(".html", "").replace("_", " ").title(),
                    "url": file_url,
                }
            )

    return {
        "report_id": report_id,
        "stato": status.stato,
        "percentuale_completamento": status.percentuale_completamento,
        "file_generati": status.file_generati,
        "report_links": report_links,
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


@app.get("/links/{report_id}")
async def get_report_links(report_id: str):
    """Endpoint per ottenere i link ai file del report generato."""
    if report_id not in report_status:
        raise HTTPException(status_code=404, detail="Report non trovato")

    status = report_status[report_id]

    # Genera URL per ogni file HTML generato
    report_links = []
    base_url = os.environ.get("BASE_URL", "http://152.42.131.39:8001")

    for file in status.file_generati:
        if file.endswith(".html"):
            file_url = f"{base_url}/files/{report_id}/{file}"
            report_links.append(
                {
                    "nome": file.replace(".html", "").replace("_", " ").title(),
                    "url": file_url,
                }
            )

    return {
        "report_id": report_id,
        "stato": status.stato,
        "titolo": f"Report su {report_id.replace('report_', '')}",
        "links": report_links,
        "completato": status.stato == "completato",
    }


# Monta la directory dei file statici
app.mount("/files", StaticFiles(directory=REPORT_DIR), name="static")

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
