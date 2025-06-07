"""
XRPL Microinsurance Utilities

This module provides utility functions to:
- Send insurance premiums
- Create conditional escrows for insurance payouts
- Fulfill or cancel escrows based on shipment health

"""

import asyncio
from datetime import datetime, timedelta
from typing import Union, Dict

from cryptoconditions import PreimageSha256
from xrpl.wallet import Wallet
from xrpl.constants import CryptoAlgorithm
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.utils import datetime_to_ripple_time, xrp_to_drops
from xrpl.models.transactions import Payment, EscrowCreate, EscrowFinish, EscrowCancel
from xrpl.asyncio.transaction import submit_and_wait

from config import XRPL_SEED, XRPL_NODE_URL, ESCROW_PREIMAGE


def get_wallet(seed: str) -> Wallet:
    """Returns a Wallet object from the given seed using ED25519."""
    return Wallet.from_seed(seed, algorithm=CryptoAlgorithm.ED25519)


def get_preimage_condition() -> tuple[str, str]:
    """Returns the condition and fulfillment hex strings from the preimage."""
    preimage_bytes = ESCROW_PREIMAGE.encode() if isinstance(ESCROW_PREIMAGE, str) else ESCROW_PREIMAGE
    cc = PreimageSha256(preimage=preimage_bytes)
    condition = cc.condition_binary.hex().upper()
    fulfillment = cc.serialize_binary().hex().upper()
    return condition, fulfillment


def get_ripple_client() -> AsyncJsonRpcClient:
    """Returns an instance of the XRPL client."""
    return AsyncJsonRpcClient(XRPL_NODE_URL)


async def send_premium(from_seed: str, to_address: str, amount_xrp: float) -> Dict[str, Union[str, float]]:
    """
    Sends a premium payment from a customer wallet to the platform wallet.

    Args:
        from_seed: Customer's XRPL seed.
        to_address: Destination XRPL address.
        amount_xrp: Premium amount in XRP.

    Returns:
        Dictionary with status and transaction hash.
    """
    client = get_ripple_client()
    wallet = get_wallet(from_seed)

    tx = Payment(
        account=wallet.classic_address,
        destination=to_address,
        amount=xrp_to_drops(amount_xrp)
    )

    print(f"[send_premium] Sending {amount_xrp} XRP from {wallet.classic_address} to {to_address}...")
    response = await submit_and_wait(tx, client, wallet)

    return {
        "status": "Premium sent",
        "tx_hash": response.result.get("hash")
    }
    
    
async def create_escrow_with_premium(
    customer_seed: str,
    platform_address: str,
    premium: float,
    payout: float,
    destination_address: str
) -> Dict[str, Union[int, str]]:
    """
    Processes the full insurance escrow setup:
    - Sends premium from customer to platform
    - Creates conditional escrow from platform to customer

    Args:
        customer_seed: Customer wallet seed.
        platform_address: Platform XRPL address receiving premium.
        premium: Premium amount in XRP.
        payout: Payout amount in XRP.
        destination_address: Insured customer destination address.

    Returns:
        Dictionary with escrow sequence, condition, fulfillment, and transaction hash.
    """
    client = get_ripple_client()

    # Customer pays premium to platform
    customer_wallet = get_wallet(customer_seed)
    premium_tx = Payment(
        account=customer_wallet.classic_address,
        destination=platform_address,
        amount=xrp_to_drops(premium)
    )
    print(f"[create_escrow_with_premium] Paying {premium} XRP from {customer_wallet.classic_address} to {platform_address}")
    await submit_and_wait(premium_tx, client, customer_wallet)

    # Platform creates conditional escrow
    platform_wallet = get_wallet(XRPL_SEED)
    condition, fulfillment = get_preimage_condition()

    finish_after = datetime_to_ripple_time(datetime.now() + timedelta(seconds=10))
    cancel_after = datetime_to_ripple_time(datetime.now() + timedelta(seconds=10))

    escrow_tx = EscrowCreate(
        account=platform_wallet.classic_address,
        destination=destination_address,
        amount=xrp_to_drops(payout),
        finish_after=finish_after,
        cancel_after=cancel_after,
        condition=condition
    )

    print(f"[create_escrow_with_premium] Creating payout escrow: {payout} XRP from {platform_wallet.classic_address} to {destination_address}")
    response = await submit_and_wait(escrow_tx, client, platform_wallet)
    sequence = response.result["tx_json"]["Sequence"]

    return {
        "sequence": sequence,
        "condition": condition,
        "fulfillment": fulfillment,
        "destination": destination_address,
        "tx_hash": response.result.get("hash")
    }

async def fulfill_escrow(sequence: int) -> Dict[str, str]:
    """
    Finishes a conditional escrow by submitting the fulfillment preimage.

    Args:
        sequence: Escrow sequence number.

    Returns:
        Dictionary with status and transaction hash.
    """
    client = get_ripple_client()
    wallet = get_wallet(XRPL_SEED)
    condition, fulfillment = get_preimage_condition()

    tx = EscrowFinish(
        account=wallet.classic_address,
        owner=wallet.classic_address,
        offer_sequence=sequence,
        condition=condition,
        fulfillment=fulfillment
    )

    print(f"[fulfill_escrow] Finishing escrow with sequence {sequence}...")
    response = await submit_and_wait(tx, client, wallet)

    return {
        "status": "Escrow fulfilled",
        "tx_hash": response.result.get("hash")
    }


async def cancel_escrow(sequence: int) -> Dict[str, str]:
    """
    Cancels an escrow that has expired or whose condition wasn't met.

    Args:
        sequence: Escrow sequence number.

    Returns:
        Dictionary with status and transaction hash.
    """
    client = get_ripple_client()
    wallet = get_wallet(XRPL_SEED)

    tx = EscrowCancel(
        account=wallet.classic_address,
        owner=wallet.classic_address,
        offer_sequence=sequence
    )

    print(f"[cancel_escrow] Canceling escrow with sequence {sequence}...")
    response = await submit_and_wait(tx, client, wallet)

    return {
        "status": "Escrow canceled",
        "tx_hash": response.result.get("hash")
    }