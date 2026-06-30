import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Login from "@/pages/Login";
import SuperAdmin from "@/pages/SuperAdmin";
import TenantAdmin from "@/pages/TenantAdmin";
import { Spinner } from "@/components/ui";

function RootRedirect() {
  const { user, ready } = useAuth();
  if (!ready || user === null)
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <Spinner label="Loading UniAI…" />
      </div>
    );
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "super_admin" ? "/super" : "/tenant"} replace />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/super"
            element={
              <ProtectedRoute role="super_admin">
                <SuperAdmin />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tenant"
            element={
              <ProtectedRoute role="admin">
                <TenantAdmin />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
