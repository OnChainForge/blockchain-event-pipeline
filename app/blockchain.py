import logging
from datetime import datetime, timezone
from web3 import Web3

from app.config import settings

logger = logging.getLogger("blockchain")

w3 = Web3(Web3.HTTPProvider(settings.ethereum_rpc_url))


def get_latest_block_number() -> int:
    """Returns the most recent block number on the network."""
    return w3.eth.block_number


def fetch_block_with_transactions(block_number: int) -> dict:
    """
    Fetches a full block (with transaction bodies) and normalizes each
    transaction into a flat dict. Returns the block metadata plus a
    list of normalized transactions.
    """
    block = w3.eth.get_block(block_number, full_transactions=True)

    normalized_txs = []
    for tx in block["transactions"]:
        try:
            receipt = w3.eth.get_transaction_receipt(tx["hash"])
        except Exception as e:
            logger.warning(f"Could not fetch receipt for {tx['hash'].hex()}: {e}")
            continue

        value_eth = float(w3.from_wei(tx["value"], "ether"))
        gas_price_gwei = float(w3.from_wei(tx.get("gasPrice", 0), "gwei"))
        is_contract_call = tx["input"] not in ("0x", b"")

        try:
            to_is_contract = w3.eth.get_code(tx["to"]) != b"" if tx["to"] else False
        except Exception:
            to_is_contract = False

        normalized_txs.append({
            "tx_hash": tx["hash"].hex(),
            "block_number": block_number,
            "from_address": tx["from"],
            "to_address": tx["to"],
            "value_eth": value_eth,
            "gas_used": receipt["gasUsed"],
            "gas_price_gwei": gas_price_gwei,
            "status": receipt["status"],
            "is_contract_call": is_contract_call,
            "to_is_contract": to_is_contract,
        })

    return {
        "block_number": block_number,
        "timestamp": datetime.fromtimestamp(block["timestamp"], tz=timezone.utc),
        "tx_count": len(normalized_txs),
        "transactions": normalized_txs,
    }
