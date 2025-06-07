from flask import Flask, request, jsonify
from flask_cors import CORS
from escrow_utils import create_escrow, fulfill_escrow
from firebase_client import (
    get_event_data,
    get_shipments_by_uid,
    get_shipment_data,
    get_latest_device_data,
    assign_shipment_to_user,
    update_claim_status,
    get_claim_status
)
import asyncio

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route("/")
def home():
    return jsonify({"status": "OK", "message": "XRPL insurance backend running"})


# Creates conditional escrow TODO: move to XRPL utility
@app.route("/create_escrow", methods=["POST"])
def create_escrow_route():
    data = request.get_json()
    destination = data.get("destination")
    amount = float(data.get("amount", 50))

    if not destination:
        return jsonify({"error": "Missing destination address"}), 400

    try:
        result = asyncio.run(create_escrow(destination, amount))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Fulfills conditional escrow TODO: move to XRPL utility
@app.route("/fulfill_escrow", methods=["POST"])
def fulfill_escrow_route():
    data = request.get_json()
    sequence = data.get("sequence")

    if sequence is None:
        return jsonify({"error": "Missing escrow sequence number"}), 400

    try:
        result = asyncio.run(fulfill_escrow(int(sequence)))
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
