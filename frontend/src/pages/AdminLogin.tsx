import { LogIn } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, adminApi } from "../api/client";
import Logo from "../components/Logo";

export default function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await adminApi.login(email, password);
      navigate("/admin");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="admin-login">
      <form className="login-card" onSubmit={submit}>
        <Logo />
        <h1>Admin login</h1>
        {error && <div className="form-alert error">{error}</div>}
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required />
        </label>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          <LogIn size={18} aria-hidden="true" />
          {loading ? "Signing in..." : "Sign In"}
        </button>
      </form>
    </main>
  );
}
