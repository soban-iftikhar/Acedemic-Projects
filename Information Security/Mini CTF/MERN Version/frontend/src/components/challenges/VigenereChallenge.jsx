import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function VigenereChallenge({ challenge }) {
  const [ciphertext, setCiphertext] = useState('');
  const [plaintext, setPlaintext] = useState('');
  const [revealed, setRevealed] = useState(false);
  const [result, setResult] = useState('');
  const [showHint, setShowHint] = useState(false);
  const expectedPlaintext = ['C', 'R', 'Y', 'P', 'T', 'O', 'G', 'R', 'A', 'P', 'H', 'Y'].join('');

  const handleRevealCiphertext = (e) => {
    e.preventDefault();
    setCiphertext('LXFOPVEFRNHR');
    setRevealed(true);
  };

  const handleCheckGuess = (e) => {
    e.preventDefault();
    
    if (plaintext.toUpperCase() === expectedPlaintext || plaintext.toLowerCase() === 'vigenere cipher decrypted') {
      setResult(`✓ Correct! You successfully decrypted the Vigenere cipher!\n\nFlag: ${CHALLENGE_FLAGS.vigenere}`);
    } else {
      setResult('✗ Incorrect. Try using frequency analysis or a Vigenere cracker tool.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>Vigenere Cipher Decryption</h3>
      <p>Decrypt a message encrypted with the Vigenere cipher. You have the ciphertext and need to find the key.</p>
      
      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleRevealCiphertext} style={{ marginBottom: '16px' }}>
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
            Reveal Ciphertext
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
            fontSize: '14px'
          }}>
            Ciphertext: {ciphertext}
          </div>
        )}
      </div>

      <form onSubmit={handleCheckGuess} style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Decrypted Message</label>
          <input
            type="text"
            value={plaintext}
            onChange={(e) => setPlaintext(e.target.value)}
            placeholder="Decrypt the message"
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
            <p style={{ marginTop: '8px', marginBottom: '8px' }}>A repeating key is hiding the pattern here.</p>
            <p style={{ marginTop: '8px' }}>Try to spot where the rhythm of the text starts to repeat, then let that guide the rest.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default VigenereChallenge;
