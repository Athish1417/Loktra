import { AlertTriangle, ShieldCheck, Database } from "lucide-react";
import { STATUS_META, URGENCY_META } from "../../lib/constants";

const OFFICIAL_MODE = "Official Government Dataset";

// Shows whether a complaint's priority used an official government dataset, plus the
// matched datasets. Renders nothing for pre-Phase-5 complaints with no dataset_mode.
export function DatasetModeBadge({ mode, matched, showMatched = true }) {
  if (!mode) return null;
  const official = mode === OFFICIAL_MODE;
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span
        className={`chip ${
          official ? "bg-success/10 text-success" : "bg-saffron-100 text-saffron-600"
        }`}
        title="Dataset used to inform this priority"
      >
        {official ? (
          <ShieldCheck className="h-3.5 w-3.5" />
        ) : (
          <Database className="h-3.5 w-3.5" />
        )}
        {mode}
      </span>
      {showMatched &&
        matched?.length > 0 &&
        matched.map((d) => (
          <span key={d} className="chip bg-royal-50 text-royal">
            {d}
          </span>
        ))}
    </div>
  );
}

export function StatusBadge({ status }) {
  const m = STATUS_META[status] || STATUS_META.Submitted;
  return (
    <span
      className="chip"
      style={{ color: m.color, backgroundColor: m.bg }}
    >
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: m.color }}
      />
      {m.label}
    </span>
  );
}

export function UrgencyPill({ urgency }) {
  const m = URGENCY_META[urgency] || URGENCY_META.Medium;
  return (
    <span className="chip" style={{ color: m.color, backgroundColor: m.bg }}>
      {urgency}
    </span>
  );
}

export function CategoryTag({ category }) {
  return (
    <span className="chip bg-paper text-muted border border-hairline">
      {category}
    </span>
  );
}

// Emergency indicator with a soft pulsing ring — the app's alert signature.
export function EmergencyFlag({ compact = false }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full bg-emergency/10 px-2.5 py-1 text-xs font-700 text-emergency animate-pulse-ring"
      title="Flagged as an emergency by AI"
    >
      <AlertTriangle className="h-3.5 w-3.5" />
      {!compact && "Emergency"}
    </span>
  );
}
