from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import requests

from escrow_utils import create_escrow_with_premium, fulfill_escrow, cancel_escrow
from firebase_client import (
    get_event_data,
    get_shipments_by_uid,
    get_shipment_data,
    get_latest_device_data,
    assign_shipment_to_user,
    update_claim_status,
    get_claim_status,
    create_shipment,
    create_user_defaults
)

from firebase_admin import auth as firebase_auth

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route("/")
def home():
    return jsonify({"status": "OK", "message": "XRPL insurance backend running"})


# Token extraction helper
def get_user_from_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token["uid"]
    except Exception as e:
        print(f"[auth] Token verification failed: {e}")
        return None


from firebase_client import get_user_wallet

@app.route("/user_info", methods=["GET"])
def get_user_info():
    uid = get_user_from_token()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    wallet_address = get_user_wallet(uid)
    if not wallet_address:
        return jsonify({"error": "No wallet assigned to user"}), 404

    # Query XRPL for balance
    res = requests.post("https://s.altnet.rippletest.net:51234", json={
        "method": "account_info",
        "params": [{
            "account": wallet_address,
            "ledger_index": "validated",
            "strict": True
        }]
    })

    if res.status_code != 200 or "result" not in res.json():
        return jsonify({"error": "Failed to fetch XRPL data"}), 500

    drops = int(res.json()["result"]["account_data"]["Balance"])
    balance_xrp = drops / 1_000_000

    return jsonify({
        "uid": uid,
        "wallet_address": wallet_address,
        "balance_xrp": balance_xrp
    })


# Initialize defaults for new user
@app.route("/init_user_defaults", methods=["POST"])
def init_user_defaults_route():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        email = request.get_json().get("email")
        create_user_defaults(uid, email)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Auth or DB error: {e}")
        return jsonify({"error": str(e)}), 400


# Create escrow and premium transfer
@app.route("/create_escrow", methods=["POST"])
def create_conditional_escrow_route():
    data = request.get_json()
    uid = get_user_from_token()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    premium = float(data.get("premium", 2))
    payout = float(data.get("payout", 5))
    customer_seed = data.get("customer_seed")
    destination = data.get("destination")
    return_addr = data.get("return_address")
    condition = int(data.get("condition", 0))
    shipment_name = data.get("shipment_name")
    device_id = data.get("device_id")

    print("DEBUG input fields:", customer_seed, destination, return_addr, shipment_name, device_id)

    if not all([customer_seed, destination, return_addr, shipment_name, device_id]):
        return jsonify({
            "error": "Missing required fields",
            "debug": {
                "customer_seed": customer_seed,
                "destination": destination,
                "return_addr": return_addr,
                "shipment_name": shipment_name,
                "device_id": device_id
            }
        }), 400
        
    try:
        result = asyncio.run(create_escrow_with_premium(
            customer_seed=customer_seed,
            platform_address=return_addr,
            premium=premium,
            payout=payout,
            destination_address=destination
        ))

        shipment_id = create_shipment(
            owner_id=uid,
            name=shipment_name,
            device_id=device_id,
            premium=premium,
            payout=payout,
            condition=condition,
            sequence=result["sequence"]
        )

        return jsonify({
            "shipment_id": shipment_id,
            "escrow_tx": result,
            "status": "Shipment and escrow created"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Fulfill escrow
@app.route("/fulfill_escrow", methods=["POST"])
def fulfill_escrow_route():
    data = request.get_json()
    shipment_id = data.get("shipment_id")
    if not shipment_id:
        return jsonify({"error": "Missing shipment_id"}), 400

    shipment = get_shipment_data(shipment_id)
    sequence = shipment.get("escrow_sequence")
    if not sequence:
        return jsonify({"error": "No escrow sequence found for shipment"}), 400

    try:
        result = asyncio.run(fulfill_escrow(int(sequence)))
        update_claim_status(shipment_id, "approved")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Cancel escrow
@app.route("/cancel_escrow", methods=["POST"])
def cancel_escrow_route():
    data = request.get_json()
    shipment_id = data.get("shipment_id")
    reason = data.get("reason", "").lower()

    if not shipment_id:
        return jsonify({"error": "Missing shipment_id"}), 400

    shipment = get_shipment_data(shipment_id)
    sequence = shipment.get("escrow_sequence")
    if not sequence:
        return jsonify({"error": "No escrow sequence found for shipment"}), 400

    try:
        result = asyncio.run(cancel_escrow(int(sequence)))
        if "success" in reason:
            update_claim_status(shipment_id, "N/A")
        else:
            update_claim_status(shipment_id, "rejected")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get shipments for logged-in user
@app.route("/shipments")
def shipments_by_uid_route():
    uid = get_user_from_token()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    shipments = get_shipments_by_uid(uid)
    return jsonify(shipments)


# Get shipment details
@app.route("/shipment/<shipment_id>")
def shipment_data_route(shipment_id):
    data = get_shipment_data(shipment_id)
    return jsonify(data)


# Get sensor events
@app.route("/shipment/<shipment_id>/events")
def shipment_event_data_route(shipment_id):
    event_data = get_event_data(shipment_id)
    return jsonify(event_data)


# Assign shipment to current user
@app.route("/assign_shipment", methods=["POST"])
def assign_shipment():
    data = request.get_json()
    uid = get_user_from_token()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401

    shipment_id = data.get("shipment_id")
    if not shipment_id:
        return jsonify({"error": "Missing shipment_id"}), 400

    success = assign_shipment_to_user(uid, shipment_id)
    return jsonify({"success": success})


# Update claim status
@app.route("/update_claim", methods=["POST"])
def update_claim():
    data = request.get_json()
    shipment_id = data.get("shipment_id")
    status = data.get("status")

    if not shipment_id or not status:
        return jsonify({"error": "Missing shipment_id or status"}), 400

    success = update_claim_status(shipment_id, status)
    return jsonify({"success": success})


# Get claim status
@app.route("/claim_status/<shipment_id>")
def get_claim_status_route(shipment_id):
    status = get_claim_status(shipment_id)
    return jsonify({"shipment_id": shipment_id, "claim_status": status})
