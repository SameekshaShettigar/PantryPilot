import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import IngredientChip from "../components/IngredientChip";
import RecipeCard from "../components/RecipeCard";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

const Dashboard = () => {
  const { user } = useAuth();
  const [pantryItems, setPantryItems] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [pantryRes, recsRes] = await Promise.all([
        api.get("/pantry"),
        api.post("/recipes/recommend"),
      ]);

      setPantryItems(pantryRes.data);
      setRecommendations(recsRes.data.slice(0, 3)); // Top 3 recommended recipes
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  // Find expiring items
  const expiringItems = pantryItems.filter((item) => {
    if (!item.expiry_date) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expDate = new Date(item.expiry_date);
    expDate.setHours(0, 0, 0, 0);
    const diffDays = Math.round((expDate - today) / (1000 * 60 * 60 * 24));
    return diffDays <= 3;
  });

  return (
    <div>
      {/* Header & Greetings */}
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 className="page-title">What's in your kitchen today, {user?.username || "Sameeksha"}?</h1>
          <p className="page-subtitle">Track your pantry, avoid food waste & cook smart recipes.</p>
        </div>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <Link to="/upload" className="btn btn-primary btn-lg">
            📷 Scan Fridge
          </Link>
          <Link to="/pantry" className="btn btn-secondary btn-lg">
            ➕ Add Ingredient
          </Link>
        </div>
      </div>

      {/* Expiring Alert Banner */}
      {expiringItems.length > 0 && (
        <div className="alert alert-warning" style={{ marginBottom: "1.5rem" }}>
          <span>⚠️</span>
          <div>
            <strong>Expiring Soon Priority:</strong> You have {expiringItems.length} ingredient{expiringItems.length > 1 ? "s" : ""} expiring soon (
            {expiringItems.map((i) => i.name).join(", ")}). Check out our top recommended recipes to use them!
          </div>
        </div>
      )}

      {/* Your Pantry Section */}
      <div className="card" style={{ marginBottom: "2rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: "700" }}>Your Pantry Ingredients</h2>
          <Link to="/pantry" style={{ color: "var(--primary-dark)", fontWeight: "600", fontSize: "0.9rem" }}>
            View All ({pantryItems.length}) →
          </Link>
        </div>

        {pantryItems.length === 0 ? (
          <div style={{ textAlign: "center", padding: "2rem 0", color: "var(--text-muted)" }}>
            <p>Your pantry is currently empty.</p>
            <Link to="/pantry" className="btn btn-primary btn-sm" style={{ marginTop: "0.75rem" }}>
              Add Your First Ingredient
            </Link>
          </div>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {pantryItems.map((item) => (
              <IngredientChip
                key={item.id}
                name={item.name}
                available={true}
                quantity={item.quantity}
                unit={item.unit}
              />
            ))}
          </div>
        )}
      </div>

      {/* Top Recommended Recipes */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: "700" }}>✨ You Can Make Right Now</h2>
          <Link to="/recipes" style={{ color: "var(--primary-dark)", fontWeight: "600", fontSize: "0.9rem" }}>
            Explore All Recipes →
          </Link>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: "3rem" }}>Loading recipe recommendations...</div>
        ) : recommendations.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: "2.5rem" }}>
            <p style={{ color: "var(--text-muted)" }}>No recipe matches found for your current pantry.</p>
            <Link to="/upload" className="btn btn-primary" style={{ marginTop: "1rem" }}>
              📷 Scan Fridge to Add Ingredients
            </Link>
          </div>
        ) : (
          <div className="grid-3">
            {recommendations.map((rec) => (
              <RecipeCard key={rec.recipe.id} recommendation={rec} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
