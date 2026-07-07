import { STATUS_META } from "../lib/constants";

function formatDateTime(iso) {
  try {
    return new Date(iso).toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

// Vertical status history for a complaint.
export default function Timeline({ events = [] }) {
  if (!events.length) {
    return <p className="text-sm text-muted">No status updates yet.</p>;
  }
  return (
    <ol className="relative space-y-5 pl-6">
      <span className="absolute left-[7px] top-1.5 bottom-1.5 w-px bg-hairline" />
      {events.map((ev, i) => {
        const m = STATUS_META[ev.status] || STATUS_META.Submitted;
        const isLast = i === events.length - 1;
        return (
          <li key={i} className="relative">
            <span
              className="absolute -left-6 top-0.5 h-4 w-4 rounded-full border-2 border-white"
              style={{ backgroundColor: m.color, boxShadow: isLast ? `0 0 0 3px ${m.bg}` : "none" }}
            />
            <div className="flex items-center gap-2">
              <p className="text-sm font-600" style={{ color: m.color }}>
                {ev.status}
              </p>
              <span className="text-xs text-muted">
                {formatDateTime(ev.created_at)}
              </span>
            </div>
            {ev.note && <p className="mt-0.5 text-sm text-muted">{ev.note}</p>}
          </li>
        );
      })}
    </ol>
  );
}
