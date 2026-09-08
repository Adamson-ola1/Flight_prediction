import { Routes, Route } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout.jsx";
import Home from "./pages/Home.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ModelInfo from "./pages/ModelInfo.jsx";
import NotFound from "./pages/NotFound.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";

export default function App() {
  return (
    <AuthProvider>
      <DashboardLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/predict" element={<Dashboard />} />
          <Route path="/model-info" element={<ModelInfo />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </DashboardLayout>
    </AuthProvider>
  );
}
