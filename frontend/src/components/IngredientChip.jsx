const IngredientChip = ({ name, available = true, quantity, unit }) => {
  return (
    <span className={`chip ${available ? "chip-available" : "chip-missing"}`}>
      <span className="chip-icon">{available ? "✓" : "✗"}</span>
      <span className="chip-name">{name}</span>
      {quantity && <span style={{ opacity: 0.8, fontSize: "0.8em" }}>({quantity} {unit || ""})</span>}
    </span>
  );
};

export default IngredientChip;
