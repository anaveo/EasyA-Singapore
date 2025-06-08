import React, { useEffect, useState } from "react";
import { auth } from "../firebase";

function AccountPage() {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const fetchInfo = async () => {
      const user = auth.currentUser;
      if (!user) return;

      const idToken = await user.getIdToken();

      const res = await fetch("http://localhost:5000/user_info", {
        headers: {
          Authorization: `Bearer ${idToken}`
        }
      });

      const data = await res.json();
      setUserData({
        email: user.email,
        ...data
      });
    };

    fetchInfo();
  }, []);


  const containerStyle = {
    padding: "2rem",
    maxWidth: "600px",
    margin: "auto",
  };

  const cardStyle = {
    backgroundColor: "#fff",
    padding: "2rem",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
  };

  const labelStyle = {
    fontWeight: "600",
    marginBottom: "6px",
    color: "#444",
  };

  const textStyle = {
    marginBottom: "1.2rem",
    fontSize: "1.05rem",
    color: "#333",
  };

  const walletStyle = {
    backgroundColor: "#f4f4ff",
    padding: "1.5rem",
    borderRadius: "12px",
    textAlign: "center",
    marginBottom: "1.5rem",
    boxShadow: "inset 0 0 0 2px #aaaad8",
  };

  const balanceStyle = {
    fontSize: "2rem",
    fontWeight: "bold",
    color: "#4c4cb8",
  };

  const buttonStyle = {
    backgroundColor: "#7f7fc7",
    color: "white",
    padding: "12px 24px",
    fontSize: "1rem",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    width: "100%",
    transition: "background 0.3s",
  };

  if (!userData) return <div>Loading account info...</div>;

  return (
    <div style={containerStyle}>
      <h1 style={{ fontSize: "2rem", textAlign: "center", marginBottom: "2rem" }}>
        Account
      </h1>

      <div style={cardStyle}>
        <div style={walletStyle}>
          <div style={{ fontSize: "1.2rem", marginBottom: "0.5rem" }}>Wallet Balance</div>
          <div style={balanceStyle}>{userData.balance_xrp.toFixed(2)} XRP</div>
        </div>

        <div style={textStyle}>
          <span style={labelStyle}>Email:</span> {userData.email}
        </div>
        <div style={textStyle}>
          <span style={labelStyle}>Wallet:</span> {userData.wallet_address}
        </div>

        <button
          style={buttonStyle}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#aaaad8")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#7f7fc7")}
          onClick={() => auth.signOut()}
        >
          Logout
        </button>
      </div>
    </div>
  );
}


export default AccountPage;
