import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user_info");
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(false);

  // Sync token changes
  useEffect(() => {
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_info");
      setUser(null);
    }
  }, [token]);

  const login = async (usernameOrEmail, password) => {
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append("username", usernameOrEmail);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const accessToken = response.data.access_token;
      setToken(accessToken);

      // Store basic user profile info from login username/email
      const userInfo = {
        username: usernameOrEmail.includes("@") ? usernameOrEmail.split("@")[0] : usernameOrEmail,
        email: usernameOrEmail.includes("@") ? usernameOrEmail : "",
      };
      setUser(userInfo);
      localStorage.setItem("user_info", JSON.stringify(userInfo));

      return { success: true };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Login failed. Please check your credentials.";
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password) => {
    setLoading(true);
    try {
      const regResp = await api.post("/auth/register", {
        username,
        email,
        password,
      });

      // Auto login after registration
      const loginRes = await login(username, password);
      if (loginRes.success) {
        const userInfo = { id: regResp.data.id, username, email };
        setUser(userInfo);
        localStorage.setItem("user_info", JSON.stringify(userInfo));
      }
      return { success: true };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Registration failed. Please try again.";
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_info");
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
