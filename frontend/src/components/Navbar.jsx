import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import api from "../services/api";

const Navbar = () => {
  const { user, token, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  const socketRef = useRef(null);

  // 1. Initial REST fetch for notification history
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
    }
  }, [isAuthenticated]);

  // 2. Real-Time Authenticated WebSocket Connection (Replaces wasteful HTTP Polling!)
  useEffect(() => {
    if (!isAuthenticated || !token) return;

    const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
    const wsProtocol = baseUrl.startsWith("https:") ? "wss:" : "ws:";
    const host = baseUrl.replace(/^https?:\/\//, "");
    const wsUrl = `${wsProtocol}//${host}/ws/notifications?token=${encodeURIComponent(token)}`;
    console.log("[WEBSOCKET CLIENT] Connecting to live notification stream...", wsUrl);

    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log("[WEBSOCKET CLIENT] Live WebSocket Connection Established! ⚡");
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("[WEBSOCKET CLIENT] Real-Time Event Received:", data);

        if (data.type === "expiry_notification") {
          const newNotif = {
            id: Date.now(),
            message: data.message,
            notification_type: data.notification_type || "warning",
            is_read: false,
            created_at: new Date().toISOString(),
          };
          setNotifications((prev) => [newNotif, ...prev]);
          setUnreadCount((prev) => prev + 1);
        }
      } catch (err) {
        console.error("[WEBSOCKET PARSE ERROR]", err);
      }
    };

    ws.onerror = (err) => {
      console.error("[WEBSOCKET CLIENT ERROR]", err);
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log("[WEBSOCKET CLIENT] Socket Closed.");
      setWsConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [isAuthenticated, token]);

  const fetchNotifications = async () => {
    try {
      const [listRes, countRes] = await Promise.all([
        api.get("/notifications"),
        api.get("/notifications/unread-count"),
      ]);
      setNotifications(listRes.data);
      setUnreadCount(countRes.data.unread_count);
    } catch (err) {
      console.error("Failed to fetch notification history", err);
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
          <NavLink to="/agent" data-magnetic className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            🤖 AI Agent
          </NavLink>
          <NavLink to="/upload" data-magnetic className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            📷 Scan Fridge
          </NavLink>
        </nav>

        <div className="nav-user">
          {/* Real-Time WebSocket Expiry Notifications Bell */}
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              data-magnetic
              className="theme-toggle-btn"
              title={wsConnected ? "Real-time WebSocket connected ⚡" : "Connecting..."}
              style={{ position: "relative" }}
            >
              <span>🔔</span>
              {wsConnected && (
                <span
                  style={{
                    width: "8px",
                    height: "8px",
                    backgroundColor: "var(--primary)",
                    borderRadius: "50%",
                    display: "inline-block",
                    marginLeft: "2px",
                  }}
                  title="Live WebSocket Connected"
                />
              )}
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
                  width: "330px",
                  maxHeight: "380px",
                  overflowY: "auto",
                  zIndex: 200,
                  padding: "1rem",
                  boxShadow: "var(--shadow-lg)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                    <strong style={{ fontSize: "0.95rem" }}>Expiry Notifications</strong>
                    {wsConnected && <span className="badge badge-green" style={{ fontSize: "0.65rem" }}>⚡ Live</span>}
                  </div>

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
                    {notifications.map((n, idx) => (
                      <div
                        key={n.id || idx}
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
