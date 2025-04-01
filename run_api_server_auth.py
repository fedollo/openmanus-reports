#!/usr/bin/env python
"""
Script per avviare il server API di OpenManus Report Generator con autenticazione.
"""
import os

import uvicorn
from app.api.report_generator_auth import app
from app.api.serve_files import configure_static_files
from app.config import config
from app.logger import logger


def main():
    """Avvia il server API con autenticazione."""
    # Assicurati che la cartella workspace esista
    os.makedirs(config.workspace_root, exist_ok=True)

    # Configura gli endpoint per servire i file statici
    configure_static_files(app)

    api_port = 8009  # Porta specifica per questa versione dell'API

    logger.info(
        f"Avvio del server API OpenManus Report Generator con autenticazione sulla porta {api_port}"
    )
    logger.info(f"I report saranno salvati in: {config.workspace_root}")
    logger.info(
        f"I report sono accessibili tramite http://{config.api_host}:{api_port}/report/ID_REPORT"
    )
    logger.info(
        f"Interfaccia Swagger disponibile su http://{config.api_host}:{api_port}/docs"
    )
    logger.info(f"Credenziali di accesso: admin/shakazamba2025")

    # Avvia il server Uvicorn
    uvicorn.run(app, host=config.api_host, port=api_port, log_level="info")


if __name__ == "__main__":
    main()
