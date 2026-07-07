import { useEffect, useMemo, useState } from "react";
import { ClipboardCheck } from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import useRefetchOnFocus from "../../lib/useRefetchOnFocus";
import { officerQueue } from "../../api/officer";
import ComplaintCard from "../../components/ComplaintCard";
import EmptyState from "../../components/ui/EmptyState";
import Loader from "../../components/ui/Loader";

const TABS = [
  { key: "active", label: "Active" },
  { key: "unverified", label: "Needs verification" },
  { key: "completed", label: "Completed" },
  { key: "all", label: "All" },
];

export default function OfficerQueue() {
  usePageHeader("Work queue", "Reports assigned to you, prioritised by AI");
  const [items, setItems] = useState(null);
  const [tab, setTab] = useState("active");

  function load() {
    officerQueue()
      .then((list) =>
        [...list].sort((a, b) => b.priority_score - a.priority_score)
      )
      .then(setItems)
      .catch(() => setItems([]));
  }
  useEffect(() => {
    load();
  }, []);
  useRefetchOnFocus(load);

  // Show every assigned report — official and no-match alike.
  const base = useMemo(() => items || [], [items]);

  const filtered = useMemo(() => {
    switch (tab) {
      case "unverified":
        return base.filter((c) => c.status === "Submitted");
      case "completed":
        return base.filter((c) => c.status === "Completed");
      case "active":
        return base.filter((c) => c.status !== "Completed");
      default:
        return base;
    }
  }, [base, tab]);

  const counts = useMemo(
    () => ({
      active: base.filter((c) => c.status !== "Completed").length,
      unverified: base.filter((c) => c.status === "Submitted").length,
      completed: base.filter((c) => c.status === "Completed").length,
      all: base.length,
    }),
    [base]
  );

  return (
    <div>
      <div className="mb-5 flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={[
              "inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-600 transition",
              tab === t.key
                ? "bg-ink text-white"
                : "border border-hairline bg-white text-muted hover:text-body",
            ].join(" ")}
          >
            {t.label}
            {counts[t.key] != null && (
              <span
                className={[
                  "rounded-full px-1.5 text-[10px]",
                  tab === t.key ? "bg-white/20" : "bg-paper",
                ].join(" ")}
              >
                {counts[t.key]}
              </span>
            )}
          </button>
        ))}
      </div>

      {items === null ? (
        <Loader label="Loading your queue" />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={ClipboardCheck}
          title="Nothing here"
          hint="Reports assigned to you and awaiting action will appear in this queue."
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {filtered.map((c) => (
            <ComplaintCard key={c.id} complaint={c} />
          ))}
        </div>
      )}
    </div>
  );
}
