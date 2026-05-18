import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function CaesarChallenge({ challenge }) {
  const [guess, setGuess] = useState('');
  const [revealed, setRevealed] = useState(false);
  const [result, setResult] = useState('');
  const [showHint, setShowHint] = useState(false);

  const expectedAnswer = ['L', 'a', 'b', ' ', 'T', 'e', 'r', 'm', 'i', 'n', 'a', 'l'].join('');

  const handleRevealCiphertext = (e) => {
    e.preventDefault();
    setRevealed(true);
  };

  const handleCheckGuess = (e) => {
    e.preventDefault();

    const normalizedGuess = guess.trim().toLowerCase();
    if (normalizedGuess === expectedAnswer.toLowerCase()) {
      setResult(`✓ Correct! You recovered the hidden phrase.\n\nFlag: ${CHALLENGE_FLAGS.caesar}`);
    } else {
      setResult('✗ Not quite. The message was shifted by a fixed amount.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>Caesar Cipher</h3>
      <p>A short phrase was shifted by 7 positions. Recover the original text.</p>

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
            Unseal Note
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
            Ciphertext: Shi Alytpuhs
          </div>
        )}
      </div>

      <form onSubmit={handleCheckGuess} style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Decrypted Phrase</label>
          <input
            type="text"
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder="Recover the original phrase"
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
            <p style={{ marginTop: '8px', marginBottom: '8px' }}>A fixed shift hides the message. Try moving each letter backward by seven.</p>
            <p style={{ marginTop: '8px' }}>If you recover a normal phrase, that is the answer to submit.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default CaesarChallenge;