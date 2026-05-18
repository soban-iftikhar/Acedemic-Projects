import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function BruteforceChallenge({ challenge }) {
  const [password, setPassword] = useState('');
  const [result, setResult] = useState('');
  const [wordlist, setWordlist] = useState(false);

  const commonPasswords = ['password', 'admin', '123456', 'letmein', 'welcome'];
  const targetPassword = ['a', 'd', 'm', 'i', 'n', '1', '2', '3'].join('');

  const handleRevealWordlist = (e) => {
    e.preventDefault();
    setWordlist(true);
  };

  const handleCheckPassword = (e) => {
    e.preventDefault();
    
    if (password.toLowerCase() === targetPassword) {
      setResult(`✓ Password is correct! You successfully brute-forced the admin password!\n\nFlag: ${CHALLENGE_FLAGS.bruteforce}`);
    } else if (commonPasswords.includes(password)) {
      setResult('✓ Close! That password is in the wordlist but it\'s not the admin password.');
    } else {
      setResult('✗ Password not found. Try using passwords from the wordlist.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>Brute Force Attack</h3>
      <p>The admin account lacks proper rate limiting. Brute force the admin password using a wordlist.</p>
      
      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleRevealWordlist} style={{ marginBottom: '16px' }}>
          <button type="submit" style={{ 
            padding: '8px 16px', 
            backgroundColor: '#f59e0b', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            Load Wordlist
          </button>
        </form>

        {wordlist && (
          <div style={{
            padding: '12px',
            backgroundColor: '#fef3c7',
            color: '#92400e',
            borderRadius: '6px',
            border: '1px solid #fde68a',
            fontFamily: 'monospace',
            fontSize: '12px',
            maxHeight: '150px',
            overflowY: 'auto'
          }}>
            {commonPasswords.map((pwd, idx) => (
              <div key={idx}>{pwd}</div>
            ))}
            <div>one entry feels more likely than the others</div>
            <div>the weak link is the one people reuse</div>
          </div>
        )}
      </div>

      <form onSubmit={handleCheckPassword} style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Admin Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Try passwords from the wordlist"
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
          Try Password
        </button>
      </form>

      {result && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          backgroundColor: result.includes('correct') ? '#d1fae5' : '#fee2e2',
          color: result.includes('correct') ? '#065f46' : '#7f1d1d',
          borderRadius: '6px',
          border: `1px solid ${result.includes('correct') ? '#a7f3d0' : '#fecaca'}`
        }}>
          {result}
        </div>
      )}

      <div style={{ marginTop: '20px', padding: '12px', backgroundColor: '#f0f9ff', borderRadius: '6px' }}>
        <strong>Hint:</strong> Weak passwords tend to follow familiar habits, especially when no lockout slows you down.
      </div>
    </div>
  );
}

export default BruteforceChallenge;
