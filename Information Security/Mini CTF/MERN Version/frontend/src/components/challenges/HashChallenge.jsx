import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function HashChallenge({ challenge }) {
  const [guess, setGuess] = useState('');
  const [result, setResult] = useState('');
  const [revealed, setRevealed] = useState(false);

  const md5Hash = '5f4dcc3b5aa765d61d8327deb882cf99';
  const acceptedAnswers = ['p', 'a', 's', 's', 'w', 'o', 'r', 'd', '1', '2', '3'].join('');

  const handleRevealHash = (e) => {
    e.preventDefault();
    setRevealed(true);
  };

  const handleCheckHash = (e) => {
    e.preventDefault();
    
    // Check if the guess matches the correct answer
    if (guess.toLowerCase() === acceptedAnswers || guess.toLowerCase() === 'password') {
      setResult(`✓ Correct! You successfully cracked the MD5 hash!\n\nFlag: ${CHALLENGE_FLAGS.hash}`);
    } else {
      setResult('✗ Incorrect. Use MD5 online tools or wordlist attacks to crack it.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>Hash Cracking</h3>
      <p>A user's password has been hashed using MD5. Crack the hash to recover the original password.</p>
      
      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleRevealHash} style={{ marginBottom: '16px' }}>
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
            Reveal Hash
          </button>
        </form>

        {revealed && (
          <div style={{
            padding: '12px',
            backgroundColor: '#fef3c7',
            color: '#92400e',
            borderRadius: '6px',
            border: '1px solid #fde68a',
            fontFamily: 'monospace',
            fontSize: '13px',
            wordBreak: 'break-all'
          }}>
            MD5 Hash: {md5Hash}
          </div>
        )}
      </div>

      <form onSubmit={handleCheckHash} style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Your Guess</label>
          <input
            type="text"
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder="Enter the cracked password"
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
          Check Guess
        </button>
      </form>

      {result && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          backgroundColor: result.includes('Correct') ? '#d1fae5' : '#fee2e2',
          color: result.includes('Correct') ? '#065f46' : '#7f1d1d',
          borderRadius: '6px',
          border: `1px solid ${result.includes('Correct') ? '#a7f3d0' : '#fecaca'}`
        }}>
          {result}
        </div>
      )}

      <div style={{ marginTop: '20px', padding: '12px', backgroundColor: '#f0f9ff', borderRadius: '6px' }}>
        <strong>Hint:</strong> The hash has a familiar shape, so the original word is likely something ordinary.
      </div>
    </div>
  );
}

export default HashChallenge;
