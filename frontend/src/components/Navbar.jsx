import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import api from "../services/api";

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
      // Poll notifications every 30 seconds
      const interval = setInterval(fetchNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const fetchNotifications = async () => {
    try {
      const [listRes, countRes] = await Promise.all([
        api.get("/notifications"),
        api.get("/notifications/unread-count"),
      ]);
      setNotifications(listRes.data);
      setUnreadCount(countRes.data.unread_count);
    } catch (err) {
      console.error("Failed to fetch notifications", err);
    }
  };

  const handleMarkAsRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error("Failed to mark notification as read", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.post("/notifications/read-all");
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error("Failed to mark all as read", err);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!isAuthenticated) return null;

  const themeIcon = theme === "dark" ? "🌙 Dark" : theme === "light" ? "☀️ Light" : "🌿 Emerald";

  return (
    <header className="navbar">
      <div className="nav-content">
        <Link to="/dashboard" className="brand" data-magnetic>
          <span className="brand-icon">🥗</span>
          <span>PantryPilot</span>
        </Link>

        <nav className="nav-links">
          <NavLink to="/dashboard" data-magnetic className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Dashboard
          </NavLink>
          <NavLink to="/pantry" data-magnetic className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Pantry
          </NavLink>
          <NavLink to="/recipes" data-magnetic className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Recipes
          </NavLink>
          <NavLink to="/shopping-list" data-magnetic className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Shopping List
          </NavLink>
          <NavLink to="/upload" data-magnetic className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            📷 Scan Fridge
          </NavLink>
        </nav>

        <div className="nav-user">
          {/* Expiry Notifications Bell Dropdown */}
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              data-magnetic
              className="theme-toggle-btn"
              title="Expiry Notifications"
              style={{ position: "relative" }}
            >
              <span>🔔</span>
              {unreadCount > 0 && (
                <span
                  style={{
                    backgroundColor: "var(--danger)",
                    color: "white",
                    fontSize: "0.7rem",
                    fontWeight: "bold",
                    borderRadius: "9999px",
                    padding: "0.15rem 0.4rem",
                    lineHeight: 1,
                  }}
                >
                  {unreadCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <div
                className="card"
                style={{
                  position: "absolute",
                  right: 0,
                  top: "120%",
                  width: "320px",
                  maxHeight: "380px",
                  overflowY: "auto",
                  zIndex: 200,
                  padding: "1rem",
                  boxShadow: "var(--shadow-lg)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <strong style={{ fontSize: "0.95rem" }}>Expiry Notifications 🔔</strong>
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllRead}
                      style={{ background: "none", border: "none", color: "var(--primary-dark)", fontSize: "0.75rem", cursor: "pointer", fontWeight: "600" }}
                    >
                      Mark all read
                    </button>
                  )}
                </div>

                {notifications.length === 0 ? (
                  <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", textAlign: "center", padding: "1rem 0" }}>
                    No expiry notifications right now.
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {notifications.map((n) => (
                      <div
                        key={n.id}
                        onClick={() => !n.is_read && handleMarkAsRead(n.id)}
                        style={{
                          padding: "0.6rem",
                          borderRadius: "var(--radius-md)",
                          backgroundColor: n.is_read ? "var(--bg-main)" : "var(--primary-light)",
                          borderLeft: n.notification_type === "critical" ? "3px solid var(--danger)" : n.notification_type === "urgent" ? "3px solid var(--warning)" : "3px solid var(--primary)",
                          fontSize: "0.85rem",
                          cursor: n.is_read ? "default" : "pointer",
                          opacity: n.is_read ? 0.7 : 1,
                        }}
                      >
                        <div>{n.message}</div>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
                          {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Theme Switcher Button */}
          <button
            onClick={toggleTheme}
            data-magnetic
            className="theme-toggle-btn"
            title="Toggle theme (Dark / Light / Emerald)"
          >
            <span>{themeIcon}</span>
          </button>

          <div className="user-badge" data-magnetic>
            <span>👤</span>
            <span>{user?.username || "Sameeksha"}</span>
          </div>

          <button onClick={handleLogout} data-magnetic className="btn btn-secondary btn-sm" title="Log out">
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
