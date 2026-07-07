import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth, HOME_BY_ROLE } from "./context/AuthContext";
import ProtectedRoute from "./routes/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import SubmitComplaint from "./pages/citizen/SubmitComplaint";
import MyReports from "./pages/citizen/MyReports";
import TrackComplaint from "./pages/citizen/TrackComplaint";
import OfficerQueue from "./pages/officer/OfficerQueue";
import MPDashboard from "./pages/mp/MPDashboard";
import MPComplaints from "./pages/mp/MPComplaints";
import AdminOverview from "./pages/admin/AdminOverview";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminDatasets from "./pages/admin/AdminDatasets";
import ComplaintDetail from "./pages/ComplaintDetail";

// Sends an authenticated user to the landing route for their role.
function RoleHome() {
  const { user } = useAuth();
  return <Navigate to={HOME_BY_ROLE[user.role] || "/login"} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RoleHome />} />

        {/* Citizen */}
        <Route
          path="submit"
          element={
            <ProtectedRoute roles={["citizen"]}>
              <SubmitComplaint />
            </ProtectedRoute>
          }
        />
        <Route
          path="my-reports"
          element={
            <ProtectedRoute roles={["citizen"]}>
              <MyReports />
            </ProtectedRoute>
          }
        />

        {/* Officer */}
        <Route
          path="officer"
          element={
            <ProtectedRoute roles={["officer"]}>
              <OfficerQueue />
            </ProtectedRoute>
          }
        />

        {/* MP */}
        <Route
          path="dashboard"
          element={
            <ProtectedRoute roles={["mp"]}>
              <MPDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="complaints"
          element={
            <ProtectedRoute roles={["mp"]}>
              <MPComplaints />
            </ProtectedRoute>
          }
        />

        {/* Admin */}
        <Route
          path="admin"
          element={
            <ProtectedRoute roles={["super_admin"]}>
              <AdminOverview />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/users"
          element={
            <ProtectedRoute roles={["super_admin"]}>
              <AdminUsers />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/datasets"
          element={
            <ProtectedRoute roles={["super_admin"]}>
              <AdminDatasets />
            </ProtectedRoute>
          }
        />

        {/* Shared — backend enforces per-report visibility */}
        <Route
          path="track"
          element={
            <ProtectedRoute roles={["citizen", "officer", "mp"]}>
              <TrackComplaint />
            </ProtectedRoute>
          }
        />
        <Route path="complaint/:id" element={<ComplaintDetail />} />
      </Route>

      <Route path="*" element={<Navigate to="/app" replace />} />
    </Routes>
  );
}
