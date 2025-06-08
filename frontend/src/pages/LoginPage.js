import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();

      await fetch("http://localhost:5000/init_user_defaults", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({ email }),
      });

      navigate("/", { replace: true });
    } catch (err) {
      setError("Registration failed. Email may already be in use.");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await signInWithEmailAndPassword(auth, email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError("Invalid credentials. Please try again.");
    }
  };

  const containerStyle = {
    padding: "2rem",
    maxWidth: "500px",
    margin: "auto",
  };

  const cardStyle = {
    backgroundColor: "#fff",
    padding: "2rem",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
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
    marginTop: "0.5rem",
  };

  const errorStyle = {
    color: "red",
    marginBottom: "1rem",
    textAlign: "center",
  };

  return (
    <div style={containerStyle}>
      <h1 style={{ fontSize: "2rem", textAlign: "center", marginBottom: "2rem" }}>Login</h1>

      <form style={cardStyle} onSubmit={handleLogin}>
        {error && <div style={errorStyle}>{error}</div>}

        <label style={{ fontWeight: "600" }}>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={inputStyle}
          required
          onFocus={(e) => (e.target.style.border = "1px solid #aaaad8")}
          onBlur={(e) => (e.target.style.border = "1px solid #7f7fc7")}
        />

        <label style={{ fontWeight: "600" }}>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
          required
          onFocus={(e) => (e.target.style.border = "1px solid #aaaad8")}
          onBlur={(e) => (e.target.style.border = "1px solid #7f7fc7")}
        />

        <button
          type="submit"
          style={buttonStyle}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#aaaad8")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#7f7fc7")}
        >
          Sign In
        </button>

        <button
          type="button"
          onClick={handleRegister}
          style={buttonStyle}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#aaaad8")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#7f7fc7")}
        >
          Register
        </button>
      </form>
    </div>
  );
}

export default LoginPage;
