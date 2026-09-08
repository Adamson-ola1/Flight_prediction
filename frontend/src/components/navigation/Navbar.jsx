import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-brand">✈️ Flight Price Predictor</div>
      <nav className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
          Home
        </NavLink>
        <NavLink to="/predict" className={({ isActive }) => (isActive ? "active" : "")}>
          Predict
        </NavLink>
        <NavLink to="/model-info" className={({ isActive }) => (isActive ? "active" : "")}>
          Model Info
        </NavLink>
      </nav>
    </header>
  );
}
