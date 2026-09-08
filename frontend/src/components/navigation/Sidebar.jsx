export default function Sidebar() {
  return (
    <aside className="sidebar">
      <h3>About</h3>
      <p>
        Predicts the ticket price of a domestic flight departing NYC
        (JFK, LGA, EWR), trained on the nycflights13 dataset with a
        synthetic price target.
      </p>
      <h4>Pipeline</h4>
      <ul>
        <li>Data cleaning</li>
        <li>Feature engineering</li>
        <li>5 candidate models</li>
        <li>Stacking ensemble</li>
      </ul>
    </aside>
  );
}
