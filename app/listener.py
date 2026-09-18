import asyncio
import logging
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.blockchain import get_latest_block_number, fetch_block_with_transactions
from app.models import Block, Transaction
from app.forwarder import forward_high_value_transaction

logger = logging.getLogger("listener")


def get_last_processed_block(db: Session) -> int | None:
    last_block = db.query(Block).order_by(Block.block_number.desc()).first()
    return last_block.block_number if last_block else None


def process_block(block_number: int) -> None:
    """
    Fetches, normalizes, stores, and forwards a single block's transactions.
    Runs in a worker thread (see run_listener_loop) since it performs
    blocking RPC calls and should never freeze the event loop. Commits
    after each transaction to keep write locks short, so reads on the
    API are never blocked for the duration of a whole block.
    """
    db = SessionLocal()
    try:
        block_data = fetch_block_with_transactions(block_number)

        db_block = Block(
            block_number=block_data["block_number"],
            timestamp=block_data["timestamp"],
            tx_count=block_data["tx_count"],
        )
        db.add(db_block)
        db.commit()

        for tx in block_data["transactions"]:
            existing = db.query(Transaction).filter(Transaction.tx_hash == tx["tx_hash"]).first()
            if existing:
                continue

            db_tx = Transaction(**tx)
            db.add(db_tx)
            db.commit()

            if tx["value_eth"] >= settings.min_value_eth_to_forward:
                forward_high_value_transaction(tx)
                db_tx.forwarded_to_risk_engine = True
                db.commit()

        logger.info(f"Processed block {block_number}: {block_data['tx_count']} transactions")
    except Exception as e:
        logger.error(f"Error processing block {block_number}: {e}")
        db.rollback()
    finally:
        db.close()


async def run_listener_loop():
    """
    Background loop: polls the network for new blocks and processes any
    that haven't been seen yet. Each block runs in a worker thread so
    blocking RPC calls never freeze the FastAPI event loop.
    """
    logger.info("Starting blockchain event listener...")

    while True:
        try:
            db = SessionLocal()
            try:
                last_processed = get_last_processed_block(db)
            finally:
                db.close()

            latest = get_latest_block_number()
            start_block = latest if last_processed is None else last_processed + 1

            for block_number in range(start_block, latest + 1):
                await asyncio.to_thread(process_block, block_number)

        except Exception as e:
            logger.error(f"Error in listener loop: {e}")

        await asyncio.sleep(settings.poll_interval_seconds)
