# OpenManus Report Generator API

API per la generazione automatica di report HTML utilizzando modelli AI di OpenAI.

## Caratteristiche

- Generazione di report strutturati con sezioni multiple
- Utilizzo di OpenAI GPT-4o per creare contenuti professionali
- Supporto per la generazione in background con monitoraggio dello stato
- Layout HTML responsivo con CSS integrato
- API RESTful con documentazione interattiva
- Supporto per parametri personalizzati

## Requisiti

- Python 3.8+
- Docker e Docker Compose (per l'esecuzione containerizzata)
- Una chiave API OpenAI valida

## Installazione

### Tramite Docker (consigliato)

1. Clona il repository:
   ```bash
   git clone https://github.com/fedollo/openmanus-reports.git
   cd openmanus-reports
   ```

2. Crea un file `.env` nella root del progetto con la tua chiave API OpenAI:
   ```
   OPENAI_API_KEY=sk-your-api-key
   BASE_URL=http://your-server-address:8001
   ```

3. Avvia il servizio con Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Manualmente

1. Clona il repository:
   ```bash
   git clone https://github.com/fedollo/openmanus-reports.git
   cd openmanus-reports
   ```

2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

3. Imposta le variabili d'ambiente:
   ```bash
   export OPENAI_API_KEY=sk-your-api-key
   export BASE_URL=http://your-server-address:8001
   ```

4. Avvia il servizio:
   ```bash
   python report_generator_direct.py
   ```

## Utilizzo dell'API

L'API è accessibile all'indirizzo `http://your-server-address:8001` (o la porta configurata).

### Documentazione interattiva

La documentazione interattiva OpenAPI è disponibile all'URL:
```
http://your-server-address:8001/docs
```

### Generazione di un report

Per generare un nuovo report, invia una richiesta POST a `/generate` con un payload JSON contenente:

```json
{
  "argomento": "Intelligenza Artificiale",
  "istruzioni": "Crea un report completo sull'intelligenza artificiale, includendo storia, applicazioni attuali e prospettive future.",
  "parametri_addizionali": {
    "lunghezza": "medio",
    "focus": "business"
  }
}
```

La risposta includerà un ID univoco per il report e un URL per verificarne lo stato:

```json
{
  "report_id": "report_20250329_180346",
  "stato": "in_attesa",
  "status_url": "http://your-server-address:8001/status/report_20250329_180346"
}
```

### Controllo dello stato di un report

Per verificare lo stato di avanzamento di un report, invia una richiesta GET a `/status/{report_id}`:

```
GET http://your-server-address:8001/status/report_20250329_180346
```

La risposta includerà informazioni dettagliate sullo stato, la percentuale di completamento e i link ai file generati:

```json
{
  "report_id": "report_20250329_180346",
  "stato": "in_elaborazione",
  "percentuale_completamento": 70,
  "file_generati": ["istruzioni.txt", "index.html", "analisi.html"],
  "report_links": [
    {
      "nome": "Index",
      "url": "http://your-server-address:8001/files/report_20250329_180346/index.html"
    },
    {
      "nome": "Analisi",
      "url": "http://your-server-address:8001/files/report_20250329_180346/analisi.html"
    }
  ],
  "errori": []
}
```

### Ottenimento dei link a un report

Per ottenere solo i link ai file HTML generati, invia una richiesta GET a `/links/{report_id}`:

```
GET http://your-server-address:8001/links/report_20250329_180346
```

La risposta includerà i link ai file HTML per la visualizzazione diretta:

```json
{
  "report_id": "report_20250329_180346",
  "stato": "completato",
  "titolo": "Report su 20250329_180346",
  "links": [
    {
      "nome": "Index",
      "url": "http://your-server-address:8001/files/report_20250329_180346/index.html"
    },
    {
      "nome": "Analisi",
      "url": "http://your-server-address:8001/files/report_20250329_180346/analisi.html"
    },
    {
      "nome": "Conclusioni",
      "url": "http://your-server-address:8001/files/report_20250329_180346/conclusioni.html"
    }
  ],
  "completato": true
}
```

### Elenco di tutti i report

Per ottenere un elenco di tutti i report generati, invia una richiesta GET a `/reports`:

```
GET http://your-server-address:8001/reports
```

### Eliminazione di un report

Per eliminare un report, invia una richiesta DELETE a `/reports/{report_id}`:

```
DELETE http://your-server-address:8001/reports/report_20250329_180346
```

## Configurazione

Il servizio può essere configurato tramite le seguenti variabili d'ambiente:

- `OPENAI_API_KEY`: La chiave API OpenAI (obbligatoria)
- `BASE_URL`: L'URL base per generare i link ai report (default: `http://152.42.131.39:8001`)
- `REPORT_DIR`: La directory in cui salvare i report generati (default: `/app/workspace`)
- `PORT`: La porta su cui eseguire il server (default: `8000`)

## Risoluzione dei problemi

### Il report rimane in stato "in_elaborazione"

- Verifica che la chiave API OpenAI sia valida e disponga di credito sufficiente
- Controlla i log del container Docker per errori specifici:
  ```bash
  docker logs openmanus-report-generator-1
  ```

### Non riesco ad accedere ai file generati

- Verifica che la variabile d'ambiente `BASE_URL` sia impostata correttamente
- Assicurati che il container esponga correttamente la porta `8001`
- Controlla che il volume Docker per la directory `workspace` sia configurato correttamente

## Note

- Le immagini vengono automaticamente ridimensionate se superano i 5MB
- I report vengono salvati nella cartella `workspace`
- È possibile monitorare lo stato di generazione in tempo reale
- I report possono essere eliminati solo quando non sono in elaborazione

## Licenza

MIT License
