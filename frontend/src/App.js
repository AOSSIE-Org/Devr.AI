import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { fetchWelcomeMessage, triggerTestEvent } from './services/api';

function App() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    // Fetch welcome message when component mounts
    const getWelcomeMessage = async () => {
      try {
        setLoading(true);
        const data = await fetchWelcomeMessage();
        setMessage(data.message);
      } catch (err) {
        setError('Failed to connect to the backend server');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getWelcomeMessage();
  }, []);

  const handleTestEvent = async () => {
    try {
      const result = await triggerTestEvent();
      setTestResult(result);
    } catch (err) {
      setError('Failed to trigger test event');
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        
        {loading ? (
          <p>Connecting to backend...</p>
        ) : error ? (
          <div>
            <p className="error">{error}</p>
            <p>Make sure your backend server is running at http://localhost:8000</p>
          </div>
        ) : (
          <div>
            <p>Backend says: {message}</p>
            <button onClick={handleTestEvent} className="App-button">
              Trigger Test Event
            </button>
            {testResult && (
              <div className="test-result">
                <p>Event ID: {testResult.event_id}</p>
                <p>{testResult.message}</p>
              </div>
            )}
          </div>
        )}
        
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
