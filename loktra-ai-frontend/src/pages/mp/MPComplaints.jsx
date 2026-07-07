import { useEffect, useMemo, useState } from "react";
import { Search, SlidersHorizontal, ListChecks } from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import useRefetchOnFocus from "../../lib/useRefetchOnFocus";
import { mpComplaints } from "../../api/mp";
import { CATEGORIES, STATUS_FLOW, OFFICIAL_DATASET_MODE } from "../../lib/constants";
import ComplaintCard from "../../components/ComplaintCard";
import EmptyState from "../../components/ui/EmptyState";
import Loader from "../../components/ui/Loader";

const URGENCIES = ["Emergency", "High", "Medium", "Low"];
const PRIORITY_TIERS = [
  { value: "", label: "Any priority" },
  { value: "85", label: "85+ (Critical)" },
  { value: "60", label: "60+ (High)" },
  { value: "40", label: "40+ (Moderate)" },
];

export default function MPComplaints() {
  usePageHeader("Constituency reports", "Every report in your constituency, AI-ranked");
  const [items, setItems] = useState(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [urgency, setUrgency] = useState("");
  const [minPriority, setMinPriority] = useState("");
  const [mode, setMode] = useState("");
  const [sort, setSort] = useState("priority");

  function load() {
    mpComplaints().then(setItems).catch(() => setItems([]));
  }
  useEffect(() => {
    load();
  }, []);
  useRefetchOnFocus(load);

  const view = useMemo(() => {
    if (!items) return [];
    // Show every report in the constituency — official and no-match alike.
    let list = items.filter((c) => {
      if (status && c.status !== status) return false;
      if (category && c.category !== category) return false;
      if (urgency && c.urgency !== urgency) return false;
      if (minPriority && c.priority_score < Number(minPriority)) return false;
      if (mode === "official" && c.dataset_mode !== OFFICIAL_DATASET_MODE) return false;
      if (mode === "nomatch" && c.dataset_mode === OFFICIAL_DATASET_MODE) return false;
      if (q) {
        const hay = `${c.title} ${c.complaint_code} ${c.ai_summary || ""}`.toLowerCase();
        if (!hay.includes(q.toLowerCase())) return false;
      }
      return true;
    });
    list = [...list].sort((a, b) =>
      sort === "priority"
        ? b.priority_score - a.priority_score
        : new Date(b.created_at) - new Date(a.created_at)
    );
    return list;
  }, [items, q, status, category, urgency, minPriority, mode, sort]);

  if (items === null) return <Loader label="Loading reports" />;

  return (
    <div>
      <div className="card mb-5 p-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              className="input pl-9"
              placeholder="Search title, code or summary…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
          <select className="input sm:w-40" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All statuses</option>
            {STATUS_FLOW.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select className="input sm:w-44" value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select className="input sm:w-40" value={urgency} onChange={(e) => setUrgency(e.target.value)}>
            <option value="">All urgencies</option>
            {URGENCIES.map((u) => <option key={u} value={u}>{u}</option>)}
          </select>
          <select className="input sm:w-40" value={minPriority} onChange={(e) => setMinPriority(e.target.value)}>
            {PRIORITY_TIERS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
          <select className="input sm:w-44" value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="">All datasets</option>
            <option value="official">Official Government Dataset</option>
            <option value="nomatch">No Official Dataset Match</option>
          </select>
          <select className="input sm:w-40" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="priority">Priority ↓</option>
            <option value="recent">Most recent</option>
          </select>
        </div>
      </div>

      <p className="mb-3 flex items-center gap-1.5 text-xs font-500 text-muted">
        <SlidersHorizontal className="h-3.5 w-3.5" />
        {view.length} report{view.length === 1 ? "" : "s"}
      </p>

      {view.length === 0 ? (
        <EmptyState icon={ListChecks} title="No matching reports" hint="Try clearing filters or a different search." />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {view.map((c) => (
            <ComplaintCard key={c.id} complaint={c} />
          ))}
        </div>
      )}
    </div>
  );
}
