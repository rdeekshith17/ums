import { useEffect, useState, useCallback } from "react";
import { Plus, Power, Ban, CheckCircle2, X } from "lucide-react";
import Layout from "../components/Layout";
import { StatCard, DataTable, Badge, Button, Spinner } from "../components/ui";
import api, { inr, formatApiError } from "../lib/api";

function AddUniversityModal({ open, onClose, onCreated }) {
  const [form, setForm] = useState({
    tenant_id: "", name: "", short_code: "", university_type: "State",
    city: "Hyderabad", established_year: "",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  if (!open) return null;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async () => {
    setError("");
    setSaving(true);
    try {
      await api.post("/superadmin/universities", {
        ...form,
        established_year: form.established_year ? Number(form.established_year) : null,
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl" data-testid="add-university-modal">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-lg font-bold text-slate-800">Add University</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-4">
          {[
            ["tenant_id", "Code (e.g. MGU)"],
            ["short_code", "Short Code"],
            ["name", "Full Name"],
            ["city", "City"],
          ].map(([k, label]) => (
            <div key={k} className={k === "name" ? "col-span-2" : ""}>
              <label className="text-xs font-semibold text-slate-500">{label}</label>
              <input
                data-testid={`uni-${k}`}
                value={form[k]}
                onChange={set(k)}
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
              />
            </div>
          ))}
          <div>
            <label className="text-xs font-semibold text-slate-500">Type</label>
            <select
              data-testid="uni-type"
              value={form.university_type}
              onChange={set("university_type")}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400"
            >
              {["State", "Central", "Deemed", "Private"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-500">Established Year</label>
            <input
              data-testid="uni-year"
              value={form.established_year}
              onChange={set("established_year")}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            />
          </div>
        </div>
        {error ? <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button data-testid="uni-save" onClick={save} disabled={saving || !form.tenant_id || !form.name}>
            {saving ? "Saving…" : "Create University"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function SuperAdmin() {
  const [overview, setOverview] = useState(null);
  const [unis, setUnis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);

  const load = useCallback(async () => {
    const [o, u] = await Promise.all([
      api.get("/superadmin/overview"),
      api.get("/superadmin/universities"),
    ]);
    setOverview(o.data);
    setUnis(u.data);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const toggleAi = async (u) => {
    await api.patch(`/superadmin/universities/${u.tenant_id}/ai`, { ai_enabled: !u.ai_enabled });
    load();
  };
  const toggleStatus = async (u) => {
    const status = u.status === "active" ? "suspended" : "active";
    await api.patch(`/superadmin/universities/${u.tenant_id}/status`, { status });
    load();
  };

  const columns = [
    { key: "name", label: "University", render: (r) => (
      <div>
        <p className="font-semibold text-slate-800">{r.name}</p>
        <p className="text-xs text-slate-400">{r.tenant_id} · {r.university_type} · {r.city}</p>
      </div>
    )},
    { key: "established_year", label: "Est." },
    { key: "students", label: "Students" },
    { key: "professors", label: "Professors" },
    { key: "status", label: "Status", render: (r) => <Badge tone={r.status}>{r.status}</Badge> },
    { key: "ai_enabled", label: "AI", render: (r) => <Badge tone={r.ai_enabled ? "on" : "off"}>{r.ai_enabled ? "Enabled" : "Disabled"}</Badge> },
    { key: "actions", label: "Actions", render: (r) => (
      <div className="flex gap-2">
        <button
          data-testid={`ai-toggle-${r.tenant_id}`}
          onClick={() => toggleAi(r)}
          title="Toggle AI"
          className="rounded-lg p-1.5 text-indigo-600 ring-1 ring-inset ring-slate-200 hover:bg-indigo-50"
        ><Power size={15} /></button>
        <button
          data-testid={`status-toggle-${r.tenant_id}`}
          onClick={() => toggleStatus(r)}
          title={r.status === "active" ? "Suspend" : "Activate"}
          className={`rounded-lg p-1.5 ring-1 ring-inset ring-slate-200 ${r.status === "active" ? "text-rose-600 hover:bg-rose-50" : "text-emerald-600 hover:bg-emerald-50"}`}
        >{r.status === "active" ? <Ban size={15} /> : <CheckCircle2 size={15} />}</button>
      </div>
    )},
  ];

  return (
    <Layout
      title="Platform Overview"
      subtitle="Manage all universities on the UniAI platform"
      badge={<Button data-testid="add-university-btn" onClick={() => setModal(true)}><Plus size={16} /> Add University</Button>}
    >
      {loading ? <Spinner /> : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6" data-testid="superadmin-stats">
            <StatCard testId="stat-universities" label="Universities" value={overview.total_universities} hint={`${overview.active} active · ${overview.suspended} suspended`} />
            <StatCard testId="stat-ai" label="AI Enabled" value={overview.ai_enabled} hint="universities" />
            <StatCard testId="stat-students" label="Students" value={overview.total_students.toLocaleString("en-IN")} />
            <StatCard testId="stat-professors" label="Professors" value={overview.total_professors} />
            <StatCard testId="stat-admins" label="Admins" value={overview.total_admins} />
            <StatCard testId="stat-revenue" label="Total Revenue" value={inr(overview.total_revenue)} />
          </div>

          <div className="mt-6">
            <h2 className="mb-3 font-display text-lg font-bold text-slate-800">Universities</h2>
            <DataTable testId="universities-table" columns={columns} rows={unis} />
          </div>
        </>
      )}

      <AddUniversityModal open={modal} onClose={() => setModal(false)} onCreated={load} />
    </Layout>
  );
}
