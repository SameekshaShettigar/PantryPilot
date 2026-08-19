import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";

import Dashboard from "./pages/Dashboard";
import ImageUpload from "./pages/ImageUpload";
import Login from "./pages/Login";
import Pantry from "./pages/Pantry";
import RecipeDetails from "./pages/RecipeDetails";
import Recipes from "./pages/Recipes";
import Register from "./pages/Register";
import ShoppingList from "./pages/ShoppingList";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/pantry"
                element={
                  <ProtectedRoute>
                    <Pantry />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/recipes"
                element={
                  <ProtectedRoute>
                    <Recipes />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/recipes/:id"
                element={
                  <ProtectedRoute>
                    <RecipeDetails />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/shopping-list"
                element={
                  <ProtectedRoute>
                    <ShoppingList />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/upload"
                element={
                  <ProtectedRoute>
                    <ImageUpload />
                  </ProtectedRoute>
                }
              />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
