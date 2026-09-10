import Navbar from "../components/navigation/Navbar.jsx";
import Footer from "../components/common/Footer.jsx";

export default function DashboardLayout({ children }) {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="app-content">{children}</main>
      <Footer />
    </div>
  );
}
