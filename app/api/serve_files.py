"""
Modulo per servire file statici dalla directory workspace.

Questo modulo configura FastAPI per servire file statici dalla directory di workspace,
e fornisce endpoint per servire direttamente i report generati.
"""

import os
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import config
from app.logger import logger

# CSS per i report
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

.nav-menu {
    background-color: #2c3e50;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 20px;
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

@media (max-width: 768px) {
    body {
        padding: 10px;
    }

    .nav-menu {
        position: static;
    }
}
"""


def configure_static_files(app: FastAPI):
    """
    Configura gli endpoint per servire file statici dalla directory workspace.

    Args:
        app: L'istanza FastAPI da configurare
    """
    # Monta la directory workspace per servire file statici
    app.mount(
        "/reports", StaticFiles(directory=config.workspace_root), name="static_files"
    )

    # Aggiungi compressione GZIP per migliorare le prestazioni
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Aggiungi un endpoint per servire i file HTML con CSS aggiunto
    @app.get("/reports-styled/{path:path}")
    async def serve_styled_report(path: str, request: Request):
        """Serve file HTML dalla directory workspace con CSS aggiunto."""
        file_path = Path(config.workspace_root) / path

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {path} non trovato")

        if not file_path.is_file():
            raise HTTPException(status_code=400, detail=f"{path} non è un file")

        if not str(file_path).endswith(".html"):
            # Per i file non HTML, utilizza FileResponse per servirli direttamente
            return FileResponse(str(file_path))

        # Per i file HTML, leggi il contenuto, aggiungi CSS e menu
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Verifica se il file ha già uno stile CSS
            if "<style>" not in content:
                # Aggiungi lo stile CSS al file
                if "<head>" in content:
                    content = content.replace(
                        "<head>", f"<head>\n<style>\n{css_styles}\n</style>"
                    )
                else:
                    # Se non c'è un tag head, aggiungi uno stile inline
                    content = content.replace(
                        "<body>",
                        f"<head>\n<style>\n{css_styles}\n</style>\n</head>\n<body>",
                    )
                    if "<body>" not in content:
                        # Se non c'è nemmeno un body, aggiungilo
                        content = f"<html><head><style>\n{css_styles}\n</style></head><body>{content}</body></html>"

            # Crea un menu di navigazione se non esiste già
            if ".nav-menu" not in content and "<body>" in content:
                # Ricava il percorso della directory dal path richiesto
                report_dir = file_path.parent

                if report_dir.exists() and report_dir.is_dir():
                    # Trova tutti i file HTML nella directory del report
                    nav_items = []
                    try:
                        files = [
                            f for f in os.listdir(report_dir) if f.endswith(".html")
                        ]
                        for file in files:
                            name = file.replace(".html", "").replace("_", " ").title()
                            report_path_parts = path.split("/")
                            # Usa l'URL styled per i link del menu
                            if len(report_path_parts) > 1:
                                base_url = (
                                    "/reports-styled/"
                                    + "/".join(report_path_parts[:-1])
                                    + "/"
                                )
                                nav_items.append(
                                    f'<a href="{base_url}{file}">{name}</a>'
                                )
                            else:
                                nav_items.append(f'<a href="{file}">{name}</a>')

                        if nav_items:
                            nav_menu = (
                                f'<div class="nav-menu">\n    '
                                + "\n    ".join(nav_items)
                                + "\n</div>"
                            )
                            # Inserisci il menu di navigazione dopo il tag body
                            content = content.replace("<body>", "<body>\n" + nav_menu)
                    except Exception as e:
                        logger.error(
                            f"Errore nella creazione del menu di navigazione: {e}"
                        )

            return HTMLResponse(content=content)
        except Exception as e:
            logger.error(f"Errore nel servire il file HTML con stile: {e}")
            raise HTTPException(
                status_code=500, detail=f"Errore nel servire il file: {str(e)}"
            )

    @app.get("/report/{report_id}")
    async def serve_report(report_id: str, request: Request):
        """
        Serve il file index.html di un report specifico.

        Args:
            report_id: L'ID del report da servire
            request: La richiesta HTTP

        Returns:
            Il file HTML del report
        """
        # Ricerca il report: prima prova direttamente con l'ID
        report_path = Path(config.workspace_root) / report_id

        # Se non esiste, prova a cercare directory che iniziano con il nome del report
        # ma potrebbero avere un suffisso numerico
        if not report_path.exists():
            # Estrai la parte base dell'ID (senza il suffisso numerico)
            base_id_match = re.match(r"(.+?)(?:_\d+)?$", report_id)
            if base_id_match:
                base_id = base_id_match.group(1)
                # Cerca directory che iniziano con base_id
                for item in os.listdir(config.workspace_root):
                    item_path = Path(config.workspace_root) / item
                    if item_path.is_dir() and item.startswith(base_id):
                        report_path = item_path
                        break

        # Se ancora non esiste, restituisci un errore
        if not report_path.exists() or not report_path.is_dir():
            raise HTTPException(
                status_code=404, detail=f"Report {report_id} non trovato"
            )

        index_path = report_path / "index.html"

        # Se il file index.html esiste, servilo
        if index_path.exists():
            # Leggi il contenuto del file
            with open(index_path, "r") as f:
                content = f.read()

            # Verifica se il file ha già uno stile CSS
            if "<style>" not in content:
                # Aggiungi lo stile CSS al file
                # Cerca il tag head per inserire lo stile
                if "<head>" in content:
                    content = content.replace(
                        "<head>", f"<head>\n<style>\n{css_styles}\n</style>"
                    )
                else:
                    # Se non c'è un tag head, aggiungi uno stile inline
                    content = content.replace(
                        "<body>",
                        f"<head>\n<style>\n{css_styles}\n</style>\n</head>\n<body>",
                    )

            # Crea un menu di navigazione se non esiste già
            if ".nav-menu" not in content:
                # Trova tutti i file HTML nella directory del report
                nav_items = []
                files = [f for f in os.listdir(report_path) if f.endswith(".html")]
                for file in files:
                    name = file.replace(".html", "").replace("_", " ").title()
                    if file == "index.html":
                        name = "Home"
                    # Usa l'URL styled per i link del menu
                    nav_items.append(
                        f'<a href="/reports-styled/{report_id}/{file}">{name}</a>'
                    )

                nav_menu = (
                    f'<div class="nav-menu">\n    '
                    + "\n    ".join(nav_items)
                    + "\n</div>"
                )

                # Inserisci il menu di navigazione dopo il tag body
                if "<body>" in content:
                    content = content.replace("<body>", "<body>\n" + nav_menu)

            return HTMLResponse(content=content)

        # Se il file index.html non esiste, elenca i file nella directory
        files = [f for f in os.listdir(report_path) if f.endswith(".html")]
        if not files:
            raise HTTPException(
                status_code=404,
                detail=f"Nessun file HTML trovato nel report {report_id}",
            )

        # Crea una pagina HTML con i link ai file
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Report {report_id}</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <h1>Report {report_id}</h1>
    <div class="section">
        <h2>File disponibili</h2>
        <ul>
"""
        for file in files:
            name = file.replace(".html", "").replace("_", " ").title()
            html_content += f'            <li><a href="/reports-styled/{report_id}/{file}">{name}</a></li>\n'

        html_content += """
        </ul>
    </div>
</body>
</html>
"""
        return HTMLResponse(content=html_content)

    logger.info("Configurazione degli endpoint per servire file statici completata")
