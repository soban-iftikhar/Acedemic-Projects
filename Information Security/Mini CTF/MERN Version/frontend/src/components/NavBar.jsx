import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function onLogout() {
    await logout();
    navigate("/login");
  }

  if (!user) {
    return null;
  }

  return (
    <header className="topbar">
      <div className="brand">MINICTF MERN</div>
      <nav>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/challenges">Challenges</Link>
        <Link to="/labs">Challenge Labs</Link>
        <Link to="/scoreboard">Scoreboard</Link>
        {user.role === "admin" && <Link to="/admin">Admin</Link>}
      </nav>
      <div className="userbox">
        <span>{user.username}</span>
        <button onClick={onLogout}>Logout</button>
      </div>
    </header>
  );
}
