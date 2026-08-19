import { useEffect, useState } from "react";
import PantryCard from "../components/PantryCard";
import api from "../services/api";

const CATEGORIES = ["Dairy", "Fruit", "Vegetable", "Grain", "Protein", "Beverage", "Snack", "Other"];

const Pantry = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("All");

  // Form State
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("");
  const [unit, setUnit] = useState("pieces");
  const [category, setCategory] = useState("Dairy");
  const [expiryDate, setExpiryDate] = useState("");
  const [formError, setFormError] = useState("");

  useEffect(() => {
    fetchPantryItems();
  }, []);

  const fetchPantryItems = async () => {
    setLoading(true);
    try {
      const response = await api.get("/pantry");
      setItems(response.data);
    } catch (err) {
      console.error("Failed to fetch pantry items", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    setFormError("");

    if (!name || !quantity || !unit) {
      setFormError("Please provide name, quantity, and unit.");
      return;
    }

    try {
      const payload = {
        name,
        quantity: parseFloat(quantity),
        unit,
        category: category || "Other",
        expiry_date: expiryDate || null,
      };

      const response = await api.post("/pantry", payload);
      setItems((prev) => [...prev, response.data]);

      // Reset form
      setName("");
      setQuantity("");
      setExpiryDate("");
    } catch (err) {
      setFormError(err.response?.data?.detail || "Failed to add pantry item.");
    }
  };

  const handleUpdateItem = async (id, updatedFields) => {
    try {
      const response = await api.patch(`/pantry/${id}`, updatedFields);
      setItems((prev) => prev.map((item) => (item.id === id ? response.data : item)));
    } catch (err) {
      console.error("Failed to update item", err);
    }
  };

  const handleDeleteItem = async (id) => {
    try {
      await api.delete(`/pantry/${id}`);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error("Failed to delete item", err);
    }
  };

  const filteredItems = selectedCategory === "All"
    ? items
    : items.filter((item) => item.category === selectedCategory);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Pantry Manager</h1>
        <p className="page-subtitle">Track your kitchen inventory and monitor expiration dates.</p>
      </div>

      {/* Add Pantry Item Form */}
      <div className="card" style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.15rem", fontWeight: "700", marginBottom: "1rem" }}>➕ Add New Pantry Ingredient</h2>
        {formError && <div className="alert alert-danger">{formError}</div>}

        <form onSubmit={handleAddItem} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem" }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Ingredient Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Milk, Eggs"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Quantity</label>
            <input
              type="number"
              step="0.1"
              className="form-input"
              placeholder="e.g. 2"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Unit</label>
            <input
              type="text"
              className="form-input"
              placeholder="litres, pieces, kg"
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Category</label>
            <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Expiry Date (Optional)</label>
            <input
              type="date"
              className="form-input"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
            />
          </div>

          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button type="submit" className="btn btn-primary" style={{ width: "100%", height: "42px" }}>
              Add to Pantry
            </button>
          </div>
        </form>
      </div>

      {/* Category Filter Pills */}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        {["All", ...CATEGORIES].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`btn btn-sm ${selectedCategory === cat ? "btn-primary" : "btn-secondary"}`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Pantry Items Grid */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem" }}>Loading pantry items...</div>
      ) : filteredItems.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
          <p style={{ color: "var(--text-muted)" }}>No pantry items found in this category.</p>
        </div>
      ) : (
        <div className="grid-3">
          {filteredItems.map((item) => (
            <PantryCard
              key={item.id}
              item={item}
              onUpdate={handleUpdateItem}
              onDelete={handleDeleteItem}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Pantry;
