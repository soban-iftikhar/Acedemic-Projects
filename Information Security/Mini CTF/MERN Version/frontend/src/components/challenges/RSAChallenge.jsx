import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function RSAChallenge({ challenge }) {
  const [sharedSecret, setSharedSecret] = useState('');
  const [revealed, setRevealed] = useState(false);
  const [result, setResult] = useState('');
  const [showHint, setShowHint] = useState(false);

  const expectedPlaintext = ['6', '7', '3', '2'].join('');

  const handleRevealParams = (e) => {
    e.preventDefault();
    setRevealed(true);
  };

  const handleCheckSecret = (e) => {
    e.preventDefault();

    const normalizedInput = sharedSecret.trim().toLowerCase();
    const digitsOnly = normalizedInput.replace(/[^0-9]/g, '');
    const isCorrect = normalizedInput === expectedPlaintext || digitsOnly === expectedPlaintext;

    if (isCorrect) {
      setResult(`✓ Correct! You successfully decrypted the RSA message!\n\nFlag: ${CHALLENGE_FLAGS.rsa}`);
    } else {
      setResult('✗ Incorrect. Use RSA decryption math with the given parameters.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>RSA Decryption</h3>
      <p>You have intercepted RSA encrypted communications. The public key uses small prime factors making it vulnerable to factorization.</p>
      
      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleRevealParams} style={{ marginBottom: '16px' }}>
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
            Reveal RSA Parameters
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
            fontSize: '12px',
            whiteSpace: 'pre-wrap'
          }}>
{`Public Key (n, e):
n = 21889
e = 17

Encrypted Message (c): 4892

RSA Parameters:
p = 139
q = 157
Encrypted: 4892

The structure is weak enough that the private side can be reconstructed from the public side.`}
          </div>
        )}
      </div>

      <form onSubmit={handleCheckSecret} style={{ marginTop: '20px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Decrypted Message</label>
          <input
            type="text"
            value={sharedSecret}
            onChange={(e) => setSharedSecret(e.target.value)}
            placeholder="Enter the decrypted message"
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
            <p style={{ marginTop: '8px', marginBottom: '8px' }}>When the primes are small, the hidden message becomes less hidden.</p>
            <p style={{ marginTop: '8px' }}>Reconstruct the missing private piece from the public parameters, then decode the ciphertext.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default RSAChallenge;
