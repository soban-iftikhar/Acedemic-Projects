import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { authAPI } from './api/client';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import LeaderboardPage from './pages/LeaderboardPage';
import ChallengePage from './pages/ChallengePage';
import IDORProfilePage from './pages/IDORProfilePage';
import BACSecretPanelPage from './pages/BACSecretPanelPage';
import Navbar from './components/Navbar';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkUser = async () => {
      try {
        const response = await authAPI.getCurrentUser();
        setUser(response.data);
      } catch (err) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkUser();
  }, []);

  const PrivateRoute = ({ children }) => {
    if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;
    return user ? children : <Navigate to="/login" />;
  };

  const AdminRoute = ({ children }) => {
    if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;
    return user && user.isAdmin ? children : <Navigate to="/dashboard" />;
  };

  const PlayerRoute = ({ children }) => {
    if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;
    if (!user) return <Navigate to="/login" />;
    return user.isAdmin ? <Navigate to="/admin" /> : children;
  };

  return (
    <Router>
      {user && <Navbar user={user} setUser={setUser} />}
      <Routes>
        <Route path="/login" element={<LoginPage setUser={setUser} user={user} />} />
        <Route path="/register" element={<RegisterPage setUser={setUser} user={user} />} />
        
        <Route path="/dashboard" element={
          <PlayerRoute>
            <DashboardPage user={user} />
          </PlayerRoute>
        } />

        <Route path="/leaderboard" element={
          <PlayerRoute>
            <LeaderboardPage user={user} />
          </PlayerRoute>
        } />

        <Route path="/challenge/idor/profile" element={
          <PlayerRoute>
            <IDORProfilePage user={user} />
          </PlayerRoute>
        } />

        <Route path="/challenge/bac/secret-panel" element={
          <PlayerRoute>
            <BACSecretPanelPage user={user} />
          </PlayerRoute>
        } />
        
        <Route path="/challenge/:id" element={
          <PlayerRoute>
            <ChallengePage user={user} setUser={setUser} />
          </PlayerRoute>
        } />
        
        <Route path="/admin" element={
          <AdminRoute>
            <AdminDashboardPage user={user} />
          </AdminRoute>
        } />
        
        <Route path="/" element={user ? <Navigate to={user.isAdmin ? '/admin' : '/dashboard'} /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
