import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { challengesAPI } from '../api/client';
import './AdminDashboardPage.css';

function LeaderboardPage() {
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);
  const displayPoints = (value) => (Number.isFinite(Number(value)) ? Number(value) : 0);
  const formatPoints = (value) => `${displayPoints(value)} pts`;

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await challengesAPI.getLeaderboard();
        setLeaders(response.data);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  if (loading) {
    return <div className="admin-container"><div className="loading">Loading leaderboard...</div></div>;
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Leaderboard</h1>
        <p>Ranked by total points and solved challenges</p>
      </div>

      <div className="leaderboard-section">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Username</th>
              <th>Points</th>
              <th>Solved</th>
            </tr>
          </thead>
          <tbody>
            {leaders.map((leader) => (
              <tr key={leader.id}>
                <td>#{leader.rank}</td>
                <td>{leader.username}</td>
                <td className="points">{formatPoints(leader.points)}</td>
                <td>{leader.solved}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '20px' }}>
        <Link to="/dashboard" className="nav-link">← Back to Dashboard</Link>
      </div>
    </div>
  );
}

export default LeaderboardPage;
