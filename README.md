# OpenManus Report Generator

Un generatore di report professionale che crea documenti HTML ben formattati e interattivi.

## Caratteristiche

- Generazione di report HTML con stile moderno e professionale
- Supporto per tabelle, liste e formattazione avanzata
- Navigazione interattiva tra le sezioni
- Layout responsive per dispositivi mobili
- Gestione automatica delle immagini
- Monitoraggio dello stato di generazione in tempo reale

## Requisiti

- Python 3.8+
- FastAPI
- Pillow (per la gestione delle immagini)
- Uvicorn (per il server)

## Installazione

1. Clona il repository:
```bash
git clone https://github.com/yourusername/OpenManus.git
cd OpenManus
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

## Avvio del Server

```bash
python run_api_server.py
```

Il server sarà disponibile su `http://localhost:8001`

## API Endpoints

### 1. Generazione Report
```http
POST /genera-report
```

**Parametri:**
```json
{
    "argomento": "string",           // Titolo del report
    "istruzioni": "string",          // Istruzioni dettagliate per la generazione
    "parametri_addizionali": {       // Parametri opzionali
        "chiave": "valore"
    }
}
```

**Risposta:**
```json
{
    "report_id": "string",
    "cartella": "string",
    "stato": "string",
    "file_generati": ["string"]
}
```

### 2. Stato Report
```http
GET /stato-report/{report_id}
```

**Risposta:**
```json
{
    "report_id": "string",
    "stato": "string",
    "percentuale_completamento": float,
    "file_generati": ["string"],
    "errori": ["string"]
}
```

### 3. Lista Report
```http
GET /lista-report
```

**Risposta:**
```json
[
    {
        "report_id": "string",
        "stato": "string",
        "percentuale_completamento": float,
        "file_generati": ["string"],
        "errori": ["string"]
    }
]
```

### 4. Eliminazione Report
```http
DELETE /elimina-report/{report_id}
```

## Esempio di Utilizzo

```bash
# Genera un nuovo report
curl -X POST "http://localhost:8001/genera-report" \
     -H "Content-Type: application/json" \
     -d '{
           "argomento": "Analisi Framework Frontend",
           "istruzioni": "Confronta i framework frontend React, Vue e Angular",
           "parametri_addizionali": {
             "criteri": ["performance", "comunità", "curva di apprendimento"],
             "focus": "applicazioni enterprise"
           }
         }'

# Verifica lo stato del report
curl "http://localhost:8001/stato-report/{report_id}"

# Lista tutti i report
curl "http://localhost:8001/lista-report"

# Elimina un report
curl -X DELETE "http://localhost:8001/elimina-report/{report_id}"
```

## Struttura del Report

Il report generato include:
- Una pagina principale (index.html) con una panoramica
- Sezioni separate per argomenti specifici
- Tabelle comparative
- Liste di vantaggi e svantaggi
- Collegamenti ipertestuali tra le sezioni
- Stile CSS professionale e responsive

## Note

- Le immagini vengono automaticamente ridimensionate se superano i 5MB
- I report vengono salvati nella cartella `workspace`
- È possibile monitorare lo stato di generazione in tempo reale
- I report possono essere eliminati solo quando non sono in elaborazione

## Licenza

MIT License
