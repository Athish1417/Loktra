import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Cell,
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
} from "recharts";
import { STATUS_META, URGENCY_META } from "../../lib/constants";

const CATEGORY_COLORS = [
  "#3B49C4", "#F5A524", "#12A150", "#E5484D", "#7C3AED",
  "#0EA5E9", "#F5820B", "#64748B", "#EC4899", "#14B8A6",
  "#6366F1", "#A16207",
];

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-hairline bg-white px-3 py-2 shadow-lift">
      <p className="text-xs font-600 text-body">{label || payload[0].name}</p>
      <p className="text-xs text-muted">
        {payload[0].value} report{payload[0].value === 1 ? "" : "s"}
      </p>
    </div>
  );
}

// Horizontal bar chart of complaint counts by category.
export function CategoryChart({ data }) {
  const rows = Object.entries(data || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  if (!rows.length) {
    return <p className="py-8 text-center text-sm text-muted">No data yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(180, rows.length * 38)}>
      <BarChart
        data={rows}
        layout="vertical"
        margin={{ left: 8, right: 16, top: 4, bottom: 4 }}
        barCategoryGap={10}
      >
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey="name"
          width={110}
          tick={{ fontSize: 12, fill: "#5B6178" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip cursor={{ fill: "#F6F7FB" }} content={<ChartTooltip />} />
        <Bar dataKey="value" radius={[0, 6, 6, 0]} maxBarSize={22}>
          {rows.map((_, i) => (
            <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// Donut of status distribution.
export function StatusDonut({ data }) {
  const rows = Object.entries(data || {}).map(([name, value]) => ({
    name,
    value,
    color: (STATUS_META[name] || {}).color || "#64748B",
  }));
  const total = rows.reduce((s, r) => s + r.value, 0);

  if (!total) {
    return <p className="py-8 text-center text-sm text-muted">No data yet.</p>;
  }

  return (
    <div className="flex items-center gap-4">
      <div className="relative h-[150px] w-[150px] shrink-0">
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={rows}
              dataKey="value"
              innerRadius={48}
              outerRadius={70}
              paddingAngle={2}
              stroke="none"
            >
              {rows.map((r, i) => (
                <Cell key={i} fill={r.color} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display text-2xl font-700 tabular text-body">
            {total}
          </span>
          <span className="text-[10px] font-600 uppercase tracking-wide text-muted">
            total
          </span>
        </div>
      </div>
      <ul className="flex-1 space-y-1.5">
        {rows.map((r) => (
          <li key={r.name} className="flex items-center gap-2 text-sm">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: r.color }}
            />
            <span className="flex-1 text-muted">{r.name}</span>
            <span className="font-600 tabular text-body">{r.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
