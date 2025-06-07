// src/App.js
import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ShipmentsListPage from "./pages/ShipmentsListPage";
import CreateEscrowPage from "./pages/CreateEscrowPage";
import ShipmentDashboard from "./ShipmentDashboard";
import "./App.css";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="app-container">
        <header className="topbar">
          <button className="menu-button" onClick={() => setSidebarOpen(!sidebarOpen)}>
            ☰
          </button>
          <h1 className="app-title">Shypto</h1>
        </header>

        <div className="main-layout">
          <nav className={`sidebar ${sidebarOpen ? "open" : ""}`}>
            <Link to="/create-escrow" onClick={() => setSidebarOpen(false)}>New Shipment</Link>
            <Link to="/" onClick={() => setSidebarOpen(false)}>My Shipments</Link>
            <Link to="/create-escrow" onClick={() => setSidebarOpen(false)}>My Account</Link>
          </nav>

          <main className="content">
            <Routes>
              <Route path="/create-escrow" element={<CreateEscrowPage />} />
              <Route path="/" element={<ShipmentsListPage />} />
              <Route path="/dashboard/:shipmentId" element={<ShipmentDashboard />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
