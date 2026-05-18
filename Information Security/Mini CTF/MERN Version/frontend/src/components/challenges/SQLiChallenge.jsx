import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function SQLiChallenge({ challenge }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [result, setResult] = useState('');
  const [showHint, setShowHint] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    
    // Vulnerable login check for demonstration
    if (username.includes("'") && (username.includes('--') || username.includes('/*'))) {
      setResult(`✓ Login bypass detected! You successfully exploited the SQL injection vulnerability!\n\nFlag: ${CHALLENGE_FLAGS.sqli}`);
    } else if (username.includes("'") || username.includes('--')) {
      setResult(`✓ Getting closer! You are on the right track with SQL injection.\n\nFlag: ${CHALLENGE_FLAGS.sqli}`);
    } else {
      setResult('✗ Login failed. Try using SQL injection techniques to bypass authentication.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>Vulnerable Login Form</h3>
      <p>Try to bypass this login form using SQL injection. The backend SQL query is vulnerable to injection attacks.</p>
      
      <form onSubmit={handleLogin} style={{ marginTop: '20px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter username"
            style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
            required
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
            style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
            required
          />
        </div>

        <button type="submit" style={{ 
          padding: '8px 16px', 
          backgroundColor: '#2563eb', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '500'
        }}>
          Login
        </button>
      </form>

      {result && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          backgroundColor: result.includes('✓') ? '#d1fae5' : '#fee2e2',
          color: result.includes('✓') ? '#065f46' : '#7f1d1d',
          borderRadius: '6px',
          border: `1px solid ${result.includes('✓') ? '#a7f3d0' : '#fecaca'}`
        }}>
          {result}
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <button 
          type="button" 
          onClick={() => setShowHint(!showHint)}
          style={{
            padding: '8px 12px',
            backgroundColor: '#f3f4f6',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: '500'
          }}
        >
          {showHint ? '▼ Hide Hint' : '▶ Show Hint'}
        </button>

        {showHint && (
          <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#fef3c7', borderRadius: '6px', borderLeft: '4px solid #f59e0b' }}>
            <strong>Hint:</strong>
            <p style={{ marginTop: '8px', marginBottom: '8px' }}>Sometimes a single character can change the meaning of a database query completely.</p>
            <p style={{ marginTop: '8px' }}>Look for places where user input might be stitched directly into a query without escaping.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default SQLiChallenge;
