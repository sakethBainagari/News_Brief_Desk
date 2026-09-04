import React, { useState } from "react";
import { login } from "../api/auth";

const DEMO_ACCOUNTS = [
  { role: "REPORTER", name: "Saketh", email: "saketh@example.com", pass: "Reporter#123", desc: "Reviews clusters, edits draft briefs, submits for review. Cannot publish." },
  { role: "EDITOR", name: "Rahul", email: "rahul@example.com", pass: "Editor#123", desc: "Rewrites briefs, approves, publishes stories, merges duplicate clusters." },
  { role: "DESK_HEAD", name: "Priya", email: "priya@example.com", pass: "DeskHead#123", desc: "Monitors published story output, subject trends, and time-to-publication." }
];

export default function LoginModal({ onLoginSuccess }) {
  const [email, setEmail] = useState("saketh@example.com");
  const [password, setPassword] = useState("Reporter#123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      onLoginSuccess();
    } catch (err) {
      setError(err.message || "Invalid credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDemo = (acc) => {
    setEmail(acc.email);
    setPassword(acc.pass);
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <h1>NEWS BRIEF DESK</h1>
          <p>AI-Assisted Newsroom Event Grouping & Editorial System</p>
        </div>

        <h3>Select a Demo Newsroom Account:</h3>
        <div className="demo-accounts-grid">
          {DEMO_ACCOUNTS.map((acc) => (
            <div
              key={acc.role}
              className={`demo-account-card ${email === acc.email ? "selected" : ""}`}
              onClick={() => handleSelectDemo(acc)}
            >
              <div className="account-header">
                <strong>{acc.name}</strong>
                <span className={`role-badge role-${acc.role.toLowerCase()}`}>{acc.role}</span>
              </div>
              <p className="account-desc">{acc.desc}</p>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-alert">{error}</div>}

          <div className="form-group">
            <label>Email Address:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? "Authenticating..." : "Log In to News Desk"}
          </button>
        </form>
      </div>
    </div>
  );
}
