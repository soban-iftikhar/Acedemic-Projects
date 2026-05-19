import { useState, useEffect } from 'react';
import { adminAPI } from '../api/client';
import './AdminDashboardPage.css';

const EMPTY_FORM = {
  id: '',
  slug: '',
  name: '',
  description: '',
  category: 'Web Security',
  difficulty: 'Easy',
  points: 100,
  flag: ''
};

function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [challenges, setChallenges] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [editingChallengeId, setEditingChallengeId] = useState('');
  const [actionMessage, setActionMessage] = useState('');
  const [actionError, setActionError] = useState('');
  const [loading, setLoading] = useState(true);

  const displayPoints = (value) => (Number.isFinite(Number(value)) ? Number(value) : 0);
  const formatPoints = (value) => `${displayPoints(value)} pts`;

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const [statsRes, usersRes, submissionsRes, challengesRes] = await Promise.all([
        adminAPI.getAdminStats(),
        adminAPI.getAllUsers(),
        adminAPI.getSubmissions(undefined, 1, 100),
        adminAPI.getChallenges()
      ]);

      setStats(statsRes.data);
      setUsers(usersRes.data);
      setSubmissions(submissionsRes.data.submissions || []);
      setChallenges(challengesRes.data || []);
    } catch (err) {
      setActionError(err.response?.data?.error || 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData(EMPTY_FORM);
    setEditingChallengeId('');
  };

  const handleEdit = (challenge) => {
    setEditingChallengeId(challenge.id);
    setFormData({
      id: challenge.id,
      slug: challenge.slug,
      name: challenge.name,
      description: challenge.description,
      category: challenge.category || 'General',
      difficulty: challenge.difficulty,
      points: challenge.points,
      flag: challenge.flag
    });
    setActiveTab('challenges');
    setActionMessage('');
    setActionError('');
  };

  const handleDelete = async (challengeId) => {
    if (!window.confirm('Delete this challenge? This also removes related submissions and solved records.')) {
      return;
    }

    try {
      await adminAPI.deleteChallenge(challengeId);
      setActionMessage('Challenge deleted successfully.');
      setActionError('');
      await loadAdminData();
      if (editingChallengeId === challengeId) {
        resetForm();
      }
    } catch (err) {
      setActionError(err.response?.data?.error || 'Failed to delete challenge');
      setActionMessage('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setActionMessage('');
    setActionError('');

    const payload = {
      ...formData,
      points: Number(formData.points)
    };

    try {
      if (editingChallengeId) {
        await adminAPI.updateChallenge(editingChallengeId, payload);
        setActionMessage('Challenge updated successfully.');
      } else {
        await adminAPI.createChallenge(payload);
        setActionMessage('Challenge created successfully.');
      }

      await loadAdminData();
      resetForm();
    } catch (err) {
      setActionError(err.response?.data?.error || 'Failed to save challenge');
    }
  };

  if (loading) {
    return <div className="admin-container"><div className="loading">Loading admin panel...</div></div>;
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p>Manage challenges and monitor platform activity</p>
      </div>

      {actionMessage && <div className="admin-alert success">{actionMessage}</div>}
      {actionError && <div className="admin-alert error">{actionError}</div>}

      <div className="admin-tabs">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'challenges' ? 'active' : ''}`}
          onClick={() => setActiveTab('challenges')}
        >
          Challenges
        </button>
        <button 
          className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Users
        </button>
        <button 
          className={`tab-btn ${activeTab === 'submissions' ? 'active' : ''}`}
          onClick={() => setActiveTab('submissions')}
        >
          Submissions
        </button>
      </div>

      {activeTab === 'overview' && stats && (
        <div className="tab-content">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Total Users</div>
              <div className="stat-value">{stats.totalUsers}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Total Challenges</div>
              <div className="stat-value">{stats.totalChallenges}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Total Submissions</div>
              <div className="stat-value">{stats.totalSubmissions}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Solve Rate</div>
              <div className="stat-value">{stats.solveRate}%</div>
            </div>
          </div>

          <div className="leaderboard-section">
            <h2>Top Players</h2>
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
                {stats.leaderboard.map((entry, idx) => (
                  <tr key={`${entry.username}-${idx}`}>
                    <td>#{idx + 1}</td>
                    <td>{entry.username}</td>
                    <td className="points">{formatPoints(entry.points)}</td>
                    <td>{entry.solved}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="recent-submissions-section">
            <h2>Recent Submissions</h2>
            <div className="submissions-list">
              {stats.recentSubmissions.slice(0, 10).map((submission, idx) => (
                <div key={idx} className="submission-item">
                  <div className="submission-user">{submission.username}</div>
                  <div className="submission-challenge">{submission.challengeName}</div>
                  <div className={`submission-status ${submission.isCorrect ? 'correct' : 'incorrect'}`}>
                    {submission.isCorrect ? '✓ Correct' : '✗ Incorrect'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'challenges' && (
        <div className="tab-content">
          <h2>{editingChallengeId ? 'Edit Challenge' : 'Create Challenge'}</h2>
          <form className="challenge-form" onSubmit={handleSubmit}>
            <div className="form-grid">
              <label>
                ID
                <input
                  type="text"
                  value={formData.id}
                  onChange={(e) => setFormData((prev) => ({ ...prev, id: e.target.value }))}
                  required
                  disabled={!!editingChallengeId}
                />
              </label>
              <label>
                Slug
                <input
                  type="text"
                  value={formData.slug}
                  onChange={(e) => setFormData((prev) => ({ ...prev, slug: e.target.value }))}
                  required
                />
                <small style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>
                  Slug is the short URL key. ID is the internal challenge identifier.
                </small>
              </label>
              <label>
                Name
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                  required
                />
              </label>
              <label>
                Category
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData((prev) => ({ ...prev, category: e.target.value }))}
                />
              </label>
              <label>
                Difficulty
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData((prev) => ({ ...prev, difficulty: e.target.value }))}
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </label>
              <label>
                Points
                <input
                  type="number"
                  min="1"
                  value={formData.points}
                  onChange={(e) => setFormData((prev) => ({ ...prev, points: e.target.value }))}
                  required
                />
              </label>
            </div>

            <label>
              Description
              <textarea
                value={formData.description}
                onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                rows="3"
                required
              />
            </label>

            <label>
              Flag
              <input
                type="text"
                value={formData.flag}
                onChange={(e) => setFormData((prev) => ({ ...prev, flag: e.target.value }))}
                required
              />
            </label>

            <div className="form-actions">
              <button type="submit" className="primary-btn">{editingChallengeId ? 'Update' : 'Create'}</button>
              {editingChallengeId && (
                <button type="button" className="ghost-btn" onClick={resetForm}>Cancel Edit</button>
              )}
            </div>
          </form>

          <h2 style={{ marginTop: '30px' }}>All Challenges</h2>
          <table className="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Difficulty</th>
                <th>Points</th>
                <th>Solve Count</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {challenges.map((challenge) => (
                <tr key={challenge.id}>
                  <td>{challenge.id}</td>
                  <td>{challenge.name}</td>
                  <td>{challenge.difficulty}</td>
                  <td className="points">{formatPoints(challenge.points)}</td>
                  <td>{challenge.solveCount || 0}</td>
                  <td>
                    <button className="small-btn" onClick={() => handleEdit(challenge)}>Edit</button>
                    <button className="small-btn danger" onClick={() => handleDelete(challenge.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="tab-content">
          <h2>All Users</h2>
          <table className="users-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Points</th>
                <th>Challenges Solved</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, idx) => (
                <tr key={idx}>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td className="points">{formatPoints(user.points)}</td>
                  <td>{user.solved}</td>
                  <td>{new Date(user.joinedAt).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'submissions' && (
        <div className="tab-content">
          <h2>All Submissions</h2>
          <table className="submissions-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Challenge</th>
                <th>Flag</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub, idx) => (
                <tr key={idx}>
                  <td>{sub.username}</td>
                  <td>{sub.challengeName}</td>
                  <td className="flag">{sub.flag}</td>
                  <td className={`status ${sub.isCorrect ? 'correct' : 'incorrect'}`}>
                    {sub.isCorrect ? '✓' : '✗'}
                  </td>
                  <td>{new Date(sub.submittedAt).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AdminDashboardPage;
