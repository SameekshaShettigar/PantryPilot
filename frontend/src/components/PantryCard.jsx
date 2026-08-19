import { useState } from "react";

const PantryCard = ({ item, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [quantity, setQuantity] = useState(item.quantity);
  const [unit, setUnit] = useState(item.unit || "");

  // Expiry calculation
  let expiryNotice = null;
  let isExpiringSoon = false;

  if (item.expiry_date) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expDate = new Date(item.expiry_date);
    expDate.setHours(0, 0, 0, 0);

    const diffDays = Math.round((expDate - today) / (1000 * 60 * 60 * 24));

    if (diffDays <= 0) {
      expiryNotice = "Expired ⚠️";
      isExpiringSoon = true;
    } else if (diffDays === 1) {
      expiryNotice = "Expires tomorrow ⚠️";
      isExpiringSoon = true;
    } else if (diffDays <= 3) {
      expiryNotice = `Expires in ${diffDays} days ⚠️`;
      isExpiringSoon = true;
    } else {
      expiryNotice = `Expires in ${diffDays} days`;
    }
  }

  const handleSave = () => {
    onUpdate(item.id, { quantity: parseFloat(quantity), unit });
    setIsEditing(false);
  };

  return (
    <div className="card card-hover" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
          <h3 style={{ fontSize: "1.15rem", fontWeight: "700" }}>{item.name}</h3>
          {item.category && <span className="badge badge-green">{item.category}</span>}
        </div>

        {isEditing ? (
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
            <input
              type="number"
              className="form-input"
              style={{ width: "80px" }}
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
            <input
              type="text"
              className="form-input"
              style={{ width: "100px" }}
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
            />
            <button onClick={handleSave} className="btn btn-primary btn-sm">
              Save
            </button>
          </div>
        ) : (
          <div style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "0.75rem" }}>
            <strong style={{ color: "var(--text-main)", fontSize: "1.1rem" }}>{item.quantity}</strong> {item.unit}
          </div>
        )}

        {expiryNotice && (
          <div style={{ marginTop: "0.5rem" }}>
            <span className={`badge ${isExpiringSoon ? "badge-amber" : "badge-blue"}`}>
              {expiryNotice}
            </span>
          </div>
        )}
      </div>

      <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid var(--border-color)" }}>
        {!isEditing && (
          <button onClick={() => setIsEditing(true)} className="btn btn-secondary btn-sm">
            ✏️ Edit
          </button>
        )}
        <button onClick={() => onDelete(item.id)} className="btn btn-danger btn-sm">
          🗑️ Delete
        </button>
      </div>
    </div>
  );
};

export default PantryCard;
