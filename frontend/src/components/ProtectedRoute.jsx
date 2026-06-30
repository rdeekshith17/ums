import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "./ui";

export default function ProtectedRoute({ role, children }) {
  const { user, ready } = useAuth();

  if (!ready || user === null) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <Spinner label="Checking session…" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) {
    return <Navigate to={user.role === "super_admin" ? "/super" : "/tenant"} replace />;
  }
  return children;
}
