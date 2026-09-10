import useFetch from "../hooks/useFetch.js";
import { getModelMetrics } from "../api/resource.api.js";
import { formatNumber, formatPercent } from "../utils/formatters.js";
import Loader from "../components/common/Loader.jsx";

export default function ModelInfo() {
  const { data, error, loading } = useFetch(getModelMetrics, []);

  if (loading) return <Loader label="Loading model metrics…" />;
  if (error) return <div className="alert alert-error">Could not load metrics: {error}</div>;
  if (!data) return null;

  const rows = Object.entries(data.leaderboard).sort((a, b) => a[1].RMSE - b[1].RMSE);

  return (
    <div className="page">
      <section className="page-hero">
        <div>
          <span className="eyebrow">MODEL EVALUATION</span>
          <h1>Model Performance</h1>
          <p>Five regression approaches are evaluated on held-out test flights. The lowest-RMSE model is selected for serving.</p>
        </div>
        <span className="live-badge">BEST · {data.best_model}</span>
      </section>

      <section className="panel form-panel">
        <div className="panel-heading">
          <div>
            <span className="panel-kicker">LEADERBOARD</span>
            <h2>Regression model comparison</h2>
          </div>
          <span className="panel-icon">◎</span>
        </div>
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr><th>Model</th><th>RMSE</th><th>MAE</th><th>R²</th><th>Status</th></tr>
            </thead>
            <tbody>
              {rows.map(([name, metrics]) => (
                <tr key={name}>
                  <td><strong>{name}</strong></td>
                  <td>{formatNumber(metrics.RMSE)}</td>
                  <td>{formatNumber(metrics.MAE)}</td>
                  <td>{formatPercent(metrics.R2)}</td>
                  <td>{name === data.best_model ? <span className="model-chip">Selected</span> : <span className="note">Candidate</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note" style={{ marginTop: 18 }}>
          Evaluated on {data.n_test_rows} held-out test flights. Lower RMSE/MAE and higher R² are better. The target price is synthetic, not observed ticket fare data.
        </p>
      </section>
    </div>
  );
}
