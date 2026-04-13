import { Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import NavBar from "./components/NavBar";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminPage from "./pages/AdminPage";
import ChallengeLabsPage from "./pages/ChallengeLabsPage";
import ChallengesPage from "./pages/ChallengesPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ScoreboardPage from "./pages/ScoreboardPage";

function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/challenges"
          element={
            <ProtectedRoute>
              <ChallengesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/labs"
          element={
            <ProtectedRoute>
              <ChallengeLabsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scoreboard"
          element={
            <ProtectedRoute>
              <ScoreboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute adminOnly>
              <AdminPage />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </>
  );
}

export default App;
