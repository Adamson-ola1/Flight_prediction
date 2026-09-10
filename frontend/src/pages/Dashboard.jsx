import { useEffect, useMemo, useState } from "react";
import { predictFlightPrice } from "../api/resource.api.js";
import { formatCurrency, pad2 } from "../utils/formatters.js";
import Loader from "../components/common/Loader.jsx";

const CARRIERS = ["AA", "DL", "UA", "US", "B6", "9E", "EV", "F9", "FL", "HA", "MQ", "OO", "VX", "WN", "YV", "AS"];
const ORIGINS = ["JFK", "LGA", "EWR"];
const HISTORY_KEY = "flight_price_prediction_history";

const initialForm = {
  year: 2013,
  month: 7,
  day: 19,
  hour: 8,
  minute: 30,
  carrier: "DL",
  origin: "JFK",
  dest: "LAX",
  distance: 2475,
};

function loadHistory() {
  try {
    const saved = localStorage.getItem(HISTORY_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function formatDate(form) {
  return `${form.year}-${String(form.month).padStart(2, "0")}-${String(form.day).padStart(2, "0")}`;
}

function formatTime(form) {
  return `${pad2(form.hour)}:${pad2(form.minute)}`;
}

export default function Dashboard() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState(loadHistory);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  }, [history]);

  const latestPrediction = useMemo(() => history[history.length - 1] || null, [history]);

  function handleChange(e) {
    const { name, value } = e.target;
    const numericFields = ["year", "month", "day", "hour", "minute", "distance"];
    setForm((prev) => ({
      ...prev,
      [name]: numericFields.includes(name) ? Number(value) : value.toUpperCase(),
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await predictFlightPrice(form);
      setResult(response);

      const prediction = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        createdAt: new Date().toISOString(),
        form: { ...form },
        response,
      };

      // Keep chronological order so the first prediction remains #1, second remains #2, and so on.
      setHistory((prev) => [...prev, prediction]);
    } catch (err) {
      setError(err.message || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  }

  function clearHistory() {
    setHistory([]);
    setResult(null);
    localStorage.removeItem(HISTORY_KEY);
  }

  function removePrediction(id) {
    setHistory((prev) => prev.filter((item) => item.id !== id));
  }

  return (
    <div className="page prediction-page">
      <section className="page-hero">
        <div>
          <span className="eyebrow">AI-POWERED FARE ESTIMATION</span>
          <h1>Flight Fare Predictor</h1>
          <p>Estimate a flight fare with the trained regression pipeline, then keep every prediction for comparison.</p>
        </div>
        <div className="hero-route" aria-hidden="true">
          <span>✈</span>
          <div className="route-line" />
          <span>◉</span>
        </div>
      </section>

      <div className="prediction-layout">
        <section className="panel form-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">01</span>
              <h2>Flight details</h2>
            </div>
            <span className="panel-icon">✈</span>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="field-section">
              <h3>Route</h3>
              <div className="field-grid two-columns">
                <label>
                  <span>Origin</span>
                  <select name="origin" value={form.origin} onChange={handleChange}>
                    {ORIGINS.map((origin) => <option key={origin} value={origin}>{origin}</option>)}
                  </select>
                </label>
                <label>
                  <span>Destination</span>
                  <input type="text" name="dest" maxLength={3} value={form.dest} onChange={handleChange} placeholder="LAX" required />
                </label>
              </div>
            </div>

            <div className="field-section">
              <h3>Airline & distance</h3>
              <div className="field-grid two-columns">
                <label>
                  <span>Carrier</span>
                  <select name="carrier" value={form.carrier} onChange={handleChange}>
                    {CARRIERS.map((carrier) => <option key={carrier} value={carrier}>{carrier}</option>)}
                  </select>
                </label>
                <label>
                  <span>Distance (miles)</span>
                  <input type="number" name="distance" min="1" max="3000" value={form.distance} onChange={handleChange} required />
                </label>
              </div>
            </div>

            <div className="field-section">
              <h3>Departure</h3>
              <label>
                <span>Date</span>
                <div className="date-grid">
                  <input type="number" name="day" min="1" max="31" value={form.day} onChange={handleChange} aria-label="Day" required />
                  <select name="month" value={form.month} onChange={handleChange} aria-label="Month">
                    {[
                      "January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December",
                    ].map((month, index) => <option key={month} value={index + 1}>{month}</option>)}
                  </select>
                  <input type="number" name="year" min="2013" max="2035" value={form.year} onChange={handleChange} aria-label="Year" required />
                </div>
              </label>
              <label className="time-field">
                <span>Departure time</span>
                <div className="time-grid">
                  <input type="number" name="hour" min="0" max="23" value={form.hour} onChange={handleChange} aria-label="Hour" required />
                  <strong>:</strong>
                  <input type="number" name="minute" min="0" max="59" value={form.minute} onChange={handleChange} aria-label="Minute" required />
                </div>
              </label>
            </div>

            <button type="submit" className="predict-button" disabled={loading}>
              {loading ? "Predicting…" : "✈  Predict fare"}
            </button>
          </form>

          {loading && <Loader label="Scoring flight…" />}
          {error && <div className="alert alert-error">{error}</div>}
        </section>

        <section className="panel result-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">02</span>
              <h2>Estimated fare</h2>
            </div>
            <span className="live-badge">MODEL READY</span>
          </div>

          {result ? (
            <div className="result-content">
              <div className="price-label">PREDICTED TICKET PRICE</div>
              <div className="result-price">{formatCurrency(result.predicted_price, result.currency)}</div>
              <div className="currency-note">{result.currency} · model estimate</div>

              <div className="route-display">
                <div><strong>{form.origin}</strong><span>Origin</span></div>
                <div className="route-arrow">→</div>
                <div><strong>{form.dest.toUpperCase()}</strong><span>Destination</span></div>
              </div>

              <div className="result-details">
                <div><span>Carrier</span><strong>{form.carrier}</strong></div>
                <div><span>Departure</span><strong>{formatDate(form)} · {formatTime(form)}</strong></div>
                <div><span>Distance</span><strong>{Number(form.distance).toLocaleString()} mi</strong></div>
                <div><span>Model used</span><strong>{result.model_used}</strong></div>
              </div>

              <div className="success-message">✓ Prediction completed successfully</div>
            </div>
          ) : (
            <div className="empty-result">
              <div className="empty-plane">✈</div>
              <h3>Your fare estimate will appear here</h3>
              <p>Enter your flight details and select <strong>Predict fare</strong> to generate an estimate.</p>
            </div>
          )}
        </section>
      </div>

      <section className="stats-strip">
        <div><span>Predictions saved</span><strong>{history.length}</strong></div>
        <div><span>Latest route</span><strong>{latestPrediction ? `${latestPrediction.form.origin} → ${latestPrediction.form.dest}` : "—"}</strong></div>
        <div><span>Storage</span><strong>Browser history</strong></div>
      </section>

      <section className="history-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">03 · PREDICTION HISTORY</span>
            <h2>Saved fare predictions</h2>
            <p>Every successful prediction is retained in this browser, from the first flight to the latest one.</p>
          </div>
          {history.length > 0 && <button type="button" className="clear-button" onClick={clearHistory}>Clear history</button>}
        </div>

        {history.length === 0 ? (
          <div className="history-empty">No predictions saved yet. Your first prediction will appear here.</div>
        ) : (
          <div className="history-table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Route</th>
                  <th>Carrier</th>
                  <th>Departure</th>
                  <th>Distance</th>
                  <th>Model</th>
                  <th>Predicted fare</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {history.map((item, index) => (
                  <tr key={item.id}>
                    <td><span className="history-number">{index + 1}</span></td>
                    <td><strong>{item.form.origin} → {item.form.dest}</strong></td>
                    <td>{item.form.carrier}</td>
                    <td>{formatDate(item.form)} · {formatTime(item.form)}</td>
                    <td>{Number(item.form.distance).toLocaleString()} mi</td>
                    <td><span className="model-chip">{item.response.model_used}</span></td>
                    <td className="history-price">{formatCurrency(item.response.predicted_price, item.response.currency)}</td>
                    <td><button type="button" className="remove-button" onClick={() => removePrediction(item.id)} aria-label={`Remove prediction ${index + 1}`}>×</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
