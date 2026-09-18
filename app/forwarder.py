import logging
import httpx

from app.config import settings

logger = logging.getLogger("forwarder")


def forward_high_value_transaction(tx: dict) -> None:
    """
    Sends a high-value transaction to the Risk Monitoring Engine for
    rule evaluation. Fire-and-forget: logs failures but never raises,
    so a forwarding error never breaks block processing.
    """
    payload = {
        "source": "blockchain-event-pipeline",
        "payload": tx,
    }

    try:
        response = httpx.post(f"{settings.risk_engine_url}/events/", json=payload, timeout=10.0)
        response.raise_for_status()
        logger.info(f"Forwarded tx {tx['tx_hash']} to risk engine")
    except Exception as e:
        logger.error(f"Failed to forward tx {tx['tx_hash']} to risk engine: {e}")
