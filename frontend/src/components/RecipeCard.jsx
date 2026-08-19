import { Link } from "react-router-dom";

const RecipeCard = ({ recommendation }) => {
  // Support both recommendation wrapper object and direct recipe object
  const recipe = recommendation?.recipe || recommendation;
  const matchPct = recommendation?.match_percentage ?? 100;
  const missingCount = recommendation?.missing_ingredients?.length || 0;
  const isExpiringPriority = recommendation?.is_expiring_soon_priority || false;

  return (
    <div className="card card-hover" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem", marginBottom: "0.5rem" }}>
          <h3 style={{ fontSize: "1.2rem", fontWeight: "700", color: "var(--text-main)" }}>
            {recipe.name}
          </h3>
          {isExpiringPriority && (
            <span className="badge badge-amber" style={{ whiteSpace: "nowrap" }}>
              🔥 Use soon
            </span>
          )}
        </div>

        {recipe.description && (
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "0.85rem" }}>
            {recipe.description}
          </p>
        )}

        {/* Match Percentage Progress Bar */}
        {recommendation && (
          <div style={{ marginBottom: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", fontWeight: "600" }}>
              <span>Ingredient Match</span>
              <span style={{ color: matchPct >= 80 ? "var(--primary-dark)" : matchPct >= 50 ? "var(--warning)" : "var(--danger)" }}>
                {matchPct}% match
              </span>
            </div>
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill"
                style={{
                  width: `${matchPct}%`,
                  backgroundColor: matchPct >= 80 ? "var(--primary)" : matchPct >= 50 ? "var(--warning)" : "var(--danger)"
                }}
              />
            </div>
            {missingCount > 0 ? (
              <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                Missing {missingCount} ingredient{missingCount > 1 ? "s" : ""}
              </span>
            ) : (
              <span style={{ fontSize: "0.8rem", color: "var(--primary-dark)", fontWeight: "600" }}>
                ✓ All ingredients available!
              </span>
            )}
          </div>
        )}

        {/* Details: Time & Difficulty */}
        <div style={{ display: "flex", gap: "1rem", fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
          {recipe.cooking_time && <span>⏱ {recipe.cooking_time} min</span>}
          {recipe.difficulty && <span style={{ textTransform: "capitalize" }}>🔥 {recipe.difficulty}</span>}
        </div>
      </div>

      <Link to={`/recipes/${recipe.id}`} className="btn btn-primary btn-sm" style={{ width: "100%", justifyContent: "center" }}>
        View Recipe & Instructions →
      </Link>
    </div>
  );
};

export default RecipeCard;
