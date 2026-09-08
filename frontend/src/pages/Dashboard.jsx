import { useState } from "react";
import { predictFlightPrice } from "../api/resource.api.js";
import { formatCurrency, pad2 } from "../utils/formatters.js";
import Loader from "../components/common/Loader.jsx";

const CARRIERS = ["AA", "DL", "UA", "US", "B6", "9E", "EV", "F9", "FL", "HA", "MQ", "OO", "VX", "WN", "YV", "AS"];
const ORIGINS = ["JFK", "LGA", "EWR"];

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

export default function Dashboard() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
    setResult(null);
    try {
      const response = await predictFlightPrice(form);
      setResult(response);
    } catch (err) {
      setError(err.message || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>Estimate a Fare</h1>
      <form className="predict-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Date
            <div className="form-row">
              <input type="number" name="year" min="2013" max="2035" value={form.year} onChange={handleChange} />
              <input type="number" name="month" min="1" max="12" value={form.month} onChange={handleChange} />
              <input type="number" name="day" min="1" max="31" value={form.day} onChange={handleChange} />
            </div>
          </label>

          <label>
            Departure time
            <div className="form-row">
              <input type="number" name="hour" min="0" max="23" value={form.hour} onChange={handleChange} />
              <span className="time-sep">:</span>
              <input type="number" name="minute" min="0" max="59" value={form.minute} onChange={handleChange} />
            </div>
          </label>

          <label>
            Carrier
            <select name="carrier" value={form.carrier} onChange={handleChange}>
              {CARRIERS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>

          <label>
            Origin
            <select name="origin" value={form.origin} onChange={handleChange}>
              {ORIGINS.map((o) => (
                <option key={o} value={o}>{o}</option>
              ))}
            </select>
          </label>

          <label>
            Destination (3-letter code)
            <input type="text" name="dest" maxLength={3} value={form.dest} onChange={handleChange} />
          </label>

          <label>
            Distance (miles)
            <input type="number" name="distance" min="1" max="3000" value={form.distance} onChange={handleChange} />
          </label>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Predicting…" : "Predict price"}
        </button>
      </form>

      {loading && <Loader label="Scoring flight…" />}

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="result-card">
          <div className="result-price">{formatCurrency(result.predicted_price, result.currency)}</div>
          <div className="result-meta">
            {form.origin} → {form.dest.toUpperCase()} · {form.carrier} · {pad2(form.hour)}:{pad2(form.minute)}
          </div>
          <div className="result-model">Model: {result.model_used}</div>
        </div>
      )}
    </div>
  );
}
