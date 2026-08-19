import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Login = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || "/dashboard";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!usernameOrEmail || !password) {
      setError("Please enter your username/email and password.");
      return;
    }

    const result = await login(usernameOrEmail, password);
    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="card auth-card">
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <span style={{ fontSize: "2.5rem" }}>🥗</span>
          <h2 style={{ fontSize: "1.5rem", fontWeight: "700", marginTop: "0.5rem" }}>Welcome back to PantryPilot</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Sign in to access your kitchen pantry & smart recipes.
          </p>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username or Email</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. john_doe or john@example.com"
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary btn-lg" style={{ width: "100%", marginTop: "1rem" }} disabled={loading}>
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>

        <div style={{ textAlign: "center", marginTop: "1.5rem", fontSize: "0.9rem", color: "var(--text-muted)" }}>
          Don't have an account?{" "}
          <Link to="/register" style={{ color: "var(--primary-dark)", fontWeight: "600" }}>
            Create one
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
