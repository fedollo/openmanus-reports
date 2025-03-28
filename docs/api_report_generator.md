# API Generatore di Report OpenManus

Questa API permette di generare report automaticamente utilizzando OpenManus. L'API crea una cartella con il nome dell'argomento specificato e genera file HTML con report, analisi e confronti basati sulle istruzioni fornite.

## Avvio del server

Per avviare il server API, eseguire:

```bash
python run_api_server.py
```

Il server sarà disponibile all'indirizzo `http://localhost:8001`.

## Endpoints

### Informazioni API

```
GET /
```

Fornisce informazioni sull'API e gli endpoint disponibili.

### Generazione Report

```
POST /genera-report
```

Genera un nuovo report basato su un argomento e istruzioni specifici.

**Parametri della richiesta (JSON):**

```json
{
  "argomento": "Nome dell'argomento del report",
  "istruzioni": "Istruzioni dettagliate per la generazione del report",
  "parametri_addizionali": {
    "chiave1": "valore1",
    "chiave2": "valore2"
  }
}
```

- `argomento`: il nome dell'argomento (diventerà il nome della cartella)
- `istruzioni`: istruzioni dettagliate per la generazione del report
- `parametri_addizionali`: (opzionale) parametri aggiuntivi per personalizzare il report

**Risposta:**

```json
{
  "report_id": "nome_argomento_1234",
  "cartella": "/percorso/alla/cartella",
  "stato": "in_coda"
}
```

### Stato Report

```
GET /stato-report/{report_id}
```

Controlla lo stato di avanzamento di un report.

**Risposta:**

```json
{
  "report_id": "nome_argomento_1234",
  "stato": "in_elaborazione",
  "percentuale_completamento": 45.0,
  "file_generati": ["istruzioni.txt", "panoramica.html"]
}
```

I possibili stati sono:
- `in_coda`: il report è in attesa di essere generato
- `in_elaborazione`: il report è in fase di generazione
- `completato`: il report è stato generato con successo
- `errore`: si è verificato un errore durante la generazione

### Lista Report

```
GET /lista-report
```

Elenca tutti i report disponibili con il loro stato.

**Risposta:**

```json
[
  {
    "report_id": "nome_argomento1_1234",
    "stato": "completato",
    "percentuale_completamento": 100.0,
    "file_generati": ["istruzioni.txt", "panoramica.html", "analisi.html", "confronto.html"]
  },
  {
    "report_id": "nome_argomento2_5678",
    "stato": "in_elaborazione",
    "percentuale_completamento": 30.0,
    "file_generati": ["istruzioni.txt"]
  }
]
```

### Eliminazione Report

```
DELETE /elimina-report/{report_id}
```

Elimina un report esistente e la relativa cartella.

**Risposta:**

```json
{
  "status": "success",
  "message": "Report nome_argomento_1234 eliminato con successo"
}
```

## Utilizzo da riga di comando

È possibile testare l'API utilizzando lo script `tools/test_report_api.py`:

```bash
python tools/test_report_api.py \
    --argomento "Costi servizi di trascrizione vocale" \
    --istruzioni "Stima il costo mensile di 200 conversazioni da 5 minuti con vari servizi di trascrizione. Confronta almeno 4 servizi come Whisper, Google e Microsoft."
```

Opzioni disponibili:
- `--host`: URL base dell'API (default: http://localhost:8001)
- `--argomento`: argomento del report (obbligatorio)
- `--istruzioni`: istruzioni per la generazione (obbligatorio)
- `--parametri`: parametri addizionali in formato JSON (opzionale)
- `--poll-interval`: intervallo in secondi per controllare lo stato (default: 5)
- `--timeout`: timeout in secondi per la generazione (default: 600)

## Esempi

### Esempio: Generazione report sui costi dei servizi cloud

```bash
python tools/test_report_api.py \
    --argomento "Costi Cloud Computing" \
    --istruzioni "Analizza i costi mensili di AWS, Google Cloud e Azure per un'applicazione web con 1000 utenti attivi al giorno. Considera storage, computing e database."
```

### Esempio: Generazione report con parametri aggiuntivi

```bash
python tools/test_report_api.py \
    --argomento "Analisi Framework Frontend" \
    --istruzioni "Confronta i framework frontend React, Vue e Angular" \
    --parametri '{"criteri": ["performance", "comunità", "curva di apprendimento"], "focus": "applicazioni enterprise"}'
```
