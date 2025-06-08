import React, { useState } from "react";
import { auth } from "../firebase";
import { useNavigate } from "react-router-dom";

function CreateEscrowPage() {
  const [shipment, setShipment] = useState({
    shipmentName: "",
    deviceId: "SQT-2808",
    premium: "",
    payout: "",
    condition: "",
    escrowSeq: "",
    claimStatus: "N/A",
  });

  const navigate = useNavigate();


  const handleChange = (e) => {
    setShipment({ ...shipment, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const user = auth.currentUser;

    if (!user) {
      alert("You must be logged in.");
      return;
    }

    const idToken = await user.getIdToken();

    const payload = {
      premium: parseFloat(shipment.premium),
      payout: parseFloat(shipment.payout),
      customer_seed: "sEdTR3zoMojyWirT4bB6D9FN1LbHKfh", // replace during dev
      destination: "rJ76R7wNbZL9T1obJcovyiDMh7fZuWV3wz",
      return_address: "rwEBoKh6i9DCAMQfFQhyrHCz9uxoYCgfdg",
      condition: parseInt(shipment.condition, 10),
      shipment_name: shipment.shipmentName,
      device_id: shipment.deviceId
    };
  console.log("Final Payload:", JSON.stringify(payload, null, 2));

    try {
      const apiBase = process.env.REACT_APP_API || "http://localhost:5000";
      const res = await fetch(`${apiBase}/create_escrow`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      if (!res.ok) throw new Error(result.error || "Unknown error");

      alert("Shipment created successfully!");
      navigate("/");
    } catch (err) {
      console.error("Creation failed:", err);
      alert("Error: " + err.message);
    }
  };

  const inputStyle = {
    width: "100%",
    padding: "12px",
    marginTop: "6px",
    marginBottom: "16px",
    border: "1px solid #ccc",
    borderRadius: "8px",
    fontSize: "1rem",
    transition: "border 0.3s",
  };

  const labelStyle = {
    fontWeight: "600",
    display: "block",
    marginBottom: "4px",
  };

  const formStyle = {
    backgroundColor: "#fff",
    padding: "2rem",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "1.5rem", textAlign: "center" }}>
        Create Shipment
      </h1>
      <form onSubmit={handleSubmit} style={formStyle}>
        {[
          { label: "Shipment Name", name: "shipmentName", type: "text" },
          { label: "Premium", name: "premium", type: "number", step: "0.01" },
          { label: "Payout", name: "payout", type: "number", step: "0.01" },
          { label: "Allowed Condition #", name: "condition", type: "number", step: "1" }
        ].map(({ label, name, type, step }) => (
          <div key={name}>
            <label style={labelStyle}>{label}</label>
            <input
              type={type}
              name={name}
              value={shipment[name]}
              onChange={handleChange}
              required
              step={step}
              style={inputStyle}
              onFocus={(e) => (e.target.style.border = "1px solid #aaaad8")}
              onBlur={(e) => (e.target.style.border = "1px solid #7f7fc7")}
            />
          </div>
        ))}
        <button
          type="submit"
          style={{
            backgroundColor: "#7f7fc7",
            color: "white",
            padding: "12px 24px",
            fontSize: "1rem",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            width: "100%",
            transition: "background 0.3s",
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#aaaad8")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#7f7fc7")}
        >
          Create Shipment
        </button>
      </form>
    </div>
  );
}

export default CreateEscrowPage;
