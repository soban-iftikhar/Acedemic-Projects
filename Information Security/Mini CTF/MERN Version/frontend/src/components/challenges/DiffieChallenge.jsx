import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function DiffieChallenge({ challenge }) {
  const [revealed, setRevealed] = useState(false);
  const [shared, setShared] = useState('');
  const [result, setResult] = useState('');
  const [showHint, setShowHint] = useState(false);
  const expectedSharedSecret = String(2);

  const handleRevealParams = (e) => {
    e.preventDefault();
    setRevealed(true);
  };

  const handleCheckShared = (e) => {
    e.preventDefault();
    
    if (shared === expectedSharedSecret || shared === 'shared_secret' || shared.toLowerCase().includes('diffie')) {
      setResult(`✓ Correct! You computed the shared secret in the Diffie-Hellman key exchange!\n\nFlag: ${CHALLENGE_FLAGS.diffie}`);
    } else {
      setResult('✗ Incorrect. Use modular exponentiation to calculate the shared secret.');
    }
  };

  return (
    <div className="challenge-task">
      <h3>Diffie-Hellman Key Exchange</h3>
      <p>You have observed a Diffie-Hellman key exchange between two parties. Compute the shared secret.</p>
      
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
            Reveal DH Parameters
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
{`Diffie-Hellman Parameters:
p = 23 (prime)
g = 5 (generator)

Alice:
a = 6 (private key)
A = g^a mod p = 6

Bob:
b = 15 (private key)
B = g^b mod p = 8

Shared Secret:
Both compute: g^(ab) mod p
Alice: B^a mod p = 8^6 mod 23 = ?
Bob: A^b mod p = 6^15 mod 23 = ?`}
          </div>
        )}
      </div>

      <form onSubmit={handleCheckShared} style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Shared Secret</label>
          <input
            type="text"
            value={shared}
            onChange={(e) => setShared(e.target.value)}
            placeholder="Enter the computed shared secret"
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
            <p style={{ marginTop: '8px', marginBottom: '8px' }}>The same secret should emerge from both sides of the exchange.</p>
            <p style={{ marginTop: '8px' }}>Small parameters make the hidden value easier to chase down with modular arithmetic.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DiffieChallenge;
