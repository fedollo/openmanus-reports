#!/usr/bin/env python
"""
Script per avviare il server API di OpenManus Report Generator.
"""
import os

import uvicorn

from app.api.report_generator import app
from app.api.serve_files import configure_static_files
from app.config import config
from app.logger import logger


def main():
    """Avvia il server API."""
    # Assicurati che la cartella workspace esista
    os.makedirs(config.workspace_root, exist_ok=True)

    # Configura gli endpoint per servire i file statici
    configure_static_files(app)

    logger.info(
        f"Avvio del server API OpenManus Report Generator sulla porta {config.api_port}"
    )
    logger.info(f"I report saranno salvati in: {config.workspace_root}")
    logger.info(
        f"I report sono accessibili tramite http://{config.api_host}:{config.api_port}/report/ID_REPORT"
    )

    # Avvia il server Uvicorn
    uvicorn.run(app, host=config.api_host, port=config.api_port, log_level="info")


if __name__ == "__main__":
    main()
