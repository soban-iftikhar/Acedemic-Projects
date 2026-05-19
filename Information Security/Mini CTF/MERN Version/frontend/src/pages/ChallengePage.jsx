import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { challengesAPI } from '../api/client';
import { authAPI } from '../api/client';
import SQLiChallenge from '../components/challenges/SQLiChallenge';
import IDORChallenge from '../components/challenges/IDORChallenge';
import XSSChallenge from '../components/challenges/XSSChallenge';
import BACChallenge from '../components/challenges/BACChallenge';
import HashChallenge from '../components/challenges/HashChallenge';
import RSAChallenge from '../components/challenges/RSAChallenge';
import BruteforceChallenge from '../components/challenges/BruteforceChallenge';
import DiffieChallenge from '../components/challenges/DiffieChallenge';
import VigenereChallenge from '../components/challenges/VigenereChallenge';
import CryptoChallenge from '../components/challenges/CryptoChallenge';
import CaesarChallenge from '../components/challenges/CaesarChallenge';
import './ChallengePage.css';

const CHALLENGE_COMPONENTS = {
  sqli: SQLiChallenge,
  idor: IDORChallenge,
  xss: XSSChallenge,
  bac: BACChallenge,
  hash: HashChallenge,
  rsa: RSAChallenge,
  bruteforce: BruteforceChallenge,
  diffie: DiffieChallenge,
  vigenere: VigenereChallenge,
  caesar: CaesarChallenge,
  crypto: CryptoChallenge
};

function ChallengePage({ user, setUser }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [challenge, setChallenge] = useState(null);
  const [flag, setFlag] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [solvedResult, setSolvedResult] = useState(null);

  useEffect(() => {
    const fetchChallenge = async () => {
      try {
        const response = await challengesAPI.getChallenge(id);
        setChallenge(response.data);
      } catch (err) {
        setMessage('Challenge not found');
        setMessageType('error');
      } finally {
        setLoading(false);
      }
    };

    fetchChallenge();
  }, [id]);

  const handleSubmitFlag = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');
    setSolvedResult(null);

    try {
      const response = await challengesAPI.submitFlag(id, flag);
      
      if (response.data.success) {
        const solvedFlag = response.data.flag ? ` Flag: ${response.data.flag}` : '';
        const pointsText = response.data.alreadySolved
          ? 'No extra points for repeat submissions.'
          : `You earned ${response.data.points} points!`;
        setMessage(`Correct! ${pointsText}${solvedFlag}`);
        setMessageType('success');
        setFlag('');
        setSolvedResult({
          flag: response.data.flag,
          points: response.data.points,
          totalPoints: response.data.totalPoints,
          firstBlood: response.data.firstBlood,
          alreadySolved: response.data.alreadySolved
        });

        if (setUser) {
          try {
            const currentUserResponse = await authAPI.getCurrentUser();
            setUser(currentUserResponse.data);
          } catch (refreshErr) {
            console.error('Failed to refresh user session:', refreshErr);
          }
        }
      } else {
        setMessage('Flag is incorrect. Try again!');
        setMessageType('error');
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Submission failed';
      setMessage(errorMsg);
      setMessageType('error');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="challenge-container"><div className="loading">Loading challenge...</div></div>;
  }

  if (!challenge) {
    return <div className="challenge-container"><div className="error-message">Challenge not found</div></div>;
  }

  const ChallengeComponent = CHALLENGE_COMPONENTS[id];

  return (
    <div className="challenge-container">
      <div className="challenge-header">
        <button className="back-btn" onClick={() => navigate('/dashboard')}>← Back</button>
        <h1>{challenge.name}</h1>
        <div className="challenge-meta">
          <span className="difficulty">{challenge.difficulty}</span>
          <span className="points">{challenge.points} points</span>
        </div>
      </div>

      <div className="challenge-content">
        <div className="challenge-description">
          <h2>Description</h2>
          <p>{challenge.description}</p>
        </div>

        <div className="challenge-interactive">
          {ChallengeComponent && <ChallengeComponent challenge={challenge} />}
        </div>

        <div className="flag-submission">
          <h2>Submit Flag</h2>
          <form onSubmit={handleSubmitFlag}>
            <div className="form-group">
              <label>Flag</label>
              <input
                type="text"
                value={flag}
                onChange={(e) => setFlag(e.target.value)}
                placeholder="Enter the flag (e.g., flag{...})"
                required
              />
            </div>

            {message && (
              <div className={`message ${messageType}`}>
                {messageType === 'success' && '✓ '}{messageType === 'error' && '✗ '}{message}
              </div>
            )}

            {solvedResult && messageType === 'success' && (
              <div className="message success" style={{ marginTop: '12px' }}>
                <div><strong>Submitted flag:</strong> {solvedResult.flag}</div>
                <div><strong>Points earned:</strong> {solvedResult.points}</div>
                <div><strong>Total points:</strong> {solvedResult.totalPoints}</div>
                {solvedResult.firstBlood && <div><strong>First blood!</strong></div>}
              </div>
            )}

            <button type="submit" className="submit-btn" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Flag'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChallengePage;
