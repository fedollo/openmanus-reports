# Bitcoin Trading Bot

Bot automatico per il trading di Bitcoin con leva, basato su analisi tecnica e gestione del rischio.

## Requisiti

- Docker e Docker Compose
- Python 3.9+
- Node.js 18+ (per il frontend)

## Setup

1. Clona il repository:
```bash
git clone <repository-url>
cd bitcoin-trading-app
```

2. Copia il file delle variabili d'ambiente:
```bash
cp backend/.env.example backend/.env
```

3. Configura le variabili d'ambiente nel file `backend/.env`:
- Inserisci il tuo token del bot Telegram
- Configura le API keys di Binance
- Personalizza i parametri di trading se necessario

4. Avvia l'applicazione con Docker Compose:
```bash
cd docker
docker-compose up --build
```

L'applicazione sarà disponibile su:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000 (quando implementato)

## Struttura del Progetto

```
bitcoin-trading-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   └── (da implementare)
└── docker/
    ├── Dockerfile.backend
    └── docker-compose.yml
```

## API Endpoints

### Segnali
- `GET /api/signals` - Lista dei segnali generati
- `POST /api/signals` - Nuovo segnale
- `GET /api/signals/{id}` - Dettaglio segnale

### Operazioni
- `GET /api/trades` - Lista delle operazioni
- `POST /api/trades` - Nuova operazione
- `PUT /api/trades/{id}` - Aggiorna operazione

### Performance
- `GET /api/performance` - Statistiche generali
- `GET /api/performance/daily` - Report giornaliero
- `GET /api/performance/weekly` - Report settimanale

## Sviluppo

1. Ambiente di sviluppo:
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # o `venv\Scripts\activate` su Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (quando implementato)
cd frontend
npm install
npm run dev
```

2. Test:
```bash
cd backend
pytest
```

## Sicurezza

- Non condividere mai le tue API keys
- Usa sempre HTTPS in produzione
- Implementa rate limiting
- Monitora regolarmente i log

## Contribuire

1. Fork il repository
2. Crea un branch per la tua feature
3. Commit le modifiche
4. Push al branch
5. Crea una Pull Request

## Licenza

MIT
