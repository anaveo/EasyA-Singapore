from flask import Flask, request, jsonify
from escrow_utils import create_escrow, fulfill_escrow
import asyncio

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "OK", "message": "XRPL insurance backend running"})


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
