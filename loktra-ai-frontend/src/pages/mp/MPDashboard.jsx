import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  FileText,
  Clock,
  CheckCircle2,
  Flame,
  AlertTriangle,
  ArrowUpRight,
  Lightbulb,
  MapPinned,
  ShieldAlert,
} from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import useRefetchOnFocus from "../../lib/useRefetchOnFocus";
import { useAuth } from "../../context/AuthContext";
import * as mpApi from "../../api/mp";
import { getConstituencyIndex } from "../../api/locations";
import {
  CONSTITUENCY_COORDS,
  DEFAULT_MAP_CENTER,
  URGENCY_META,
  priorityColor,
  jitter,
} from "../../lib/constants";
import StatTile from "../../components/ui/StatTile";
import { CategoryChart, StatusDonut } from "../../components/charts/Charts";
import ConstituencyMap from "../../components/ConstituencyMap";
import ComplaintCard from "../../components/ComplaintCard";
import { StatusBadge } from "../../components/ui/Badges";
import Loader from "../../components/ui/Loader";

// A complaint is "critical" if it is high-scoring, an emergency, or high urgency.
const CRITICAL_URGENCY = new Set(["Emergency", "High"]);
function isCritical(c) {
  return c.priority_score >= 85 || c.is_emergency || CRITICAL_URGENCY.has(c.urgency);
}

// Count complaints by an area key (state / district / city-ward), ranked desc.
function countBy(items, keyFn) {
  const m = {};
  for (const it of items) {
    const k = keyFn(it);
    if (!k) continue;
    m[k] = (m[k] || 0) + 1;
  }
  return Object.entries(m).sort((a, b) => b[1] - a[1]);
}

function AreaCard({ title, rows }) {
  return (
    <div className="card p-5">
      <h3 className="mb-3 font-display font-600 text-body">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-muted">No data yet.</p>
      ) : (
        <div className="divide-y divide-hairline">
          {rows.slice(0, 6).map(([name, count]) => (
            <div key={name} className="flex items-center justify-between gap-3 py-2 text-sm">
              <span className="truncate text-body">{name}</span>
              <span className="chip shrink-0 bg-royal-50 text-royal">
                {count} complaint{count === 1 ? "" : "s"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const REC_TONE = {
  critical: { dot: "#E5484D", chip: "bg-emergency/10 text-emergency" },
  high: { dot: "#F5820B", chip: "bg-saffron-100 text-saffron-600" },
  medium: { dot: "#3B49C4", chip: "bg-royal-50 text-royal" },
  info: { dot: "#12A150", chip: "bg-success/10 text-success" },
};

export default function MPDashboard() {
  usePageHeader("Constituency dashboard", "Live civic intelligence for your area");
  const { user } = useAuth();
  const profileIncomplete = !user?.constituency_id;
  const [data, setData] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [points, setPoints] = useState([]);
  const [center, setCenter] = useState(DEFAULT_MAP_CENTER);

  // Build map markers; `index` (constituency id -> name) is optional and only
  // refines centroid coordinates — points still render without it.
  function buildPoints(list, index) {
    const pts = list.map((c) => {
      const name = index?.[c.constituency_id]?.name;
      const hasCoords =
        Number.isFinite(c.latitude) && Number.isFinite(c.longitude);
      const base = (name && CONSTITUENCY_COORDS[name]) || DEFAULT_MAP_CENTER;
      const position = hasCoords ? [c.latitude, c.longitude] : jitter(c.id, base);
      return {
        id: c.id,
        position,
        urgency: c.urgency,
        is_emergency: c.is_emergency,
        title: c.title,
        code: c.complaint_code,
        score: c.priority_score,
        category: c.category,
        status: c.status,
      };
    });
    setPoints(pts);
    if (pts[0]) {
      const firstName = index?.[list[0]?.constituency_id]?.name;
      setCenter((firstName && CONSTITUENCY_COORDS[firstName]) || pts[0].position);
    }
  }

  function load() {
    mpApi.getDashboard().then(setData).catch(() => setData(false));

    // Complaints drive the critical/recent/area lists — set them immediately,
    // independent of the (potentially slow) constituency index.
    mpApi
      .mpComplaints()
      .then((list) => {
        setComplaints(list);
        buildPoints(list, null); // render markers now with fallback coordinates
        getConstituencyIndex()
          .then((index) => buildPoints(list, index)) // refine centroids when ready
          .catch(() => {});
      })
      .catch(() => setComplaints([]));
  }

  useEffect(() => {
    load();
  }, []);
  // Re-pull from the backend (source of truth) when the MP returns to the tab.
  useRefetchOnFocus(load);

  if (data === null) return <Loader label="Building your dashboard" />;
  if (data === false)
    return <p className="text-sm text-muted">Could not load the dashboard.</p>;

  const s = data.summary;
  const critical = [...complaints]
    .filter(isCritical)
    .sort((a, b) => b.priority_score - a.priority_score)
    .slice(0, 6);
  const recent = [...complaints]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 6);
  // Area problem counts — shown even when complaints have no map coordinates.
  const byState = countBy(complaints, (c) => c.state_name);
  const byDistrict = countBy(complaints, (c) => c.district_name);
  const byCity = countBy(complaints, (c) => c.ward_name || c.constituency_name);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {profileIncomplete && (
        <div className="rounded-xl border border-saffron-600/30 bg-saffron-100 px-4 py-3 text-sm font-500 text-saffron-600">
          MP location profile incomplete. Showing relevant open complaints.
        </div>
      )}

      {/* Critical issues — surfaced first so the MP sees them immediately. */}
      {critical.length > 0 && (
        <div className="rounded-2xl border border-emergency/30 bg-white p-5 shadow-card">
          <div className="mb-4 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-emergency" />
            <h3 className="font-display font-600 text-body">
              Critical Issues Needing Attention
            </h3>
            <span className="chip bg-emergency/10 text-emergency">
              {critical.length}
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {critical.map((c) => (
              <ComplaintCard key={c.id} complaint={c} />
            ))}
          </div>
        </div>
      )}

      {/* Stat tiles */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <StatTile icon={FileText} label="Total reports" value={s.total_complaints} tone="ink" />
        <StatTile icon={Clock} label="Pending" value={s.pending} tone="royal" />
        <StatTile icon={Flame} label="High priority" value={s.high_priority} tone="saffron" />
        <StatTile icon={AlertTriangle} label="Emergencies" value={s.emergencies} tone="emergency" />
        <StatTile icon={CheckCircle2} label="Resolved" value={s.resolution_rate} suffix="%" tone="success" />
      </div>

      {/* Charts */}
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-5">
          <h3 className="mb-4 font-display font-600 text-body">Reports by category</h3>
          <CategoryChart data={data.category_distribution} />
        </div>
        <div className="card p-5">
          <h3 className="mb-4 font-display font-600 text-body">Status breakdown</h3>
          <StatusDonut data={data.status_distribution} />
        </div>
      </div>

      {/* Map + recommendations */}
      <div className="grid gap-5 lg:grid-cols-3">
        <div className="card overflow-hidden p-5 lg:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <MapPinned className="h-4 w-4 text-royal" />
            <h3 className="font-display font-600 text-body">Where reports are coming from</h3>
          </div>
          <div className="h-[340px]">
            <ConstituencyMap points={points} center={center} />
          </div>
        </div>

        <div className="card p-5">
          <div className="mb-4 flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-saffron" />
            <h3 className="font-display font-600 text-body">Recommended focus</h3>
          </div>
          <div className="space-y-3">
            {data.recommendations.map((r, i) => {
              const tone = REC_TONE[r.priority] || REC_TONE.medium;
              return (
                <div key={i} className="rounded-xl border border-hairline p-3">
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{ backgroundColor: tone.dot }}
                    />
                    <p className="flex-1 text-sm font-600 text-body">{r.title}</p>
                    <span className={`chip ${tone.chip} capitalize`}>{r.priority}</span>
                  </div>
                  <p className="mt-1.5 pl-4 text-xs leading-relaxed text-muted">
                    {r.detail}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Problems by area — counts work even without map coordinates */}
      <div className="grid gap-5 lg:grid-cols-3">
        <AreaCard title="Problems by State" rows={byState} />
        <AreaCard title="Problems by District" rows={byDistrict} />
        <AreaCard title="Problems by City / Ward" rows={byCity} />
      </div>

      {/* Recent complaints */}
      <div className="card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display font-600 text-body">Recent reports</h3>
          <Link
            to="/app/complaints"
            className="inline-flex items-center gap-1 text-sm font-600 text-royal hover:underline"
          >
            View all <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>
        {recent.length === 0 ? (
          <p className="py-4 text-sm text-muted">No reports yet.</p>
        ) : (
        <div className="divide-y divide-hairline">
          {recent.map((c) => (
            <Link
              key={c.id}
              to={`/app/complaint/${c.id}`}
              className="flex items-center gap-3 py-3 transition hover:bg-paper/60"
            >
              <span
                className="h-9 w-1.5 shrink-0 rounded-full"
                style={{ backgroundColor: (URGENCY_META[c.urgency] || URGENCY_META.Medium).color }}
              />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-600 text-body">{c.title}</p>
                <p className="font-mono text-xs text-muted">{c.complaint_code}</p>
              </div>
              <span
                className="font-mono text-base font-600 tabular"
                style={{ color: priorityColor(c.priority_score) }}
              >
                {Math.round(c.priority_score)}
              </span>
              <div className="hidden sm:block">
                <StatusBadge status={c.status} />
              </div>
            </Link>
          ))}
        </div>
        )}
      </div>
    </motion.div>
  );
}
