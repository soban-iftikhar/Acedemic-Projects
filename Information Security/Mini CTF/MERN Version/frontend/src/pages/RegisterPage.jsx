import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const { register } = useAuth();
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      const data = await register(form);
      setMessage(data.message || "Registered");
      setTimeout(() => navigate("/login"), 900);
    } catch (err) {
      setError(err?.response?.data?.message || "Registration failed");
    }
  }

  return (
    <div className="auth-wrap">
      <form className="card" onSubmit={onSubmit}>
        <h1>Register</h1>
        <input placeholder="Username" value={form.username} onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))} />
        <input placeholder="Email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} />
        {error && <p className="error">{error}</p>}
        {message && <p className="success">{message}</p>}
        <button type="submit">Create Account</button>
        <p>
          Already have account? <Link to="/login">Go to login</Link>
        </p>
      </form>
    </div>
  );
}
