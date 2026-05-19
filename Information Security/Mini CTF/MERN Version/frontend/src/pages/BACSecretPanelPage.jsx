import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { challengesAPI } from '../api/client';
import './ChallengePage.css';

function BACSecretPanelPage() {
  const [panel, setPanel] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPanel = async () => {
      try {
        const response = await challengesAPI.getBacSecretPanel();
        setPanel(response.data);
      } finally {
        setLoading(false);
      }
    };

    fetchPanel();
  }, []);

  if (loading) {
    return <div className="challenge-container"><div className="loading">Opening secret panel...</div></div>;
  }

  return (
    <div className="challenge-container">
      <div className="challenge-header">
        <Link to="/challenge/bac" className="back-btn">← Back</Link>
        <h1>Secret Admin Panel</h1>
        <div className="challenge-meta">
          <span className="difficulty">Easy</span>
          <span className="points">100 points</span>
        </div>
      </div>

      <div className="challenge-content">
        <div className="challenge-description">
          <h2>Unauthorized Access</h2>
          <p>A restricted-looking panel responded even though you are not meant to be here.</p>
        </div>

        <div className="challenge-interactive">
          <div className="message success" style={{ whiteSpace: 'pre-wrap' }}>
            ✓ {panel?.message}
            <br />
            Flag: {panel?.flag}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BACSecretPanelPage;
