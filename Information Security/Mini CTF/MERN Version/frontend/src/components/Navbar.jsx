import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/client';
import './Navbar.css';

function Navbar({ user, setUser }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Mini CTF
        </Link>
        
        <div className="navbar-menu">
          {user?.isAdmin ? (
            <Link to="/admin" className="nav-link">Admin Dashboard</Link>
          ) : (
            <>
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
              <Link to="/leaderboard" className="nav-link">Leaderboard</Link>
            </>
          )}
          
          <div className="user-info">
            <span className="username">{user?.username}</span>
            <span className="points">{user?.totalPoints || 0} pts</span>
            <button className="logout-btn" onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
