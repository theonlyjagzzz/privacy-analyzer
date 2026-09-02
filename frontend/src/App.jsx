import React, { useState } from "react";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import TopBar from "./components/TopBar";
import ProtectedRoute from "./components/ProtectedRoute";
import Auth from "./pages/Auth";
import Submit from "./pages/Submit";
import Dashboard from "./pages/Dashboard";
import Report from "./pages/Report";

export default function App() {
  const [user, setUser] = useState(() => localStorage.getItem("userEmail") || "");
  const navigate = useNavigate();

  const handleAuthed = (email) => {
    setUser(email);
    localStorage.setItem("userEmail", email);
  };

  const handleLogout = () => {
    setUser("");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("token");
    navigate("/login");
  };

  const isAuthed = Boolean(user);

  return (
    <div className="min-h-screen bg-paper">
      {isAuthed && <TopBar user={user} onLogout={handleLogout} />}
      <Routes>
        <Route path="/login" element={<Auth onAuthed={handleAuthed} />} />
        <Route
          path="/submit"
          element={
            <ProtectedRoute isAuthed={isAuthed}>
              <Submit />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute isAuthed={isAuthed}>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/report/:id"
          element={
            <ProtectedRoute isAuthed={isAuthed}>
              <Report />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to={isAuthed ? "/submit" : "/login"} replace />} />
      </Routes>
    </div>
  );
}
