import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { getHealth } from "../../api/resource.api.js";

export default function Navbar() {
  const [live, setLive] = useState(false);

  useEffect(() => {
    let active = true;
    getHealth()
      .then((data) => active && setLive(data?.status === "ok" && data?.model_loaded === true))
      .catch(() => active && setLive(false));
    return () => { active = false; };
  }, []);

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand">
          <span className="brand-mark">✈</span>
          <span>Flight Price Predictor</span>
        </NavLink>
        <nav className="navbar-links" aria-label="Main navigation">
          <NavLink to="/predict" className={({ isActive }) => isActive ? "active" : ""}>Predict</NavLink>
          <NavLink to="/model-info" className={({ isActive }) => isActive ? "active" : ""}>Model Info</NavLink>
          <span className={`model-status ${live ? "is-live" : "is-offline"}`} title={live ? "Backend and trained model are available" : "Backend or trained model unavailable"}>
            <span className="status-dot" /> Model {live ? "Live" : "Offline"}
          </span>
        </nav>
      </div>
    </header>
  );
}
