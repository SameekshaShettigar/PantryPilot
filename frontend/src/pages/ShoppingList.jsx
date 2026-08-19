import { useEffect, useState } from "react";
import api from "../services/api";

const ShoppingList = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  // Add Item form state
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("");
  const [unit, setUnit] = useState("");
  const [category, setCategory] = useState("Other");

  useEffect(() => {
    fetchShoppingList();
  }, []);

  const fetchShoppingList = async () => {
    setLoading(true);
    try {
      const response = await api.get("/shopping-list");
      setItems(response.data);
    } catch (err) {
      console.error("Failed to fetch shopping list", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = async (item) => {
    const newStatus = !item.is_completed;
    try {
      const response = await api.patch(`/shopping-list/${item.id}`, {
        is_completed: newStatus,
      });
      setItems((prev) => prev.map((i) => (i.id === item.id ? response.data : i)));
    } catch (err) {
      console.error("Failed to toggle status", err);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      const payload = {
        name,
        quantity: quantity || null,
        unit: unit || null,
        category: category || "Other",
      };

      const response = await api.post("/shopping-list", payload);
      setItems((prev) => [response.data, ...prev]);

      setName("");
      setQuantity("");
      setUnit("");
    } catch (err) {
      console.error("Failed to add shopping list item", err);
    }
  };

  const handleDeleteItem = async (id) => {
    try {
      await api.delete(`/shopping-list/${id}`);
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      console.error("Failed to delete shopping list item", err);
    }
  };

  const handleClearCompleted = async () => {
    const completedItems = items.filter((i) => i.is_completed);
    try {
      await Promise.all(completedItems.map((i) => api.delete(`/shopping-list/${i.id}`)));
      setItems((prev) => prev.filter((i) => !i.is_completed));
    } catch (err) {
      console.error("Failed to clear completed items", err);
    }
  };

  const completedCount = items.filter((i) => i.is_completed).length;

  return (
    <div style={{ maxWidth: "750px", margin: "0 auto" }}>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 className="page-title">🛒 Shopping List</h1>
          <p className="page-subtitle">Keep track of groceries & missing ingredients to buy.</p>
        </div>

        {completedCount > 0 && (
          <button onClick={handleClearCompleted} className="btn btn-secondary btn-sm">
            🗑️ Clear Completed ({completedCount})
          </button>
        )}
      </div>

      {/* Quick Add Form */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <form onSubmit={handleAddItem} style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <input
            type="text"
            className="form-input"
            style={{ flex: 2, minWidth: "180px" }}
            placeholder="Add item (e.g. Milk, Garlic, Butter)..."
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="text"
            className="form-input"
            style={{ flex: 1, minWidth: "90px" }}
            placeholder="Qty"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
          <input
            type="text"
            className="form-input"
            style={{ flex: 1, minWidth: "90px" }}
            placeholder="Unit"
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">
            ➕ Add
          </button>
        </form>
      </div>

      {/* Shopping List Items */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem" }}>Loading shopping list...</div>
      ) : items.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
          <p style={{ color: "var(--text-muted)" }}>Your shopping list is empty!</p>
        </div>
      ) : (
        <div className="card" style={{ padding: "0.5rem 1rem" }}>
          {items.map((item) => (
            <div
              key={item.id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0.85rem 0.5rem",
                borderBottom: "1px solid var(--border-color)",
                opacity: item.is_completed ? 0.6 : 1,
              }}
            >
              <label style={{ display: "flex", alignItems: "center", gap: "0.75rem", cursor: "pointer", flex: 1 }}>
                <input
                  type="checkbox"
                  checked={item.is_completed}
                  onChange={() => handleToggleComplete(item)}
                  style={{ width: "18px", height: "18px", accentColor: "var(--primary)" }}
                />
                <span
                  style={{
                    fontSize: "1.05rem",
                    fontWeight: "500",
                    textDecoration: item.is_completed ? "line-through" : "none",
                  }}
                >
                  {item.name}
                </span>
                {(item.quantity || item.unit) && (
                  <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                    ({item.quantity || ""} {item.unit || ""})
                  </span>
                )}
                {item.category && item.category !== "Other" && (
                  <span className="badge badge-blue" style={{ fontSize: "0.7rem" }}>
                    {item.category}
                  </span>
                )}
              </label>

              <button
                onClick={() => handleDeleteItem(item.id)}
                className="btn btn-secondary btn-sm"
                style={{ border: "none", color: "var(--danger)", padding: "0.25rem 0.5rem" }}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ShoppingList;
