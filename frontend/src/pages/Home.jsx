import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page">
      <h1>Predict NYC Flight Ticket Prices</h1>
      <p>
        This demo trains five regression models (Linear Regression, Random
        Forest, XGBoost, LightGBM, and a Stacking Ensemble) on the
        nycflights13 dataset and serves the best one through a FastAPI
        backend.
      </p>
      <div className="home-actions">
        <Link className="btn btn-primary" to="/predict">
          Get a price estimate →
        </Link>
        <Link className="btn btn-secondary" to="/model-info">
          View model performance
        </Link>
      </div>
      <div className="home-cards">
        <div className="card">
          <h3>1. Data cleaning</h3>
          <p>Duplicates removed, midnight-hour quirk fixed, distance outliers trimmed.</p>
        </div>
        <div className="card">
          <h3>2. Feature engineering</h3>
          <p>Season/time-of-day buckets, route &amp; destination frequency encodings, cyclical time features.</p>
        </div>
        <div className="card">
          <h3>3. Model training</h3>
          <p>Five regressors compared on RMSE, MAE and R²; the best is auto-selected for serving.</p>
        </div>
      </div>
    </div>
  );
}
