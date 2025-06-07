import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_DB = os.getenv("FIREBASE_DB")
XRPL_SEED = os.getenv("XRPL_SEED")
XRPL_NODE_URL = os.getenv("XRPL_NODE_URL", "https://s.altnet.rippletest.net:51234")
ESCROW_PREIMAGE = os.getenv("ESCROW_PREIMAGE", "shipment_damaged_123")  # or bytes
