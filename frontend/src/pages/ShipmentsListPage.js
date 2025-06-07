// src/pages/ShipmentsListPage.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function ShipmentsListPage() {
  const [shipments, setShipments] = useState([]);
  const uid = "uid1"; // Hardcoded for now
  const apiBase = process.env.REACT_APP_API || "http://localhost:5000";
  const navigate = useNavigate();

  useEffect(() => {
    const fetchShipments = async () => {
      try {
        const res = await axios.get(`${apiBase}/shipments?owner_id=${uid}`);
        const data = res.data;
        console.log("shipment")

        // Convert { id1: {...}, id2: {...} } → [{ id: id1, ... }, ...]
        const shipmentList = Object.entries(data || {}).map(([id, val]) => ({
          id,
          ...val,
        }));

        setShipments(shipmentList);
        console.log("Fetched shipments:", res.data);
      } catch (err) {
        console.error("Error fetching shipments:", err);
      }
    };

    fetchShipments();
  }, [uid]);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Alice's Shipments</h1>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
        {shipments.length === 0 ? (
          <p>No shipments found.</p>
        ) : (
        shipments.map((shipment) => (
          <div
            key={shipment.id}
            style={{
              border: "2px rgba(255, 47, 0, 0.73)",
              borderRadius: "8px",
              padding: "1rem",
              backgroundColor: "#fff",
              width: "250px",
              boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
              cursor: "pointer",
            }}
            onClick={() => navigate(`/dashboard/${shipment.id}`)}
          >
            <h3>{shipment.id}</h3>
            <p><strong>Device:</strong> {shipment.device_id}</p>
            <p><strong>Claim:</strong> {shipment.claim_status}</p>
            <p><strong>Escrow Seq:</strong> {shipment.escrow_sequence || "N/A"}</p>
          </div>
        )))}
      </div>
    </div>
  );
}

export default ShipmentsListPage;

// 1234
