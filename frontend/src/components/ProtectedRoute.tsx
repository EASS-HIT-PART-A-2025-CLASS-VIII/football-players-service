import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const location = useLocation();
  const token = localStorage.getItem("access_token");

  if (!token) {
    // Redirect to home page, preserving the attempted destination
    return (
      <Navigate to="/" state={{ from: location, requiresAuth: true }} replace />
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
