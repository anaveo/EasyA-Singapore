import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import ShipmentsListPage from "./pages/ShipmentsListPage";
import CreateEscrowPage from "./pages/CreateEscrowPage";
import ShipmentDashboard from "./ShipmentDashboard";
import LoginPage from "./pages/LoginPage";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./firebase";
import "./App.css";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  if (loading) return <div>Loading...</div>;

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
          {user && (
            <nav className={`sidebar ${sidebarOpen ? "open" : ""}`}>
              <Link to="/create-escrow" onClick={() => setSidebarOpen(false)}>New Shipment</Link>
              <Link to="/" onClick={() => setSidebarOpen(false)}>My Shipments</Link>
              <Link to="/create-escrow" onClick={() => setSidebarOpen(false)}>My Account</Link>
            </nav>
          )}

          <main className="content">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              {user ? (
                <>
                  <Route path="/create-escrow" element={<CreateEscrowPage />} />
                  <Route path="/" element={<ShipmentsListPage />} />
                  <Route path="/dashboard/:shipmentId" element={<ShipmentDashboard />} />
                </>
              ) : (
                <Route path="*" element={<Navigate to="/login" />} />
              )}
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
