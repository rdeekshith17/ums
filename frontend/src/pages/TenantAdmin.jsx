import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import Layout from "../components/Layout";
import { StatCard, DataTable, Badge, Spinner } from "../components/ui";
import api, { inr } from "../lib/api";

const TABS = [
  { key: "students", label: "Students" },
  { key: "professors", label: "Professors" },
  { key: "payments", label: "Payments" },
  { key: "payroll", label: "Payroll" },
  { key: "hall-tickets", label: "Hall Tickets" },
  { key: "expenses", label: "Expenses" },
];

const COLUMNS = {
  students: [
    { key: "roll_no", label: "Roll No" },
    { key: "name", label: "Name", render: (r) => <span className="font-medium text-slate-800">{r.name}</span> },
    { key: "department", label: "Department" },
    { key: "current_year", label: "Year" },
    { key: "cgpa", label: "CGPA" },
    { key: "attendance", label: "Attendance %", render: (r) => `${r.attendance}%` },
    { key: "fee_status", label: "Fees", render: (r) => <Badge tone={r.fee_status}>{r.fee_status}</Badge> },
    { key: "hall_ticket", label: "Hall Ticket", render: (r) => <Badge tone={r.hall_ticket}>{r.hall_ticket}</Badge> },
  ],
  professors: [
    { key: "employee_id", label: "Emp ID" },
    { key: "name", label: "Name", render: (r) => <span className="font-medium text-slate-800">{r.name}</span> },
    { key: "designation", label: "Designation" },
    { key: "department", label: "Department" },
    { key: "specialization", label: "Specialization" },
    { key: "salary", label: "Salary", render: (r) => inr(r.salary) },
    { key: "net_pay", label: "Last Net Pay", render: (r) => inr(r.net_pay) },
  ],
  payments: [
    { key: "roll_no", label: "Roll No" },
    { key: "student", label: "Student" },
    { key: "description", label: "Description" },
    { key: "amount", label: "Amount", render: (r) => inr(r.amount) },
    { key: "paid", label: "Paid", render: (r) => inr(r.paid) },
    { key: "method", label: "Method" },
    { key: "status", label: "Status", render: (r) => <Badge tone={r.status}>{r.status}</Badge> },
  ],
  payroll: [
    { key: "employee_id", label: "Emp ID" },
    { key: "name", label: "Professor", render: (r) => <span className="font-medium text-slate-800">{r.name}</span> },
    { key: "period", label: "Period" },
    { key: "gross", label: "Gross", render: (r) => inr(r.gross) },
    { key: "deductions", label: "Deductions", render: (r) => inr(r.deductions) },
    { key: "net", label: "Net Pay", render: (r) => <span className="font-semibold text-slate-800">{inr(r.net)}</span> },
  ],
  "hall-tickets": [
    { key: "roll_no", label: "Roll No" },
    { key: "student", label: "Student" },
    { key: "exam_name", label: "Exam" },
    { key: "eligibility", label: "Eligibility", render: (r) => <Badge tone={r.eligibility}>{r.eligibility}</Badge> },
    { key: "block_reason", label: "Reason", render: (r) => r.block_reason || "—" },
  ],
  expenses: [
    { key: "category", label: "Category", render: (r) => <span className="font-medium text-slate-800">{r.category}</span> },
    { key: "description", label: "Description" },
    { key: "vendor", label: "Vendor" },
    { key: "spent_on", label: "Date" },
    { key: "amount", label: "Amount", render: (r) => inr(r.amount) },
  ],
};

export default function TenantAdmin() {
  const [overview, setOverview] = useState(null);
  const [tab, setTab] = useState("students");
  const [data, setData] = useState({});
  const [loadingTab, setLoadingTab] = useState(false);

  useEffect(() => {
    api.get("/tenant/overview").then((r) => setOverview(r.data));
  }, []);

  useEffect(() => {
    if (data[tab]) return;
    setLoadingTab(true);
    api.get(`/tenant/${tab}`).then((r) => {
      setData((d) => ({ ...d, [tab]: r.data }));
      setLoadingTab(false);
    });
  }, [tab]); // eslint-disable-line

  return (
    <Layout
      title={overview ? overview.university.name : "Loading…"}
      subtitle={overview ? `${overview.university.city} · University Administration` : ""}
      badge={overview ? (
        <Badge tone={overview.university.ai_enabled ? "on" : "off"}>
          <Sparkles size={12} className="mr-1" />
          AI {overview.university.ai_enabled ? "Enabled" : "Disabled"}
        </Badge>
      ) : null}
    >
      {!overview ? <Spinner /> : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4" data-testid="tenant-stats">
            <StatCard testId="t-students" label="Students" value={overview.total_students.toLocaleString("en-IN")} />
            <StatCard testId="t-professors" label="Professors" value={overview.total_professors} />
            <StatCard testId="t-departments" label="Departments" value={overview.total_departments} hint={`${overview.total_courses} courses`} />
            <StatCard testId="t-payroll" label="Monthly Payroll" value={inr(overview.monthly_payroll)} />
            <StatCard testId="t-collected" label="Fees Collected" value={inr(overview.fees_collected)} />
            <StatCard testId="t-pending" label="Fees Pending" value={inr(overview.fees_pending)} />
            <StatCard testId="t-expenses" label="Total Expenses" value={inr(overview.total_expenses)} />
            <StatCard testId="t-courses" label="Courses" value={overview.total_courses} />
          </div>

          {/* Tabs */}
          <div className="mt-6 flex flex-wrap gap-1 rounded-xl border border-slate-200 bg-white p-1" data-testid="tenant-tabs">
            {TABS.map((t) => (
              <button
                key={t.key}
                data-testid={`tab-${t.key}`}
                onClick={() => setTab(t.key)}
                className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
                  tab === t.key ? "bg-indigo-600 text-white" : "text-slate-500 hover:bg-slate-50"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          <div className="mt-4">
            {loadingTab || !data[tab] ? (
              <Spinner label={`Loading ${tab}…`} />
            ) : (
              <DataTable testId={`table-${tab}`} columns={COLUMNS[tab]} rows={data[tab]} />
            )}
          </div>
        </>
      )}
    </Layout>
  );
}
