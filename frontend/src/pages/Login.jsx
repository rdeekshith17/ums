import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GraduationCap, ShieldCheck } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui";
import { formatApiError } from "../lib/api";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const u = await login(email, password);
      navigate(u.role === "super_admin" ? "/super" : "/tenant", { replace: true });
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  const fill = (em, pw) => {
    setEmail(em);
    setPassword(pw);
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Brand panel */}
      <div className="relative hidden w-1/2 flex-col justify-between bg-slate-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600">
            <GraduationCap size={24} />
          </span>
          <span className="font-display text-2xl font-bold">UniAI</span>
        </div>
        <div>
          <h2 className="font-display text-4xl font-bold leading-tight">
            The AI-powered platform for universities.
          </h2>
          <p className="mt-4 max-w-md text-slate-400">
            Manage every institution, student, professor and finance record from a single,
            secure multi-tenant dashboard.
          </p>
        </div>
        <p className="text-xs text-slate-500">© 2026 UniAI · Telangana edition</p>
      </div>

      {/* Form panel */}
      <div className="flex w-full items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-sm">
          <h1 className="font-display text-2xl font-bold text-slate-800">Welcome back</h1>
          <p className="mt-1 text-sm text-slate-400">Sign in to your dashboard.</p>

          <form onSubmit={submit} className="mt-8 space-y-4" data-testid="login-form">
            <div>
              <label className="text-sm font-medium text-slate-600">Email</label>
              <input
                data-testid="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                placeholder="you@university.ac.in"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-600">Password</label>
              <input
                data-testid="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                placeholder="••••••••"
              />
            </div>

            {error ? (
              <p data-testid="login-error" className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {error}
              </p>
            ) : null}

            <Button data-testid="login-submit" type="submit" disabled={loading} className="w-full">
              {loading ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          <div className="mt-8 rounded-xl border border-slate-200 bg-white p-4 text-sm">
            <p className="flex items-center gap-1.5 font-semibold text-slate-600">
              <ShieldCheck size={15} className="text-indigo-600" /> Demo accounts
            </p>
            <button
              data-testid="demo-super"
              onClick={() => fill("superadmin@uniai.app", "SuperAdmin@123")}
              className="mt-2 block w-full rounded-lg px-3 py-2 text-left text-xs text-slate-500 transition hover:bg-slate-50"
            >
              <b className="text-slate-700">Super Admin</b> — superadmin@uniai.app / SuperAdmin@123
            </button>
            <button
              data-testid="demo-tenant"
              onClick={() => fill("aishwarya.mudirajadm4@ku.ac.in", "Admin@123")}
              className="block w-full rounded-lg px-3 py-2 text-left text-xs text-slate-500 transition hover:bg-slate-50"
            >
              <b className="text-slate-700">Tenant Admin</b> — Kakatiya University / Admin@123
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
