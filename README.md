# Blockchain Event Pipeline

A background listener that monitors new Ethereum blocks in real time, normalizes every transaction, persists it, and forwards high-value transactions via HTTP to the Risk Monitoring Engine for further analysis.

![Blockchain Event Pipeline screenshot](docs/screenshot.png)

📹 [Watch demo video](https://youtu.be/vAqVrAKZU7k)

**Live demo:** https://blockchain-event-pipeline-fronted.onrender.com  
**Backend API:** https://blockchain-event-pipeline.onrender.com/docs

## Problem

Reacting to on-chain activity in real time requires continuously watching new blocks as they're mined, extracting and normalizing transaction data, and deciding which transactions matter enough to act on — without missing blocks or double-processing them.

## Solution

A FastAPI service that:

1. Runs an asynchronous background listener (`listener.py`) alongside the Web API, polling for new blocks via `asyncio.to_thread`
2. Fetches and normalizes each transaction (`blockchain.py`)
3. Persists every transaction to the database
4. Forwards transactions above a configurable ETH threshold to the Risk Monitoring Engine via HTTP (`forwarder.py`, using `httpx`)
5. Exposes REST endpoints for the frontend to consume the live feed

## Architecture

Ethereum Network (RPC)
│
▼
Background Listener (app/listener.py)
│
▼
Normalize transaction (app/blockchain.py)
│
▼
Persist to SQLite (event_pipeline.db)
│
├──▶ value ≥ threshold? ──▶ Forward to Risk Monitoring Engine (app/forwarder.py, httpx)
│
▼
FastAPI REST API
│
▼
Frontend live feed (badge: "Flagged for review")


## Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite (WAL mode)
- **Blockchain:** Web3.py via Infura RPC
- **Forwarding:** httpx (async HTTP client)
- **Frontend:** Vanilla HTML/CSS/JS, dark theme, polling-based
- **Config:** pydantic-settings (`.env`)

## Running locally

Backend:
```bash
cd blockchain-event-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Infura API key and Risk Engine URL
uvicorn app.main:app --reload --port 8001
```

Frontend:
```bash
cd frontend
python3 -m http.server 5501
```

Open `http://localhost:5501`.

## API

| Method | Endpoint         | Description                              |
|--------|------------------|--------------------------------------------|
| GET    | `/transactions/` | List recent normalized transactions        |
| GET    | `/health`        | Health check                               |

## Technical decisions

- **Why a background listener over on-demand fetching:** the pipeline's job is to react to new blocks as they happen, not to answer one-off queries — a continuous listener is the right fit, unlike the on-demand analysis in Risk Monitoring Engine.
- **Why forward via HTTP instead of a shared database:** keeping services decoupled (each with its own database) means Risk Monitoring Engine can be queried independently and doesn't need direct access to this service's internals — only the transactions that matter cross the boundary.
- **Threshold as config:** the ETH value that triggers forwarding lives in `.env`, so it can be tuned without redeploying.
- **SQLite over Postgres (local):** same constraint as the other projects — `psycopg2-binary` build issues on Python 3.14 locally. Postgres is planned for Render.

## Challenges & learnings

- Early versions occasionally missed blocks when the RPC provider was slow to respond — solved by making the listener loop tolerant of individual block-fetch failures instead of crashing the whole background task.
- Deciding what counts as "high value" needed to be a runtime config, not a hardcoded constant, since the right threshold depends on current ETH price and what the receiving Risk Engine considers worth analyzing.

## License

MIT
