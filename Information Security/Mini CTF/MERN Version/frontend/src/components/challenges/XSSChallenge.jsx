import { useState } from 'react';
import { CHALLENGE_FLAGS } from '../../constants/challengeFlags';

function XSSChallenge({ challenge }) {
  const [message, setMessage] = useState('');
  const [result, setResult] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [messages, setMessages] = useState([]);

  const handlePostMessage = (e) => {
    e.preventDefault();
    
    // Check if message contains script tags (vulnerable to XSS)
    if (message.toLowerCase().includes('<script>') || message.toLowerCase().includes('onclick=') || message.toLowerCase().includes('onerror=')) {
      setResult(`✓ XSS Vulnerability Detected! Your script payload would execute and steal cookies!\n\nFlag: ${CHALLENGE_FLAGS.xss}`);
      setMessages([...messages, { text: message, isXSS: true }]);
    } else {
      setResult('✗ Message posted but no XSS detected. Try injecting JavaScript!');
      setMessages([...messages, { text: message, isXSS: false }]);
    }
    setMessage('');
  };

  return (
    <div className="challenge-task">
      <h3>Stored Cross-Site Scripting (XSS)</h3>
      <p>The message board doesn't properly sanitize user input. Try injecting JavaScript code to demonstrate an XSS vulnerability and steal user cookies.</p>
      
      <form onSubmit={handlePostMessage} style={{ marginTop: '20px' }}>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Post a Message</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Write something the browser might misread"
            style={{ 
              width: '100%', 
              padding: '8px', 
              border: '1px solid #ccc', 
              borderRadius: '4px',
              minHeight: '80px',
              fontFamily: 'monospace',
              fontSize: '13px'
            }}
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
          Post Message
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

      {messages.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h4>Message Board ({messages.length} messages)</h4>
          {messages.map((msg, idx) => (
            <div key={idx} style={{
              padding: '12px',
              marginBottom: '8px',
              backgroundColor: msg.isXSS ? '#fef3c7' : '#f3f4f6',
              borderRadius: '6px',
              border: `1px solid ${msg.isXSS ? '#fde68a' : '#e5e7eb'}`,
              fontFamily: 'monospace',
              fontSize: '12px',
              color: '#333'
            }}>
              {msg.text}
            </div>
          ))}
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
            <p style={{ marginTop: '8px', marginBottom: '8px' }}>The board seems to trust HTML more than it should.</p>
            <p style={{ marginTop: '8px' }}>Think about what happens when the browser is asked to interpret your message instead of just showing it.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default XSSChallenge;
