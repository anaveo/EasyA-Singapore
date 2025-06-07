import React, { useState } from "react";
import axios from "axios";

function ShipmentDashboard() {
  const [shipmentId, setShipmentId] = useState("");
  const [data, setData] = useState(null);
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(false);

  const apiBase = process.env.REACT_APP_API || "http://localhost:5000";

  const fetchShipment = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${apiBase}/shipment/${shipmentId}`);
      setData(res.data);
    } catch (err) {
      console.error("Error fetching shipment", err);
    }
    setLoading(false);
  };

  const triggerClaim = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${apiBase}/evaluate/${shipmentId}`);
      setClaim(res.data);
    } catch (err) {
      console.error("Claim error", err);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h2>📦 Shipment Dashboard</h2>
      <input
        placeholder="Enter Shipment ID"
        value={shipmentId}
        onChange={(e) => setShipmentId(e.target.value)}
      />
      <button onClick={fetchShipment} disabled={!shipmentId || loading}>Load Data</button>
      <button onClick={triggerClaim} disabled={!shipmentId || loading}>Evaluate Claim</button>

      {data && (
        <div style={{ marginTop: "1rem" }}>
          <h4>Shock Values</h4>
          <pre>{JSON.stringify(data.shock_values, null, 2)}</pre>
        </div>
      )}

      {claim && (
        <div style={{ marginTop: "1rem" }}>
          <h4>Claim Result</h4>
          <pre>{JSON.stringify(claim, null, 2)}</pre>
          {claim.tx_hash && (
            <a href={`https://testnet.xrpl.org/transactions/${claim.tx_hash}`} target="_blank" rel="noreferrer">
              View on XRPL ↗
            </a>
          )}
        </div>
      )}
    </div>
  );
}

export default ShipmentDashboard;
