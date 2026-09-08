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
      <h1>Model Performance</h1>
      <p>
        Best model: <strong>{data.best_model}</strong> — evaluated on {data.n_test_rows}{" "}
        held-out test flights.
      </p>

      <table className="data-table">
        <thead>
          <tr>
            <th>Model</th>
            <th>RMSE</th>
            <th>MAE</th>
            <th>R²</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([name, metrics]) => (
            <tr key={name} className={name === data.best_model ? "best-row" : ""}>
              <td>{name}</td>
              <td>{formatNumber(metrics.RMSE)}</td>
              <td>{formatNumber(metrics.MAE)}</td>
              <td>{formatPercent(metrics.R2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="note">
        Lower RMSE/MAE and higher R² are better. Prices are modeled from a
        synthetic formula — see <code>docs/model_card.md</code> for details.
      </p>
    </div>
  );
}
