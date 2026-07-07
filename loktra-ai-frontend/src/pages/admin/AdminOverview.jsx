import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Users,
  Landmark,
  ShieldCheck,
  UserCog,
  User,
  Database,
  ArrowUpRight,
} from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import useRefetchOnFocus from "../../lib/useRefetchOnFocus";
import { listUsers, listDatasets } from "../../api/admin";
import { listComplaints } from "../../api/complaints";
import { getConstituencyIndex } from "../../api/locations";
import StatTile from "../../components/ui/StatTile";
import ComplaintCard from "../../components/ComplaintCard";
import Loader from "../../components/ui/Loader";
import { isOfficialComplaint } from "../../lib/constants";

const ROLE_META = {
  super_admin: { label: "Admin", cls: "bg-ink/5 text-ink" },
  mp: { label: "MP", cls: "bg-royal-50 text-royal" },
  officer: { label: "Officer", cls: "bg-saffron-100 text-saffron-600" },
  citizen: { label: "Citizen", cls: "bg-paper text-muted" },
};

const DATASET_FILTERS = [
  { value: "", label: "All datasets" },
  { value: "official", label: "Official Government Dataset" },
  { value: "nomatch", label: "No Official Dataset Match" },
];

export default function AdminOverview() {
  usePageHeader("Platform overview", "System-wide view across constituencies");
  const [state, setState] = useState(null);
  const [mode, setMode] = useState("");

  function load() {
    // Lightweight core fetch — renders even if the constituency count is slow.
    Promise.all([listUsers(), listDatasets(), listComplaints()])
      .then(([users, datasets, complaints]) =>
        setState((prev) => ({
          users,
          datasets,
          complaints,
          constituencies: prev?.constituencies ?? 0,
        }))
      )
      .catch(() => setState((prev) => (prev && prev.complaints ? prev : false)));
    // Constituency count is non-critical — never let it block the overview.
    getConstituencyIndex()
      .then((idx) =>
        setState((prev) =>
          prev ? { ...prev, constituencies: Object.keys(idx).length } : prev
        )
      )
      .catch(() => {});
  }
  useEffect(() => {
    load();
  }, []);
  useRefetchOnFocus(load);

  if (state === null) return <Loader label="Loading overview" />;
  if (state === false)
    return <p className="text-sm text-muted">Could not load the overview.</p>;

  const { users, datasets, constituencies, complaints } = state;
  const byRole = users.reduce((acc, u) => {
    acc[u.role] = (acc[u.role] || 0) + 1;
    return acc;
  }, {});
  const shown = complaints
    .filter((c) => {
      if (mode === "official") return isOfficialComplaint(c);
      if (mode === "nomatch") return !isOfficialComplaint(c);
      return true;
    })
    // Newest first so a just-submitted complaint always appears at the top.
    .slice()
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 50);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile icon={Users} label="Total users" value={users.length} tone="ink" />
        <StatTile icon={User} label="Citizens" value={byRole.citizen || 0} tone="royal" />
        <StatTile icon={ShieldCheck} label="MPs" value={byRole.mp || 0} tone="royal" />
        <StatTile icon={UserCog} label="Officers" value={byRole.officer || 0} tone="saffron" />
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="card flex items-center gap-3.5 p-4">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-royal-50 text-royal">
            <Landmark className="h-5 w-5" />
          </div>
          <div>
            <p className="font-display text-2xl font-700 tabular text-body">{constituencies}</p>
            <p className="text-xs font-500 text-muted">Constituencies configured</p>
          </div>
        </div>
        <div className="card flex items-center gap-3.5 p-4">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-success/10 text-success">
            <Database className="h-5 w-5" />
          </div>
          <div>
            <p className="font-display text-2xl font-700 tabular text-body">{datasets.length}</p>
            <p className="text-xs font-500 text-muted">Datasets configured</p>
          </div>
        </div>
      </div>

      <div>
        <div className="mb-3 flex items-center justify-between gap-3">
          <h3 className="font-display font-600 text-body">
            Recent complaints
            <span className="ml-2 text-xs font-500 text-muted">
              (all constituencies)
            </span>
          </h3>
          <select
            className="input w-auto"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            aria-label="Filter by dataset mode"
          >
            {DATASET_FILTERS.map((f) => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </select>
        </div>
        {shown.length ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {shown.map((c) => (
              <ComplaintCard key={c.id} complaint={c} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted">No complaints match this dataset filter.</p>
        )}
      </div>

      <div className="card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display font-600 text-body">People on the platform</h3>
          <Link to="/app/admin/users" className="inline-flex items-center gap-1 text-sm font-600 text-royal hover:underline">
            Manage <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="divide-y divide-hairline">
          {users.slice(0, 6).map((u) => {
            const m = ROLE_META[u.role] || ROLE_META.citizen;
            return (
              <div key={u.id} className="flex items-center gap-3 py-2.5">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-royal text-xs font-700 text-white">
                  {u.name.split(" ").map((s) => s[0]).slice(0, 2).join("").toUpperCase()}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-600 text-body">{u.name}</p>
                  <p className="truncate text-xs text-muted">{u.email}</p>
                </div>
                <span className={`chip ${m.cls}`}>{m.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
