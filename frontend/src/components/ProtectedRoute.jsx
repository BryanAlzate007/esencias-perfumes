import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Spinner } from "react-bootstrap";
import { useAuth } from "../hooks/useAuth";

export function ProtectedRoute({ adminOnly = false }) {
  const { ready, isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();

  if (!ready) {
    return (
      <div className="d-flex justify-content-center py-5">
        <Spinner animation="border" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  if (!adminOnly && isAdmin && location.pathname === "/") {
    return <Navigate to="/admin/catalogo" replace />;
  }

  return <Outlet />;
}
