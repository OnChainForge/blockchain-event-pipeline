 
# Whale Alert

A real-time Ethereum transaction listener microservice that monitors raw blocks for high-value ETH transfers ("whales"), uses Redis to perform atomic deduplication, persists transaction history, and exposes a REST API for real-time feed consumption.

![Blockchain Event Pipeline screenshot](docs/screenshot.png)

**Live demo:** _pending deployment_  
**Video walkthrough:** _pending_

## Problem

Scanning Ethereum mainnet blocks for massive transaction transfers generates high volumes of raw data. Without an efficient deduplication layer, background listeners risk persisting or broadcasting identical transaction events multiple times during re-scans or network delays.

## Solution

A FastAPI microservice that:

1. Runs an asynchronous background polling task alongside the Web API
2. Filters raw network transactions against a configurable ETH threshold
3. Verifies transaction novelty using Redis key caching to eliminate duplicate events
4. Persists verified whale transactions (`tx_hash`, `block_number`, `from_address`, `to_address`, `value_eth`, `detected_at`) in SQLite
5. Exposes REST endpoints (`/health`, `/alerts/`) for frontend and client consumption

## Architecture

Ethereum Network (RPC)│▼Background Polling Loop (app/listener.py)│┌────┴────────────────────────┐▼                             ▼Redis Deduplication Check    SQLite Persistence (whale_alerts)(dedup_health_check)              │▼FastAPI REST API (/alerts/)│▼Frontend Client Feed
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic v2
- **Cache / Deduplication**: Redis
- **Database**: SQLite
- **Frontend**: Vanilla HTML/JS

## Stack

Python · FastAPI · SQLAlchemy · Pydantic · Redis · SQLite

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in ETHEREUM_RPC_URL and REDIS_URL
uvicorn app.main:app --reload --port 8002
Frontend:Bashcd frontend
python3 -m http.server 5502
Open http://localhost:5502.APIMethodEndpointDescriptionGET/healthService health status and Redis connection verificationGET/alerts/Returns the 50 most recently detected whale transactionsTechnical decisionsPydantic v2 Object Relational Mapping: Configured ConfigDict(from_attributes=True) in response schemas (WhaleAlertOut) to seamlessly serialize SQLAlchemy model instances into JSON payloads.Atomic Indexing & Uniqueness: Explicitly indexed and constrained tx_hash at the database level (unique=True, index=True) alongside primary keys to enforce data integrity even under heavy ingestion.CORS Middleware Enablement: Standardized wildcards on origin access to decouple local static development servers from backend API services.Challenges & learningsHandled timezone awareness on record insertion by binding SQLAlchemy models to explicit UTC datetimes (datetime.now(timezone.utc)).Managed multi-service availability checks by validating Redis health status alongside standard application health endpoints.LicenseMITEOF
