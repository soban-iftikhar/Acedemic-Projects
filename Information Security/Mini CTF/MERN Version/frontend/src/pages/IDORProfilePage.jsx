import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { challengesAPI } from '../api/client';
import './ChallengePage.css';

function IDORProfilePage() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get('id') || '1';
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await challengesAPI.getIdorProfile(id);
        setProfile(response.data.profile);
      } catch (err) {
        setError(err.response?.data?.error || 'Profile not found');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [id]);

  if (loading) {
    return <div className="challenge-container"><div className="loading">Loading profile...</div></div>;
  }

  if (error || !profile) {
    return <div className="challenge-container"><div className="error-message">{error || 'Profile not found'}</div></div>;
  }

  const isAdminProfile = profile.role === 'admin';

  return (
    <div className="challenge-container">
      <div className="challenge-header">
        <Link to="/challenge/idor" className="back-btn">← Back</Link>
        <h1>Profile Viewer</h1>
        <div className="challenge-meta">
          <span className="difficulty">Easy</span>
          <span className="points">100 points</span>
        </div>
      </div>

      <div className="challenge-content">
        <div className="challenge-description">
          <h2>Unauthorized Profile Access</h2>
          <p>Some profile data is returned too eagerly when identifiers are adjusted.</p>
        </div>

        <div className="challenge-interactive">
          <h3>Profile Data</h3>
          <div style={{ display: 'grid', gap: '10px', fontFamily: 'monospace' }}>
            <div><strong>User ID:</strong> {id}</div>
            <div><strong>Username:</strong> {profile.username}</div>
            <div><strong>Email:</strong> {profile.email}</div>
            <div><strong>Role:</strong> {profile.role}</div>
            <div><strong>Score:</strong> {profile.score} pts</div>
            <div><strong>Secret Data:</strong> {profile.secretData}</div>
          </div>
        </div>

        <div className="flag-submission">
          <h2>Flag</h2>
          {isAdminProfile ? (
            <div className="message success" style={{ whiteSpace: 'pre-wrap' }}>
              ✓ High-privilege profile reached.
              <br />
              Flag: {profile.secretData}
            </div>
          ) : (
            <div className="message" style={{ whiteSpace: 'pre-wrap' }}>
              Keep mapping profile IDs. Not every record contains challenge data.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default IDORProfilePage;
