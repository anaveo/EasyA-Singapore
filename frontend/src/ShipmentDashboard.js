// src/ShipmentDashboard.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

function ShipmentDashboard() {
  const { shipmentId } = useParams();
  const [data, setData] = useState(null);
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(false);

  const apiBase = process.env.REACT_APP_API || "http://localhost:5000";

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${apiBase}/shipment/${shipmentId}`);
        setData(res.data);
      } catch (err) {
        console.error("Error loading shipment data", err);
        setData(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [shipmentId]);

  const triggerClaim = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${apiBase}/evaluate/${shipmentId}`);
      setClaim(res.data);
    } catch (err) {
      console.error("Claim error", err);
      setClaim({ error: "Claim failed" });
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>📦 Shipment: {shipmentId}</h2>
      <button onClick={triggerClaim} disabled={loading}>
        Evaluate Claim
      </button>

      {data && (
        <div style={{ marginTop: "1rem" }}>
          <h4>Sensor Data</h4>
          <pre>{JSON.stringify(data.shock_values, null, 2)}</pre>
        </div>
      )}

      {claim && (
        <div style={{ marginTop: "1rem" }}>
          <h4>Claim Result</h4>
          <pre>{JSON.stringify(claim, null, 2)}</pre>
          {claim.tx_hash && (
            <a
              href={`https://testnet.xrpl.org/transactions/${claim.tx_hash}`}
              target="_blank"
              rel="noreferrer"
            >
              View on XRPL ↗
            </a>
          )}
        </div>
      )}
    </div>
  );
}

export default ShipmentDashboard;
