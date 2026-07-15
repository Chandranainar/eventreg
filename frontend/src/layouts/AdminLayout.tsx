import { CalendarCog, FileUp, LayoutDashboard, LogOut } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { adminApi } from "../api/client";
import Logo from "../components/Logo";
import type { AdminUser } from "../types";

export default function AdminLayout() {
  const navigate = useNavigate();
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi
      .me()
      .then(setUser)
      .catch(() => navigate("/admin/login", { replace: true }))
      .finally(() => setLoading(false));
  }, [navigate]);

  async function logout() {
    await adminApi.logout().catch(() => undefined);
    navigate("/admin/login", { replace: true });
  }

  if (loading) return <main className="center-state">Checking session...</main>;
  if (!user) return null;

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <Logo />
        <nav aria-label="Admin navigation">
          <NavLink to="/admin" end>
            <LayoutDashboard size={18} aria-hidden="true" />
            Dashboard
          </NavLink>
          <NavLink to="/admin/event">
            <CalendarCog size={18} aria-hidden="true" />
            Event
          </NavLink>
          <NavLink to="/admin/import">
            <FileUp size={18} aria-hidden="true" />
            Import
          </NavLink>
        </nav>
        <button className="btn btn-secondary" type="button" onClick={logout}>
          <LogOut size={18} aria-hidden="true" />
          Logout
        </button>
      </aside>
      <main className="admin-main">
        <div className="admin-topbar">
          <div>
            <span>Signed in as</span>
            <strong>{user.name}</strong>
          </div>
        </div>
        <Outlet />
      </main>
    </div>
  );
}
