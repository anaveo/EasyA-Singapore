import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from config import FIREBASE_DB
import random
import string

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DB
})

def generate_shipment_id():
    return "sid" + ''.join(random.choices(string.digits, k=8))

def get_event_data(shipment_id):
    if not shipment_id:
        print("Invalid input: Missing shipment ID")
        return False
    try:
        shipment = db.reference(f"/shipments/{shipment_id}").get()
        if not shipment:
            return {"error": "Shipment not found"}
        if "device_id" not in shipment:
            return {"error": "Device not in shipment"}

        return get_latest_device_data(shipment["device_id"])
    except Exception as e:
        print("Firebase error:", e)
        return {"error": str(e)}


def get_latest_device_data(device_id):
    if not device_id:
        print("Invalid input: Missing device ID")
        return False
    try:
        root_ref = db.reference(f"/device_data/{device_id}/latest_log")
        log_data = root_ref.get()
        if not log_data:
            return {"error": "No data found for this device"}

        events = log_data.get("events", {})
        location = log_data.get("location", {})
        timestamp = log_data.get("timestamp", {})

        return {
            "events": events,
            "location": location,
            "timestamp": timestamp
        }
    except Exception as e:
        print("Firebase error:", e)
        return {"error": str(e)}


def get_shipments_by_uid(uid):
    if not uid:
        print("Invalid input: Missing UID")
        return False
    try:
        ref = db.reference("/shipments")
        all_shipments = ref.get() or {}
        filtered = [
            {**v, "id": k} for k, v in all_shipments.items()
            if v.get("owner_id") == uid
        ]
        return filtered
    except Exception as e:
        print("Firebase error:", e)
        return []


def get_shipment_data(shipment_id):
    if not shipment_id:
        print("Invalid input: Missing shipment ID")
        return False
    try:
        ref = db.reference(f"/shipments/{shipment_id}")
        data = ref.get()
        return data if data else {}
    except Exception as e:
        print("Firebase error:", e)
        return {}


def assign_shipment_to_user(uid, shipment_id):
    if not uid or not shipment_id:
        print("Invalid input: Missing UID or shipment ID")
        return False
    try:
        ref = db.reference(f"/shipments/{shipment_id}")
        ref.update({"owner_id": uid})
        return True
    except Exception as e:
        print("Firebase error (assign_shipment):", e)
        return False


def update_claim_status(shipment_id, status):
    VALID_STATUSES = {"approved", "rejected", "pending", "N/A"}

    if status not in VALID_STATUSES:
        print(f"Invalid claim status: {status}")
        return False

    try:
        ref = db.reference(f"/shipments/{shipment_id}")
        ref.update({"claim_status": status})
        return True
    except Exception as e:
        print("Firebase error (update_claim):", e)
        return False

# TODO: Restrict by UID
def get_claim_status(shipment_id):
    if not shipment_id:
        print("Invalid input: Missing shipment ID")
        return False
    try:
        ref = db.reference(f"/shipments/{shipment_id}/claim_status")
        status = ref.get()
        return status if status is not None else "unknown"
    except Exception as e:
        print("Firebase error:", e)
        return {}
    
def store_escrow_metadata(shipment_id, data: dict):
    if not shipment_id:
        print("Invalid input: Missing shipment ID")
        return False
    
    ref = db.reference(f"shipments/{shipment_id}")
    try:
        ref.update(data)
        return True
    except Exception as e:
        print("Firebase error (store_escrow_metadata):", e)
        return False


def create_shipment(owner_id, name, device_id, premium, payout, condition, sequence):
    ref = db.reference("/shipments")
    shipment_id = generate_shipment_id()
    data = {
        "owner_id": owner_id,
        "shipment_name": name,
        "device_id": device_id,
        "premium": premium,
        "payout": payout,
        "condition": condition,
        "escrow_sequence": sequence,
        "claim_status": "N/A"
    }
    ref.child(shipment_id).set(data)
    return shipment_id


def create_user_defaults(uid, email):
    try:
        ref = db.reference(f"/users/{uid}")
        ref.set({
            "email": email,
            "owned_devices": {},
            "created_at": datetime.utcnow().isoformat()
        })
        return True
    except Exception as e:
        print("Firebase error (create_user_defaults):", e)
        return False
