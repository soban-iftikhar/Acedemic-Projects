import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { challengesAPI } from '../api/client';
import './DashboardPage.css';

function DashboardPage({ user }) {
  const [challenges, setChallenges] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [challengesRes, progressRes] = await Promise.all([
          challengesAPI.getAllChallenges(),
          challengesAPI.getUserProgress()
        ]);
        
        setChallenges(challengesRes.data);
        setProgress(progressRes.data);
      } catch (err) {
        setError('Failed to load challenges');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="dashboard-container"><div className="loading">Loading challenges...</div></div>;
  }

  if (error) {
    return <div className="dashboard-container"><div className="error-message">{error}</div></div>;
  }

  const difficultyColors = {
    'Easy': '#10b981',
    'Medium': '#f59e0b',
    'Hard': '#ef4444'
  };

  const progressPercentage = progress ? (progress.solvedCount / progress.totalChallenges) * 100 : 0;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Challenge Dashboard</h1>
        <p>Solve challenges to earn points and climb the leaderboard</p>
      </div>

      <div className="stats-section">
        <div className="stat-card">
          <div className="stat-label">Total Points</div>
          <div className="stat-value">{progress?.totalPoints || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Challenges Solved</div>
          <div className="stat-value">{progress?.solvedCount || 0}/{progress?.totalChallenges || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Completion Rate</div>
          <div className="stat-value">{progressPercentage.toFixed(0)}%</div>
        </div>
      </div>

      <div className="progress-section">
        <h2>Overall Progress</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: progressPercentage + '%' }}></div>
        </div>
        <p className="progress-text">{progress?.solvedCount || 0} of {progress?.totalChallenges || 0} challenges solved</p>
      </div>

      <div className="challenges-section">
        <h2>Available Challenges</h2>
        <div className="challenges-grid">
          {challenges.map(challenge => {
            const isSolved = progress?.progress.find(p => p.id === challenge.id)?.solved;
            return (
              <Link to={`/challenge/${challenge.id}`} key={challenge.id} className="challenge-card-link">
                <div className={`challenge-card ${isSolved ? 'solved' : ''}`}>
                  <div className="challenge-header">
                    <h3>{challenge.name}</h3>
                    <span className="difficulty-badge" style={{ backgroundColor: difficultyColors[challenge.difficulty] }}>
                      {challenge.difficulty}
                    </span>
                  </div>
                  <p className="challenge-description">{challenge.description}</p>
                  <div className="challenge-footer">
                    <span className="points">{challenge.points} pts</span>
                    {isSolved && <span className="solved-badge">✓ Solved</span>}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
