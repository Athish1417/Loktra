import { useState } from "react";
import { Search, Loader2, PackageSearch } from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import { trackComplaint } from "../../api/complaints";
import { errorMessage } from "../../api/client";
import {
  StatusBadge,
  UrgencyPill,
  CategoryTag,
  EmergencyFlag,
  DatasetModeBadge,
} from "../../components/ui/Badges";
import PriorityGauge from "../../components/ui/PriorityGauge";
import Timeline from "../../components/Timeline";
import EmptyState from "../../components/ui/EmptyState";

export default function TrackComplaint() {
  usePageHeader("Track a report", "Look up any report you can see by its code");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  async function search(e) {
    e.preventDefault();
    if (!code.trim()) return;
    setBusy(true);
    setError("");
    setData(null);
    try {
      setData(await trackComplaint(code.trim().toUpperCase()));
    } catch (err) {
      setError(errorMessage(err, "No report found for that code."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <form onSubmit={search} className="mb-6 flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            className="input pl-10 font-mono uppercase"
            placeholder="LOK-2026-000001"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        </div>
        <button className="btn-primary" disabled={busy}>
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Track"}
        </button>
      </form>

      {error && (
        <EmptyState icon={PackageSearch} title="Not found" hint={error} />
      )}

      {data && (
        <div className="card overflow-hidden">
          <div className="flex items-center gap-5 border-b border-hairline p-5">
            <PriorityGauge score={data.priority_score} size={104} />
            <div className="min-w-0 flex-1">
              <p className="font-mono text-xs text-muted">{data.complaint_code}</p>
              <h3 className="mt-0.5 font-display text-base font-600 text-body">
                {data.title}
              </h3>
              <div className="mt-2 flex flex-wrap items-center gap-1.5">
                <StatusBadge status={data.status} />
                <UrgencyPill urgency={data.urgency} />
                <CategoryTag category={data.category} />
                {data.is_emergency && <EmergencyFlag compact />}
              </div>
              {data.dataset_mode && (
                <div className="mt-2">
                  <DatasetModeBadge
                    mode={data.dataset_mode}
                    matched={data.matched_datasets}
                  />
                </div>
              )}
            </div>
          </div>
          <div className="p-5">
            <h4 className="mb-3 text-xs font-600 uppercase tracking-wide text-muted">
              Progress
            </h4>
            <Timeline events={data.timeline} />
          </div>
        </div>
      )}
    </div>
  );
}
