import Navbar from "../components/navigation/Navbar.jsx";
import Sidebar from "../components/navigation/Sidebar.jsx";
import Footer from "../components/common/Footer.jsx";

export default function DashboardLayout({ children }) {
  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-body">
        <Sidebar />
        <main className="app-content">{children}</main>
      </div>
      <Footer />
    </div>
  );
}
