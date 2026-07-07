import { useEffect, useState } from "react";
import { Inbox, FilePlus2 } from "lucide-react";
import { Link } from "react-router-dom";
import usePageHeader from "../../lib/usePageHeader";
import useRefetchOnFocus from "../../lib/useRefetchOnFocus";
import { listComplaints } from "../../api/complaints";
import ComplaintCard from "../../components/ComplaintCard";
import EmptyState from "../../components/ui/EmptyState";
import Loader from "../../components/ui/Loader";
import { STATUS_FLOW } from "../../lib/constants";

export default function MyReports() {
  usePageHeader("My reports", "Everything you've reported and its progress");
  const [items, setItems] = useState(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    listComplaints(status ? { status } : {})
      .then(setItems)
      .catch(() => setItems([]));
  }, [status]);
  // Reflect status changes made by officers/MPs when the citizen returns to the tab.
  useRefetchOnFocus(() =>
    listComplaints(status ? { status } : {})
      .then(setItems)
      .catch(() => {})
  );

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center gap-2">
        <FilterChip active={status === ""} onClick={() => setStatus("")}>
          All
        </FilterChip>
        {STATUS_FLOW.map((s) => (
          <FilterChip key={s} active={status === s} onClick={() => setStatus(s)}>
            {s}
          </FilterChip>
        ))}
      </div>

      {items === null ? (
        <Loader label="Loading your reports" />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="No reports yet"
          hint="When you report a civic issue, it'll show up here with live status."
          action={
            <Link to="/app/submit" className="btn-primary">
              <FilePlus2 className="h-4 w-4" /> Report an issue
            </Link>
          }
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {items.map((c) => (
            <ComplaintCard key={c.id} complaint={c} />
          ))}
        </div>
      )}
    </div>
  );
}

function FilterChip({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={[
        "rounded-full px-3.5 py-1.5 text-xs font-600 transition",
        active
          ? "bg-ink text-white"
          : "border border-hairline bg-white text-muted hover:text-body",
      ].join(" ")}
    >
      {children}
    </button>
  );
}
