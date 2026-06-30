import { useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!input) return;

    setLoading(true);
    setResult("");

    try {
      const response = await fetch("http://127.0.0.1:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          sql: input
        })
      });

      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setResult("Error: Backend not connected");
    }

    setLoading(false);
  };

  return (
    <div className="page">

      <div className="header">
        <h1>Query Engine Dashboard</h1>
        <span className="badge">v1.0</span>
      </div>

      <div className="card">
        <h2>Ask a Question</h2>

        <div className="row">
          <input
            type="text"
            placeholder="Type your query..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <button onClick={handleSubmit} disabled={loading}>
            {loading ? "Running..." : "Submit"}
          </button>
        </div>
      </div>

      <div className="card">
        <h2>Result</h2>
        <p className="resultText">
          {result || "No result yet..."}
        </p>
      </div>

    </div>
  );
}

export default App;