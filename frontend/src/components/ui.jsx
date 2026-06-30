import { useMemo, useState } from "react";

export function Spinner({ label = "Loading…" }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-slate-400">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-600" />
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}

export function StatCard({ label, value, hint, testId }) {
  return (
    <div
      data-testid={testId}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
    >
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </p>
      <p className="mt-2 font-display text-2xl font-bold text-slate-800">{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-400">{hint}</p> : null}
    </div>
  );
}

const badgeTones = {
  active: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  suspended: "bg-rose-50 text-rose-700 ring-rose-600/20",
  eligible: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  blocked: "bg-rose-50 text-rose-700 ring-rose-600/20",
  paid: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  partial: "bg-amber-50 text-amber-700 ring-amber-600/20",
  unpaid: "bg-slate-100 text-slate-600 ring-slate-500/20",
  overdue: "bg-rose-50 text-rose-700 ring-rose-600/20",
  on: "bg-indigo-50 text-indigo-700 ring-indigo-600/20",
  off: "bg-slate-100 text-slate-500 ring-slate-500/20",
};

export function Badge({ children, tone = "unpaid" }) {
  const cls = badgeTones[tone] || badgeTones.unpaid;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${cls}`}>
      {children}
    </span>
  );
}

export function Button({ children, variant = "primary", className = "", ...rest }) {
  const variants = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700",
    ghost: "bg-white text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-slate-50",
    danger: "bg-rose-600 text-white hover:bg-rose-700",
    subtle: "bg-slate-800 text-white hover:bg-slate-900",
  };
  return (
    <button
      className={`inline-flex items-center justify-center gap-1.5 rounded-lg px-3.5 py-2 text-sm font-semibold transition disabled:opacity-50 ${variants[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}

export function DataTable({ columns, rows, searchable = true, testId }) {
  const [q, setQ] = useState("");
  const filtered = useMemo(() => {
    if (!q.trim()) return rows;
    const t = q.toLowerCase();
    return rows.filter((r) =>
      columns.some((c) => String(r[c.key] ?? "").toLowerCase().includes(t))
    );
  }, [q, rows, columns]);

  return (
    <div data-testid={testId} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">
        <span className="text-sm font-semibold text-slate-500">
          {filtered.length} record{filtered.length === 1 ? "" : "s"}
        </span>
        {searchable && (
          <input
            data-testid="table-search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search…"
            className="w-56 rounded-lg border border-slate-200 px-3 py-1.5 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
          />
        )}
      </div>
      <div className="max-h-[60vh] overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-slate-50 text-xs uppercase tracking-wider text-slate-400">
            <tr>
              {columns.map((c) => (
                <th key={c.key} className="whitespace-nowrap px-4 py-3 font-semibold">
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map((r, i) => (
              <tr key={r.roll_no || r.employee_id || r.tenant_id || r.id || i} className="hover:bg-slate-50/60">
                {columns.map((c) => (
                  <td key={c.key} className="whitespace-nowrap px-4 py-3 text-slate-700">
                    {c.render ? c.render(r) : r[c.key]}
                  </td>
                ))}
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-4 py-10 text-center text-slate-400">
                  No records found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
