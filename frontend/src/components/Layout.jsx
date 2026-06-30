import { LogOut, GraduationCap } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Layout({ title, subtitle, badge, children }) {
  const { user, logout } = useAuth();
  const initials = (user?.name || "U")
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col bg-slate-900 text-slate-300 lg:flex">
        <div className="flex items-center gap-2.5 px-6 py-6">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white">
            <GraduationCap size={20} />
          </span>
          <div>
            <p className="font-display text-lg font-bold leading-none text-white">UniAI</p>
            <p className="text-[11px] text-slate-400">University AI Platform</p>
          </div>
        </div>

        <div className="mt-2 px-4">
          <div className="rounded-xl bg-slate-800/60 px-4 py-3">
            <p className="text-[11px] uppercase tracking-wider text-slate-500">Signed in as</p>
            <p className="mt-0.5 truncate text-sm font-semibold text-white" data-testid="sidebar-user-name">
              {user?.name}
            </p>
            <p className="truncate text-xs text-slate-400">{user?.email}</p>
            <span className="mt-2 inline-flex rounded-full bg-indigo-500/20 px-2 py-0.5 text-[11px] font-semibold text-indigo-300">
              {user?.role === "super_admin" ? "Super Admin" : "Tenant Admin"}
            </span>
          </div>
        </div>

        <div className="mt-auto px-4 pb-6">
          <button
            data-testid="logout-button"
            onClick={logout}
            className="flex w-full items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-slate-800 hover:text-white"
          >
            <LogOut size={16} /> Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
          <div className="flex items-center justify-between px-6 py-4">
            <div>
              <h1 className="font-display text-xl font-bold text-slate-800" data-testid="page-title">
                {title}
              </h1>
              {subtitle ? <p className="text-sm text-slate-400">{subtitle}</p> : null}
            </div>
            <div className="flex items-center gap-3">
              {badge}
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-700">
                {initials}
              </span>
            </div>
          </div>
        </header>
        <main className="px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
