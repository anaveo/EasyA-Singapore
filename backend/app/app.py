from flask import Flask, request, jsonify
from flask_cors import CORS
from escrow_utils import create_escrow_with_premium, fulfill_escrow, cancel_escrow
from firebase_client import (
    get_event_data,
    get_shipments_by_uid,
    get_shipment_data,
    get_latest_device_data,
    assign_shipment_to_user,
    update_claim_status,
    get_claim_status,
    create_shipment
)
import asyncio

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route("/")
def home():
    return jsonify({"status": "OK", "message": "XRPL insurance backend running"})


# Creates conditional escrow TODO: move to XRPL utility
from firebase_client import create_shipment
from escrow_utils import create_escrow_with_premium  # replace old import

@app.route("/create_escrow", methods=["POST"])
def create_conditional_escrow_route():
    data = request.get_json()
    premium = float(data.get("premium", 2))
    payout = float(data.get("payout", 5))
    customer_seed = data.get("customer_seed")
    destination = data.get("destination")
    return_addr = data.get("return_address")
    condition = int(data.get("condition", 0))  # integer from 0 to 5
    shipment_name = data.get("shipment_name")
    device_id = data.get("device_id")
    owner_id = data.get("owner_id")

    if not all([customer_seed, destination, return_addr, shipment_name, device_id, owner_id]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = asyncio.run(create_escrow_with_premium(
            customer_seed=customer_seed,
            platform_address=return_addr,
            premium=premium,
            payout=payout,
            destination_address=destination
        ))

        shipment_id = create_shipment(
            owner_id=owner_id,
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


# Fulfills conditional escrow TODO: move to XRPL utility
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


# Cancels conditional escrow
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

        # Set claim status based on reason
        if "success" in reason:
            update_claim_status(shipment_id, "N/A")
        else:
            update_claim_status(shipment_id, "rejected")

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Returns shipments belonging to owner
@app.route("/shipments")
def shipments_by_uid_route():
    uid = request.args.get("owner_id")
    if not uid:
        return jsonify({"error": "Missing owner_id"}), 400

    shipments = get_shipments_by_uid(uid)
    return jsonify(shipments)


# Returns the shipments parameters
@app.route("/shipment/<shipment_id>")
def shipment_data_route(shipment_id):
    data = get_shipment_data(shipment_id)
    return jsonify(data)


# Returns the events associated with a shipment
@app.route("/shipment/<shipment_id>/events")
def shipment_event_data_route(shipment_id):
    event_data = get_event_data(shipment_id)
    return jsonify(event_data)


# Links a shipment to a user
@app.route("/assign_shipment", methods=["POST"])
def assign_shipment():
    data = request.get_json()
    uid = data.get("owner_id")
    shipment_id = data.get("shipment_id")

    if not uid or not shipment_id:
        return jsonify({"error": "Missing owner_id or shipment_id"}), 400

    success = assign_shipment_to_user(uid, shipment_id)
    return jsonify({"success": success})


# Updates a shipment's claim status
@app.route("/update_claim", methods=["POST"])
def update_claim():
    data = request.get_json()
    shipment_id = data.get("shipment_id")
    status = data.get("status")

    if not shipment_id or not status:
        return jsonify({"error": "Missing shipment_id or status"}), 400

    success = update_claim_status(shipment_id, status)
    return jsonify({"success": success})


# Returns a shipment's claim status
@app.route("/claim_status/<shipment_id>")
def get_claim_status_route(shipment_id):
    status = get_claim_status(shipment_id)
    return jsonify({"shipment_id": shipment_id, "claim_status": status})
