import React, { useEffect, useState } from "react";
import axios from "axios";
import { LinearProgress, Box, Typography } from "@mui/material";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { useParams } from "react-router-dom";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// Fix for missing default marker icons
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});


function ShipmentDashboardPage() {
  const { shipmentId } = useParams();
  const [eventData, setEventData] = useState(null);
  const [claimStatus, setClaimStatus] = useState("Not Found");
  const apiBase = process.env.REACT_APP_API || "http://localhost:5000";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [eventRes, shipmentRes] = await Promise.all([
          axios.get(`${apiBase}/shipment/${shipmentId}/events`),     // Sensor events
          axios.get(`${apiBase}/shipment/${shipmentId}`),            // Metadata
        ]);

        setEventData({
          ...eventRes.data,
          shipment_name: shipmentRes.data.shipment_name || shipmentId,
          claim_status: shipmentRes.data.claim_status || "N/A",
        });

      } catch (err) {
        console.error("Error fetching dashboard data:", err);
      }
    };

    if (shipmentId) {
      fetchData();
    }
  }, [shipmentId]);


  if (!eventData) return <div>Loading dashboard...</div>;

  const {
    events: { temp = 0, hum = 0, shock = 0 } = {},
    location: { lat = 0, lng = 0 } = {},
    timestamp
  } = eventData;

  const formattedTime = timestamp
    ? new Date(timestamp * 1000).toLocaleString()
    : "Unknown";

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h2 style={{ fontWeight: 600, marginBottom: "1rem" }}>
        Shipment: {eventData.shipment_name}
      </h2>

      <div style={{ marginBottom: "2rem", borderRadius: "10px", overflow: "hidden", boxShadow: "0 2px 10px rgba(0,0,0,0.15)" }}>
        <MapContainer center={[lat, lng]} zoom={16} style={{ height: "400px", width: "100%" }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://carto.com/">CARTO</a> | Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
          />
          <Marker position={[lat, lng]}>
            <Popup>Shipment {shipmentId}<br />Current location</Popup>
          </Marker>
        </MapContainer>
      </div>

      <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
        {/* Gauges */}
        <div style={{ flex: "2", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <ProgressCard label="Shock" value={shock} max={4} />
          <ProgressCard label="Overtemperature" value={temp} max={4} />
          <ProgressCard label="Water Damage" value={hum} max={4} />
        </div>

        {/* Claim status and last update time */}
<div style={{ padding: "1.5rem 2rem", background: "#fff", borderRadius: "10px", boxShadow: "0 2px 6px rgba(0,0,0,0.1)", flexGrow: 1, marginLeft: "1rem" }}>
  <h3 style={{ marginBottom: "1rem" }}>Claim Status</h3>
  <p style={{
    fontSize: "1.5rem",
    fontWeight: 600,
    color: eventData.claim_status === "approved" ? "#28a745" :
           claimStatus === "rejected" ? "#dc3545" : "#ffc107"
  }}>
    {eventData.claim_status.toUpperCase()}
  </p>

  {/* Last updated time */}
  <div style={{
    marginTop: "1rem",
    padding: "8px 12px",
    background: "#f1f3f4",
    borderRadius: "6px",
    fontSize: "0.9rem",
    color: "#333"
  }}>
    <strong>Last updated:</strong><br />
    {timestamp ? new Date(timestamp * 1000).toLocaleString() : "Unknown"}
  </div>
</div>

      </div>
    </div>
  );
}

// Horizontal gradient bar component
function ProgressCard({ label, value, max }) {
  const percent = Math.min((value / max) * 100, 100);

  return (
    <Box
      sx={{
        background: "#fff",
        borderRadius: "10px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
        padding: "1rem",
        marginBottom: "1rem",
        width: "100%"
      }}
    >
      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
        {label}
      </Typography>
      <Box sx={{ position: "relative", height: 10, borderRadius: 5, background: "#e0e0e0" }}>
        <Box
          sx={{
            position: "absolute",
            height: "100%",
            width: `${percent}%`,
            borderRadius: 5,
            background: `linear-gradient(to right, #8400ff, red)`
          }}
        />
      </Box>
      <Typography variant="body2" mt={1}>
        {value} {label === "Temperature" ? "°C" : label === "Humidity" ? "%" : ""}
      </Typography>
    </Box>
  );
}


export default ShipmentDashboardPage;
