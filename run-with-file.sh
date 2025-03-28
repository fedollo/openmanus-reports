#!/bin/bash

# Script per eseguire OpenManus con istruzioni da file
# Utilizzo: ./run-with-file.sh <percorso_file_istruzioni>

if [ $# -ne 1 ]; then
    echo "Errore: inserisci il percorso del file con le istruzioni"
    echo "Utilizzo: ./run-with-file.sh <percorso_file_istruzioni>"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Errore: il file $1 non esiste"
    exit 1
fi

# Leggi il contenuto del file
ISTRUZIONI=$(cat "$1")

# Esegui OpenManus con le istruzioni dal file
python run_mcp.py -p "$ISTRUZIONI"
