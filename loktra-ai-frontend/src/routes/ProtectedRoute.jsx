import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { HOME_BY_ROLE } from "../context/AuthContext";
import Loader from "../components/ui/Loader";

// Gate authenticated areas; optionally restrict to specific roles.
export default function ProtectedRoute({ roles, children }) {
  const { user, ready } = useAuth();
  const location = useLocation();

  if (!ready) return <Loader full label="Loading your workspace" />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;

  if (roles && !roles.includes(user.role)) {
    // Signed in but wrong role — send to their own home.
    return <Navigate to={HOME_BY_ROLE[user.role] || "/login"} replace />;
  }
  return children;
}
