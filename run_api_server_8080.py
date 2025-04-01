#!/usr/bin/env python
"""
Script per avviare il server API di OpenManus Report Generator sulla porta 8080 con autenticazione.
"""
import os
import secrets
from typing import Optional

import uvicorn
from app.api.report_generator import app as original_app
from app.api.serve_files import configure_static_files
from app.config import config
from app.logger import logger
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware

# Credenziali per l'autenticazione basic
USERNAME = os.environ.get("API_USERNAME")
PASSWORD = os.environ.get("API_PASSWORD")

# Se le credenziali non sono impostate, generiamo una password casuale
if not USERNAME or not PASSWORD:
    USERNAME = USERNAME or "admin"
    PASSWORD = PASSWORD or secrets.token_urlsafe(12)
    logger.warning("Credenziali di autenticazione non configurate tramite variabili d'ambiente!")
    logger.warning(f"USERNAME generato: {USERNAME}")
    logger.warning(f"PASSWORD generata: {PASSWORD}")
    logger.warning("Imposta API_USERNAME e API_PASSWORD come variabili d'ambiente per personalizzare le credenziali")

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verifica le credenziali per l'autenticazione basic."""
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Crea una nuova app copiando la configurazione dall'app originale
app = FastAPI(
    title="OpenManus Report Generator",
    description="API per la generazione di report professionali",
    version="1.0.0",
    docs_url=None,  # Disabilitiamo l'URL docs predefinito
    redoc_url=None,  # Disabilitiamo l'URL redoc predefinito
)

# Copiamo tutti i router dall'app originale
for route in original_app.routes:
    app.routes.append(route)

# Configuriamo i middleware manualmente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint personalizzato per la documentazione Swagger con autenticazione
@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    """Endpoint per la documentazione Swagger protetta da autenticazione basic."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Documentazione API",
    )


# Endpoint per lo schema OpenAPI
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema(username: str = Depends(get_current_username)):
    """Endpoint per lo schema OpenAPI protetto da autenticazione basic."""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


def main():
    """Avvia il server API sulla porta 8080."""
    # Assicurati che la cartella workspace esista
    os.makedirs(config.workspace_root, exist_ok=True)

    # Configura gli endpoint per servire i file statici
    configure_static_files(app)

    logger.info(f"Avvio del server API OpenManus Report Generator sulla porta 8080")
    logger.info(f"I report saranno salvati in: {config.workspace_root}")
    logger.info(
        f"I report sono accessibili tramite http://{config.api_host}:8080/report/ID_REPORT"
    )
    logger.info(
        f"La documentazione API è accessibile tramite http://{config.api_host}:8080/docs (richiede autenticazione)"
    )

    # Avvia il server Uvicorn sulla porta 8080
    uvicorn.run(app, host=config.api_host, port=8080, log_level="info")


if __name__ == "__main__":
    main()
