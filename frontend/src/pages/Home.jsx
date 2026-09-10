import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page home-page">
      <section className="home-hero">
        <div className="home-copy">
          <span className="eyebrow">MACHINE LEARNING · FLIGHT ANALYTICS</span>
          <h1>Predict the price before you fly.</h1>
          <p>
            Estimate domestic flight fares departing New York using a trained regression pipeline,
            compare model performance, and keep a history of your predictions.
          </p>
          <div className="home-actions">
            <Link className="predict-button home-primary" to="/predict">✈  Start predicting</Link>
            <Link className="home-secondary" to="/model-info">Explore model performance →</Link>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="flight-card">
            <span>ESTIMATED FARE</span>
            <strong>$—</strong>
            <small>Enter a flight to begin</small>
          </div>
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <span className="hero-plane">✈</span>
        </div>
      </section>

      <section className="home-feature-grid">
        <article className="feature-card">
          <span className="feature-number">01</span>
          <h2>Engineer the signal</h2>
          <p>Time features, route frequency encodings, seasonality and cyclical features prepare the flight data for modeling.</p>
        </article>
        <article className="feature-card featured">
          <span className="feature-number">02</span>
          <h2>Compare five models</h2>
          <p>Linear Regression, Random Forest, XGBoost, LightGBM and a Stacking Ensemble compete on the same pipeline.</p>
        </article>
        <article className="feature-card">
          <span className="feature-number">03</span>
          <h2>Serve the best model</h2>
          <p>The selected model is exposed through FastAPI for live predictions from this React application.</p>
        </article>
      </section>
    </div>
  );
}
