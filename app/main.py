import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.logging_config import setup_logging
from app.listener import run_listener_loop
from app import models, schemas

setup_logging()
logger = logging.getLogger("main")

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Starts the background listener when the app boots, cancels it on shutdown."""
    listener_task = asyncio.create_task(run_listener_loop())
    logger.info("Listener task started in background.")
    yield
    listener_task.cancel()
    logger.info("Listener task cancelled.")


app = FastAPI(
    title="Blockchain Event Pipeline",
    description="Listens to Ethereum blocks in real time, stores normalized transactions, and forwards high-value ones to the Risk Monitoring Engine.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/blocks/", response_model=list[schemas.BlockOut])
def list_blocks(db: Session = Depends(get_db)):
    return db.query(models.Block).order_by(models.Block.block_number.desc()).limit(20).all()


@app.get("/transactions/", response_model=list[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).order_by(models.Transaction.id.desc()).limit(50).all()
