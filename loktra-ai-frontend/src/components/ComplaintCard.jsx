import { Link } from "react-router-dom";
import { ArrowUpRight, MapPin, Copy } from "lucide-react";
import {
  StatusBadge,
  UrgencyPill,
  CategoryTag,
  EmergencyFlag,
  DatasetModeBadge,
} from "./ui/Badges";
import { URGENCY_META, priorityColor } from "../lib/constants";

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

export default function ComplaintCard({ complaint, to }) {
  const rail = (URGENCY_META[complaint.urgency] || URGENCY_META.Medium).color;
  const pColor = priorityColor(complaint.priority_score);

  const locationLabel = [
    complaint.ward_name,
    complaint.constituency_name,
    complaint.district_name,
    complaint.state_name,
  ]
    .filter(Boolean)
    .join(", ");
  const hasCoords =
    complaint.latitude != null &&
    complaint.longitude != null &&
    complaint.latitude !== "" &&
    complaint.longitude !== "";

  return (
    <Link
      to={to || `/app/complaint/${complaint.id}`}
      className="group relative block overflow-hidden rounded-2xl border border-hairline bg-white p-4 pl-5 shadow-card transition hover:-translate-y-0.5 hover:shadow-lift"
    >
      <span
        className="absolute inset-y-0 left-0 w-1.5"
        style={{ backgroundColor: rail }}
      />

      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <CategoryTag category={complaint.category} />
          <UrgencyPill urgency={complaint.urgency} />
          {complaint.is_emergency && <EmergencyFlag compact />}
          {complaint.duplicate_count > 0 && (
            <span
              className="inline-flex items-center gap-1 rounded-full bg-saffron-100 px-2 py-0.5 text-[11px] font-600 text-saffron-600"
              title="Possible duplicate reports in this area"
            >
              <Copy className="h-3 w-3" />
              {complaint.duplicate_count} similar
            </span>
          )}
        </div>
        <div className="flex shrink-0 items-center gap-1">
          <span
            className="font-mono text-lg font-600 tabular leading-none"
            style={{ color: pColor }}
          >
            {Math.round(complaint.priority_score)}
          </span>
          <span className="text-[10px] font-600 text-muted">/100</span>
        </div>
      </div>

      <h3 className="mt-2.5 line-clamp-1 font-display text-[15px] font-600 text-body">
        {complaint.title}
      </h3>
      {complaint.ai_summary && (
        <p className="mt-1 line-clamp-2 text-sm leading-relaxed text-muted">
          {complaint.ai_summary}
        </p>
      )}

      {(locationLabel || hasCoords) && (
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
          {locationLabel && (
            <span className="inline-flex items-center gap-1">
              <MapPin className="h-3.5 w-3.5 text-royal" />
              {locationLabel}
            </span>
          )}
          {hasCoords && (
            <span className="font-mono">
              {Number(complaint.latitude).toFixed(4)}, {Number(complaint.longitude).toFixed(4)}
            </span>
          )}
        </div>
      )}

      {complaint.dataset_mode && (
        <div className="mt-2.5">
          <DatasetModeBadge
            mode={complaint.dataset_mode}
            matched={complaint.matched_datasets}
          />
        </div>
      )}

      <div className="mt-3 flex items-center justify-between border-t border-hairline pt-3">
        <div className="flex items-center gap-3">
          <StatusBadge status={complaint.status} />
          {complaint.complaint_code && (
            <span className="font-mono text-xs text-muted">
              {complaint.complaint_code}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-muted">
          <span>{formatDate(complaint.created_at)}</span>
          <ArrowUpRight className="h-4 w-4 text-royal opacity-0 transition group-hover:opacity-100" />
        </div>
      </div>
    </Link>
  );
}
