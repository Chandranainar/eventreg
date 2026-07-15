import { Navigate, Route, Routes } from "react-router-dom";

import AdminLayout from "./layouts/AdminLayout";
import AdminDashboard from "./pages/AdminDashboard";
import AdminImport from "./pages/AdminImport";
import AdminLogin from "./pages/AdminLogin";
import EventSettings from "./pages/EventSettings";
import LandingPage from "./pages/LandingPage";
import PrivacyNotice from "./pages/PrivacyNotice";
import RegistrationDetail from "./pages/RegistrationDetail";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/privacy" element={<PrivacyNotice />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        <Route path="registrations/:id" element={<RegistrationDetail />} />
        <Route path="event" element={<EventSettings />} />
        <Route path="import" element={<AdminImport />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
