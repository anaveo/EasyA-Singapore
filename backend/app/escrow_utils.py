import asyncio
from datetime import datetime, timedelta
from cryptoconditions import PreimageSha256

from xrpl.wallet import Wallet
from xrpl.constants import CryptoAlgorithm
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.utils import datetime_to_ripple_time, xrp_to_drops
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.asyncio.transaction import submit_and_wait

from config import XRPL_SEED, XRPL_NODE_URL, ESCROW_PREIMAGE


async def create_escrow(destination_address: str, amount_xrp: float = 50.0):
    client = AsyncJsonRpcClient(XRPL_NODE_URL)
    wallet = Wallet.from_seed(XRPL_SEED, algorithm=CryptoAlgorithm.ED25519)

    # Prepare preimage + condition + fulfillment
    preimage = ESCROW_PREIMAGE.encode() if isinstance(ESCROW_PREIMAGE, str) else ESCROW_PREIMAGE
    cc = PreimageSha256(preimage=preimage)
    condition = cc.condition_binary.hex().upper()
    fulfillment = cc.serialize_binary().hex().upper()

    # Timing windows
    finish_after = datetime_to_ripple_time(datetime.now() + timedelta(seconds=30))
    cancel_after = datetime_to_ripple_time(datetime.now() + timedelta(minutes=5))

    tx = EscrowCreate(
        account=wallet.classic_address,
        destination=destination_address,
        amount=xrp_to_drops(amount_xrp),
        finish_after=finish_after,
        cancel_after=cancel_after,
        condition=condition
    )

    print("[create_escrow] Submitting escrow transaction...")
    response = await submit_and_wait(tx, client, wallet)
    sequence = response.result["tx_json"]["Sequence"]

    return {
        "sequence": sequence,
        "condition": condition,
        "fulfillment": fulfillment,
        "destination": destination_address,
        "tx_hash": response.result.get("hash")
    }


async def fulfill_escrow(sequence: int):
    client = AsyncJsonRpcClient(XRPL_NODE_URL)
    wallet = Wallet.from_seed(XRPL_SEED, algorithm=CryptoAlgorithm.ED25519)

    preimage = ESCROW_PREIMAGE.encode() if isinstance(ESCROW_PREIMAGE, str) else ESCROW_PREIMAGE
    cc = PreimageSha256(preimage=preimage)
    condition = cc.condition_binary.hex().upper()
    fulfillment = cc.serialize_binary().hex().upper()

    tx = EscrowFinish(
        account=wallet.classic_address,
        owner=wallet.classic_address,
        offer_sequence=sequence,
        condition=condition,
        fulfillment=fulfillment
    )

    print(f"[fulfill_escrow] Submitting escrow finish for sequence {sequence}...")
    response = await submit_and_wait(tx, client, wallet)
    return {
        "status": "Escrow claimed",
        "tx_hash": response.result.get("hash")
    }
