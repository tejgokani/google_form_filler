import React, { useState } from "react";

function App() {
  const [formUrl, setFormUrl] = useState("");
  const [numResponses, setNumResponses] = useState(1);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("Generating responses...");
    try {
      const res = await fetch("http://127.0.0.1:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ formUrl, numResponses }),
      });
      const data = await res.json();
      setMessage(data.message);
    } catch (err) {
      setMessage("Error generating responses.");
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: "auto", padding: 32 }}>
      <h1>Fake Google Form Response Generator</h1>
      {/* Red warning message */}
      <div style={{ color: "red", marginBottom: 20, fontWeight: "bold" }}>
        Note: Responses will be generated with a gap of 30-45 seconds between each submission to match the response sheet’s timestamps.
      </div>
      <form onSubmit={handleSubmit}>
        <label>
          Google Form URL:
          <input
            type="text"
            value={formUrl}
            onChange={(e) => setFormUrl(e.target.value)}
            style={{ width: "100%", marginBottom: 8 }}
            required
          />
        </label>
        <label>
          Number of Responses:
          <input
            type="number"
            min={1}
            max={50}
            value={numResponses}
            onChange={(e) => setNumResponses(e.target.value)}
            style={{ width: "100%", marginBottom: 16 }}
            required
          />
        </label>
        <button type="submit">Generate Fake Responses</button>
      </form>
      <div style={{ marginTop: 24 }}>{message}</div>
    </div>
  );
}

export default App;