import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import IngredientChip from "../components/IngredientChip";
import api from "../services/api";

const RecipeDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [pantryItems, setPantryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addingToShoppingList, setAddingToShoppingList] = useState(false);
  const [shoppingListMessage, setShoppingListMessage] = useState("");

  useEffect(() => {
    fetchRecipeAndPantry();
  }, [id]);

  const fetchRecipeAndPantry = async () => {
    setLoading(true);
    try {
      const [recipeRes, pantryRes] = await Promise.all([
        api.get(`/recipes/${id}`),
        api.get("/pantry"),
      ]);
      setRecipe(recipeRes.data);
      setPantryItems(pantryRes.data);
    } catch (err) {
      console.error("Failed to fetch recipe details", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: "center", padding: "3rem" }}>Loading recipe...</div>;
  }

  if (!recipe) {
    return (
      <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
        <h2>Recipe not found</h2>
        <Link to="/recipes" className="btn btn-primary" style={{ marginTop: "1rem" }}>
          ← Back to Recipes
        </Link>
      </div>
    );
  }

  // Determine ingredient availability
  const pantryNamesNormalized = pantryItems.map((p) => p.name.trim().toLowerCase());

  const availableIngredients = [];
  const missingIngredients = [];

  recipe.ingredients.forEach((ing) => {
    const ingNameLower = ing.name.trim().toLowerCase();
    const isAvailable = pantryNamesNormalized.some(
      (pName) => pName === ingNameLower || pName.includes(ingNameLower) || ingNameLower.includes(pName)
    );

    if (isAvailable) {
      availableIngredients.push(ing);
    } else {
      missingIngredients.push(ing);
    }
  });

  const handleAddMissingToShoppingList = async () => {
    if (missingIngredients.length === 0) return;
    setAddingToShoppingList(true);
    setShoppingListMessage("");

    try {
      const payload = {
        items: missingIngredients.map((ing) => ({
          name: ing.name,
          quantity: ing.quantity ? String(ing.quantity) : "1",
          unit: ing.unit || "item",
          category: "Other",
        })),
      };

      await api.post("/shopping-list/batch", payload);
      setShoppingListMessage(`Added ${missingIngredients.length} missing ingredient(s) to your shopping list!`);
      setTimeout(() => navigate("/shopping-list"), 1200);
    } catch (err) {
      console.error("Failed to add items to shopping list", err);
      setShoppingListMessage("Failed to add missing ingredients.");
    } finally {
      setAddingToShoppingList(false);
    }
  };

  return (
    <div style={{ maxWidth: "850px", margin: "0 auto" }}>
      <Link to="/recipes" style={{ color: "var(--text-muted)", fontSize: "0.9rem", fontWeight: "500", display: "inline-block", marginBottom: "1rem" }}>
        ← Back to Recipes
      </Link>

      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
          <h1 className="page-title">{recipe.name}</h1>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {recipe.cooking_time && <span className="badge badge-blue">⏱ {recipe.cooking_time} min</span>}
            {recipe.difficulty && <span className="badge badge-green" style={{ textTransform: "capitalize" }}>🔥 {recipe.difficulty}</span>}
          </div>
        </div>

        {recipe.description && (
          <p style={{ color: "var(--text-muted)", fontSize: "1.05rem", marginBottom: "1.5rem" }}>
            {recipe.description}
          </p>
        )}

        {shoppingListMessage && (
          <div className="alert alert-success">{shoppingListMessage}</div>
        )}

        {/* Ingredients Checklist Section */}
        <h2 style={{ fontSize: "1.2rem", fontWeight: "700", marginBottom: "0.75rem" }}>
          Ingredients Checklist
        </h2>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "1.5rem" }}>
          {recipe.ingredients.map((ing) => {
            const isAvail = availableIngredients.some((a) => a.name === ing.name);
            return (
              <IngredientChip
                key={ing.id || ing.name}
                name={ing.name}
                available={isAvail}
                quantity={ing.quantity}
                unit={ing.unit}
              />
            );
          })}
        </div>

        {/* Missing Ingredients Alert & Action */}
        {missingIngredients.length > 0 ? (
          <div className="alert alert-warning" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <strong>Missing {missingIngredients.length} ingredient(s):</strong>{" "}
              {missingIngredients.map((m) => m.name).join(", ")}
            </div>
            <button
              onClick={handleAddMissingToShoppingList}
              className="btn btn-primary btn-sm"
              disabled={addingToShoppingList}
            >
              {addingToShoppingList ? "Adding..." : "🛒 Add Missing Ingredients to Shopping List"}
            </button>
          </div>
        ) : (
          <div className="alert alert-success">
            🎉 You have all ingredients required to cook this recipe right now!
          </div>
        )}

        {/* Instructions */}
        <h2 style={{ fontSize: "1.2rem", fontWeight: "700", marginTop: "1.5rem", marginBottom: "0.75rem" }}>
          Cooking Instructions
        </h2>
        <div style={{ whiteSpace: "pre-line", color: "var(--text-main)", lineHeight: "1.7", background: "var(--bg-main)", padding: "1.25rem", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)" }}>
          {recipe.instructions}
        </div>
      </div>
    </div>
  );
};

export default RecipeDetails;
