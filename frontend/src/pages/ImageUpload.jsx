import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  // HITL state
  const [detectedItems, setDetectedItems] = useState([]);
  const [isDetected, setIsDetected] = useState(false);
  const [savingBatch, setSavingBatch] = useState(false);

  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError("");
      setIsDetected(false);
      setDetectedItems([]);
    }
  };

  const handleUploadAndDetect = async () => {
    if (!selectedFile) {
      setError("Please select an image file first.");
      return;
    }

    setUploading(true);
    setError("");

    try {
      // 1. Upload Image file
      const formData = new FormData();
      formData.append("file", selectedFile);

      const uploadRes = await api.post("/images/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const imageId = uploadRes.data.id;

      // 2. Trigger AI Vision Detection
      const detectRes = await api.post(`/images/${imageId}/detect`);
      const rawItems = detectRes.data.items || [];

      // Map detected items with HITL state
      const hitlItems = rawItems.map((item, idx) => ({
        id: idx,
        name: item.name,
        category: item.category || "Other",
        quantity: item.estimated_quantity || 1.0,
        unit: item.unit || "pieces",
        confidence: item.confidence,
        accepted: item.confidence >= 0.50, // Auto check if >= 50%
      }));

      setDetectedItems(hitlItems);
      setIsDetected(true);
    } catch (err) {
      console.error("Upload & Detection failed", err);
      setError(err.response?.data?.detail || "Food detection failed. Please try another image.");
    } finally {
      setUploading(false);
    }
  };

  const handleToggleItem = (id) => {
    setDetectedItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, accepted: !item.accepted } : item))
    );
  };

  const handleItemChange = (id, field, value) => {
    setDetectedItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, [field]: value } : item))
    );
  };

  const handleAddSelectedToPantry = async () => {
    const selected = detectedItems.filter((i) => i.accepted);
    if (selected.length === 0) {
      setError("Please select at least one item to add to your pantry.");
      return;
    }

    setSavingBatch(true);
    setError("");

    try {
      const payload = selected.map((item) => ({
        name: item.name,
        quantity: parseFloat(item.quantity) || 1.0,
        unit: item.unit,
        category: item.category,
      }));

      await api.post("/pantry/batch", payload);
      navigate("/pantry");
    } catch (err) {
      console.error("Failed to add items to pantry", err);
      setError(err.response?.data?.detail || "Failed to add items to pantry.");
    } finally {
      setSavingBatch(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <div className="page-header">
        <h1 className="page-title">📷 AI Fridge & Pantry Scanner</h1>
        <p className="page-subtitle">Upload a photo of your fridge or kitchen to auto-detect ingredients.</p>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {/* Upload Dropzone Card */}
      {!isDetected && (
        <div className="card" style={{ textAlign: "center", padding: "3rem 1.5rem", border: "2px dashed var(--border-color)", marginBottom: "1.5rem" }}>
          {previewUrl ? (
            <div style={{ marginBottom: "1.5rem" }}>
              <img src={previewUrl} alt="Preview" style={{ maxHeight: "250px", borderRadius: "var(--radius-md)", objectFit: "cover" }} />
            </div>
          ) : (
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📷</div>
          )}

          <h2 style={{ fontSize: "1.25rem", fontWeight: "700", marginBottom: "0.5rem" }}>
            Upload Fridge or Pantry Image
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
            Supports JPEG, PNG, WebP up to 10MB
          </p>

          <input
            type="file"
            accept="image/*"
            id="fileInput"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />

          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <label htmlFor="fileInput" className="btn btn-secondary">
              Choose Image
            </label>

            {selectedFile && (
              <button onClick={handleUploadAndDetect} className="btn btn-primary" disabled={uploading}>
                {uploading ? "Analyzing Image with Gemini..." : "✨ Detect Food Items"}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Human-In-The-Loop (HITL) Review Panel */}
      {isDetected && (
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
            <div>
              <h2 style={{ fontSize: "1.3rem", fontWeight: "700" }}>PantryPilot Detected Items</h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
                Review, edit, or uncheck items before saving them to your pantry.
              </p>
            </div>
            <span className="badge badge-green">Human-In-The-Loop AI</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1.5rem" }}>
            {detectedItems.map((item) => (
              <div
                key={item.id}
                style={{
                  display: "grid",
                  gridTemplateColumns: "auto 1fr 100px 100px auto",
                  gap: "0.75rem",
                  alignItems: "center",
                  padding: "0.75rem",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--border-color)",
                  backgroundColor: item.accepted ? "white" : "var(--bg-main)",
                  opacity: item.accepted ? 1 : 0.6,
                }}
              >
                <input
                  type="checkbox"
                  checked={item.accepted}
                  onChange={() => handleToggleItem(item.id)}
                  style={{ width: "18px", height: "18px", accentColor: "var(--primary)" }}
                />

                {/* Edit Name */}
                <input
                  type="text"
                  className="form-input"
                  value={item.name}
                  onChange={(e) => handleItemChange(item.id, "name", e.target.value)}
                  disabled={!item.accepted}
                />

                {/* Edit Quantity */}
                <input
                  type="number"
                  step="0.1"
                  className="form-input"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(item.id, "quantity", e.target.value)}
                  disabled={!item.accepted}
                />

                {/* Edit Unit */}
                <input
                  type="text"
                  className="form-input"
                  value={item.unit}
                  onChange={(e) => handleItemChange(item.id, "unit", e.target.value)}
                  disabled={!item.accepted}
                />

                {/* Confidence Badge */}
                <span className={`badge ${item.confidence >= 0.8 ? "badge-green" : "badge-amber"}`}>
                  {Math.round(item.confidence * 100)}%
                </span>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
            <button onClick={() => setIsDetected(false)} className="btn btn-secondary">
              Scan Another Photo
            </button>
            <button onClick={handleAddSelectedToPantry} className="btn btn-primary btn-lg" disabled={savingBatch}>
              {savingBatch ? "Saving to Pantry..." : "✓ Add Selected to Pantry"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
