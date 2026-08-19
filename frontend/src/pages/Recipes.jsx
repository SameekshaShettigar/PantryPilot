import { useEffect, useState } from "react";
import RecipeCard from "../components/RecipeCard";
import api from "../services/api";

const Recipes = () => {
  const [activeTab, setActiveTab] = useState("recommendations"); // 'recommendations' | 'all' | 'generate'
  const [recommendations, setRecommendations] = useState([]);
  const [allRecipes, setAllRecipes] = useState([]);
  const [loading, setLoading] = useState(true);

  // AI Generator state
  const [generating, setGenerating] = useState(false);
  const [generatedRecipe, setGeneratedRecipe] = useState(null);
  const [genError, setGenError] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [recsRes, allRes] = await Promise.all([
        api.post("/recipes/recommend"),
        api.get("/recipes"),
      ]);
      setRecommendations(recsRes.data);
      setAllRecipes(allRes.data);
    } catch (err) {
      console.error("Failed to load recipes", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRecipe = async () => {
    setGenerating(true);
    setGenError("");
    setGeneratedRecipe(null);
    try {
      const response = await api.post("/recipes/generate");
      setGeneratedRecipe(response.data);
    } catch (err) {
      setGenError(err.response?.data?.detail || "Recipe generation failed.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Recipe Intelligence Engine</h1>
        <p className="page-subtitle">Discover recipes based on your available ingredients & food expiration dates.</p>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: "flex", gap: "1rem", borderBottom: "1px solid var(--border-color)", marginBottom: "1.5rem" }}>
        <button
          onClick={() => setActiveTab("recommendations")}
          className={`btn ${activeTab === "recommendations" ? "btn-primary" : "btn-secondary"}`}
        >
          ✨ Recommended for You ({recommendations.length})
        </button>
        <button
          onClick={() => setActiveTab("all")}
          className={`btn ${activeTab === "all" ? "btn-primary" : "btn-secondary"}`}
        >
          📖 Recipe Catalog ({allRecipes.length})
        </button>
        <button
          onClick={() => setActiveTab("generate")}
          className={`btn ${activeTab === "generate" ? "btn-primary" : "btn-secondary"}`}
        >
          🤖 Cook Something New (AI)
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem" }}>Loading recipes...</div>
      ) : (
        <>
          {/* Tab 1: Recommendations */}
          {activeTab === "recommendations" && (
            <div>
              {recommendations.length === 0 ? (
                <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
                  <p style={{ color: "var(--text-muted)" }}>No recommendations available. Try adding ingredients to your pantry!</p>
                </div>
              ) : (
                <div className="grid-3">
                  {recommendations.map((rec) => (
                    <RecipeCard key={rec.recipe.id} recommendation={rec} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Tab 2: All Catalog Recipes */}
          {activeTab === "all" && (
            <div className="grid-3">
              {allRecipes.map((recipe) => (
                <RecipeCard key={recipe.id} recommendation={recipe} />
              ))}
            </div>
          )}

          {/* Tab 3: Custom AI Recipe Generator */}
          {activeTab === "generate" && (
            <div>
              <div className="card" style={{ marginBottom: "1.5rem" }}>
                <h2 style={{ fontSize: "1.25rem", fontWeight: "700", marginBottom: "0.5rem" }}>
                  ✨ AI Recipe Generator
                </h2>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1.25rem" }}>
                  Gemini will create a unique recipe tailored to your current pantry ingredients with Pydantic validation guarantees.
                </p>

                {genError && <div className="alert alert-danger">{genError}</div>}

                <button onClick={handleGenerateRecipe} className="btn btn-primary btn-lg" disabled={generating}>
                  {generating ? "🤖 Gemini Chef is cooking up a recipe..." : "✨ Generate AI Recipe Now"}
                </button>
              </div>

              {/* Generated Result Card */}
              {generatedRecipe && (
                <div className="card" style={{ border: "2px solid var(--primary)", backgroundColor: "white" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                    <div>
                      <span className="badge badge-green" style={{ marginBottom: "0.5rem" }}>
                        AI Generated & Pydantic Validated
                      </span>
                      <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "var(--text-main)" }}>
                        {generatedRecipe.name}
                      </h2>
                      <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>{generatedRecipe.description}</p>
                    </div>

                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>⏱ {generatedRecipe.cooking_time} min</div>
                      <span className="badge badge-blue" style={{ marginTop: "0.25rem" }}>
                        🔥 {generatedRecipe.difficulty}
                      </span>
                    </div>
                  </div>

                  <h3 style={{ fontSize: "1.1rem", fontWeight: "700", marginBottom: "0.5rem" }}>Ingredients Needed:</h3>
                  <ul style={{ paddingLeft: "1.25rem", marginBottom: "1.25rem", color: "var(--text-main)" }}>
                    {generatedRecipe.ingredients.map((ing, idx) => (
                      <li key={idx} style={{ marginBottom: "0.25rem" }}>
                        <strong>{ing.name}</strong> — {ing.quantity} {ing.unit}
                      </li>
                    ))}
                  </ul>

                  <h3 style={{ fontSize: "1.1rem", fontWeight: "700", marginBottom: "0.5rem" }}>Instructions:</h3>
                  <p style={{ whiteSpace: "pre-line", color: "var(--text-main)", lineHeight: "1.6" }}>
                    {generatedRecipe.instructions}
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Recipes;
