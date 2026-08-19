import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!isAuthenticated) return null;

  return (
    <header className="navbar">
      <div className="nav-content">
        <Link to="/dashboard" className="brand">
          <span className="brand-icon">🥗</span>
          <span>PantryPilot</span>
        </Link>

        <nav className="nav-links">
          <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Dashboard
          </NavLink>
          <NavLink to="/pantry" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Pantry
          </NavLink>
          <NavLink to="/recipes" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Recipes
          </NavLink>
          <NavLink to="/shopping-list" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            Shopping List
          </NavLink>
          <NavLink to="/upload" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            📷 Scan Fridge
          </NavLink>
        </nav>

        <div className="nav-user">
          <div className="user-badge">
            <span>👤</span>
            <span>{user?.username || "Sameeksha"}</span>
          </div>
          <button onClick={handleLogout} className="btn btn-secondary btn-sm" title="Log out">
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
