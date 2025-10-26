import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [formUrl, setFormUrl] = useState("");
  const [numResponses, setNumResponses] = useState(1);
  const [intervalMinutes, setIntervalMinutes] = useState(0);
  const [intervalSeconds, setIntervalSeconds] = useState(5);
  const [formContext, setFormContext] = useState("");
  const [responseTone, setResponseTone] = useState("positive");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState(0);
  const [progress, setProgress] = useState(0);

  // Simulate progress updates (since backend doesn't send real-time updates)
  useEffect(() => {
    if (isLoading && currentResponse < numResponses) {
      // Calculate estimated time based on user's interval selection
      const estimatedTimePerResponse = (intervalMinutes * 60 + intervalSeconds) * 1000; // milliseconds
      const timer = setTimeout(() => {
        setCurrentResponse((prev) => prev + 1);
        setProgress(((currentResponse + 1) / numResponses) * 100);
      }, estimatedTimePerResponse);

      return () => clearTimeout(timer);
    }
  }, [isLoading, currentResponse, numResponses, intervalMinutes, intervalSeconds]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsLoading(true);
    setCurrentResponse(0);
    setProgress(0);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || "http://127.0.0.1:5002";
      const res = await fetch(`${apiUrl}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          formUrl, 
          numResponses,
          intervalMinutes,
          intervalSeconds,
          formContext,
          responseTone
        }),
      });
      const data = await res.json();
      setMessage(data.message);
      setIsLoading(false);
      setCurrentResponse(numResponses);
      setProgress(100);
    } catch (err) {
      setMessage("⚠️ Error generating responses. Check console for details.");
      setIsLoading(false);
      console.error(err);
    }
  };

  return (
    <div className="app-container">
      {/* Animated background */}
      <div className="cyber-grid"></div>
      <div className="glow-orb glow-orb-1"></div>
      <div className="glow-orb glow-orb-2"></div>

      <div className="content-wrapper">
        {/* Header */}
        <div className="header">
          <div className="glitch-wrapper">
            <h1 className="glitch" data-text="FORM FILLER">
              FORM FILLER
            </h1>
          </div>
          <p className="subtitle">AUTOMATED RESPONSE GENERATOR v2.0</p>
        </div>

        {/* Warning Banner */}
        <div className="warning-banner">
          <span className="warning-icon">⚠</span>
          <div className="warning-text">
            <strong>TIMING PROTOCOL:</strong> Custom interval of {intervalMinutes > 0 ? `${intervalMinutes}m ` : ''}{intervalSeconds}s between submissions
          </div>
        </div>

        {/* Main Form */}
        <form onSubmit={handleSubmit} className="cyber-form">
          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">🔗</span>
              TARGET URL
            </label>
            <input
              type="text"
              value={formUrl}
              onChange={(e) => setFormUrl(e.target.value)}
              className="cyber-input"
              placeholder="https://docs.google.com/forms/..."
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">📊</span>
              RESPONSE COUNT
            </label>
            <input
              type="number"
              min={1}
              max={50}
              value={numResponses}
              onChange={(e) => setNumResponses(parseInt(e.target.value))}
              className="cyber-input"
              required
              disabled={isLoading}
            />
            <div className="input-hint">Maximum: 50 responses</div>
          </div>

          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">⏱️</span>
              TIME INTERVAL BETWEEN RESPONSES
            </label>
            <div className="time-inputs">
              <div className="time-input-group">
                <input
                  type="number"
                  min={0}
                  max={5}
                  value={intervalMinutes}
                  onChange={(e) => setIntervalMinutes(parseInt(e.target.value) || 0)}
                  className="cyber-input time-input"
                  disabled={isLoading}
                />
                <span className="time-label">minutes</span>
              </div>
              <div className="time-input-group">
                <input
                  type="number"
                  min={0}
                  max={59}
                  value={intervalSeconds}
                  onChange={(e) => setIntervalSeconds(parseInt(e.target.value) || 0)}
                  className="cyber-input time-input"
                  disabled={isLoading}
                />
                <span className="time-label">seconds</span>
              </div>
            </div>
            <div className="input-hint">
              Total: {intervalMinutes}m {intervalSeconds}s per response (Max: 5 minutes)
            </div>
          </div>

          {/* AI Settings Toggle */}
          <div className="advanced-toggle" onClick={() => setShowAdvanced(!showAdvanced)}>
            <span className="toggle-icon">{showAdvanced ? '▼' : '▶'}</span>
            <span className="toggle-text">AI RESPONSE SETTINGS</span>
          </div>

          {/* AI Settings Panel */}
          {showAdvanced && (
            <div className="advanced-panel">
              <div className="form-group">
                <label className="form-label">
                  <span className="label-icon">📝</span>
                  FORM DESCRIPTION
                </label>
                <textarea
                  value={formContext}
                  onChange={(e) => setFormContext(e.target.value)}
                  className="cyber-input context-textarea"
                  placeholder="Describe this form... (e.g., 'Movie feedback survey about director preferences', 'Product satisfaction survey', etc.)"
                  rows={3}
                  disabled={isLoading}
                />
                <div className="input-hint">
                  Tell the AI what this form is about for better contextual responses
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span className="label-icon">🎭</span>
                  RESPONSE TONE
                </label>
                <div className="tone-selector">
                  <button
                    type="button"
                    className={`tone-btn ${responseTone === 'positive' ? 'active' : ''}`}
                    onClick={() => setResponseTone('positive')}
                    disabled={isLoading}
                  >
                    <span className="tone-icon">😊</span>
                    <span className="tone-label">Positive</span>
                  </button>
                  <button
                    type="button"
                    className={`tone-btn ${responseTone === 'neutral' ? 'active' : ''}`}
                    onClick={() => setResponseTone('neutral')}
                    disabled={isLoading}
                  >
                    <span className="tone-icon">�</span>
                    <span className="tone-label">Neutral</span>
                  </button>
                  <button
                    type="button"
                    className={`tone-btn ${responseTone === 'negative' ? 'active' : ''}`}
                    onClick={() => setResponseTone('negative')}
                    disabled={isLoading}
                  >
                    <span className="tone-icon">😞</span>
                    <span className="tone-label">Negative</span>
                  </button>
                  <button
                    type="button"
                    className={`tone-btn ${responseTone === 'mixed' ? 'active' : ''}`}
                    onClick={() => setResponseTone('mixed')}
                    disabled={isLoading}
                  >
                    <span className="tone-icon">🤔</span>
                    <span className="tone-label">Mixed</span>
                  </button>
                </div>
                <div className="input-hint">
                  Choose how AI should respond to questions (positive, negative, neutral, or mixed)
                </div>
              </div>
            </div>
          )}

          <button
            type="submit"
            className={`cyber-button ${isLoading ? "loading" : ""}`}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                PROCESSING...
              </>
            ) : (
              <>
                <span className="button-icon">⚡</span>
                INITIATE GENERATION
              </>
            )}
          </button>
        </form>

        {/* Loading Progress */}
        {isLoading && (
          <div className="loading-container">
            <div className="progress-info">
              <span className="progress-label">GENERATING RESPONSES</span>
              <span className="progress-count">
                {currentResponse}/{numResponses}
              </span>
            </div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${progress}%` }}
              >
                <div className="progress-shimmer"></div>
              </div>
            </div>
            <div className="loading-animation">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        )}

        {/* Success/Error Message */}
        {message && !isLoading && (
          <div
            className={`message-container ${
              message.includes("Error") || message.includes("⚠️") ? "error" : "success"
            }`}
          >
            <div className="message-icon">
              {message.includes("Error") || message.includes("⚠️") ? "❌" : "✓"}
            </div>
            <div className="message-text">{message}</div>
          </div>
        )}

        {/* Footer */}
        <div className="footer">
          <div className="footer-line"></div>
          <p className="footer-text">⚡ MADE WITH ❤️ ⚡</p>
        </div>
      </div>
    </div>
  );
}

export default App;