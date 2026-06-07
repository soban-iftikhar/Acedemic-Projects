 import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function CryptoChallenge({ challenge }) {
  const [revealed, setRevealed] = useState(false);
  const [guess, setGuess] = useState('');
  const [result, setResult] = useState('');
  const [showHint, setShowHint] = useState(false);
  const rot13 = (str) => {
    return str.replace(/[a-zA-Z]/g, function(c) {
      return String.fromCharCode((c <= 'Z' ? 90 : 122) >= (c = c.charCodeAt(0) + 13) ? c : c - 26);
    });
  };

  const encrypted = 'Gur dhvpx oebja sbk whzcf bire gur ynml qbt';
  const expectedPlaintext = rot13(encrypted);

  const handleRevealEncrypted = (e) => {
    e.preventDefault();
    setRevealed(true);
  };

  const handleCheckGuess = (e) => {
    e.preventDefault();
    const normalize = (s) => s.replace(/\s+/g, ' ').trim().toLowerCase();
    const normalizedGuess = normalize(guess);
    const normalizedExpected = normalize(expectedPlaintext);

    if (normalizedGuess === normalizedExpected) {
      setResult(`✓ Correct! You successfully decrypted the ROT13 message!\n\nFlag: ${CHALLENGE_FLAGS.crypto}`);
    } else {
      setResult('✗ Incorrect. ROT13 shifts each letter by 13 positions.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>ROT13 Decryption</h3>
      <p>Decrypt a message that has been encrypted using ROT13 cipher (a simple substitution cipher).</p>
      
      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleRevealEncrypted} style={{ marginBottom: '16px' }}>
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
            Reveal Encrypted Message
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
            fontSize: '13px'
          }}>
            Encrypted (ROT13): {encrypted}
          </div>
        )}
      </div>

      <form onSubmit={handleCheckGuess} style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Decrypted Message</label>
          <input
            type="text"
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder="Decrypt the ROT13 message"
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
          Check Answer
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
            <p style={{ marginTop: '8px', marginBottom: '8px' }}>This message is shifted by a fixed amount, and the same trick can undo it.</p>
            <p style={{ marginTop: '8px' }}>Look for a Caesar-style substitution hiding in plain sight.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default CryptoChallenge;
