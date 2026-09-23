import { useEffect } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Spinner } from "react-bootstrap";
import { useAuth } from "../hooks/useAuth";
import { useAuthModal } from "../hooks/useAuthModal";

function LoginRequired({ from }) {
  const { openLogin } = useAuthModal();

  useEffect(() => {
    openLogin(from);
  }, [from, openLogin]);

  return <Navigate to="/" replace />;
}

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
    return <LoginRequired from={location.pathname} />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  if (!adminOnly && isAdmin && location.pathname === "/") {
    return <Navigate to="/admin" replace />;
  }

  return <Outlet />;
}
