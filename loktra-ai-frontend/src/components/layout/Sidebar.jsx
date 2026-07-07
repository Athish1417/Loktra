import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FilePlus2,
  ListChecks,
  Search,
  ClipboardCheck,
  Users,
  Building2,
  ShieldCheck,
} from "lucide-react";
import Logo from "../ui/Logo";
import { useAuth } from "../../context/AuthContext";

const NAV = {
  citizen: [
    { to: "/app/submit", label: "Report an issue", icon: FilePlus2 },
    { to: "/app/my-reports", label: "My reports", icon: ListChecks },
    { to: "/app/track", label: "Track a report", icon: Search },
  ],
  officer: [
    { to: "/app/officer", label: "Work queue", icon: ClipboardCheck },
    { to: "/app/track", label: "Track a report", icon: Search },
  ],
  mp: [
    { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/app/complaints", label: "Constituency", icon: ListChecks },
    { to: "/app/track", label: "Track a report", icon: Search },
  ],
  super_admin: [
    { to: "/app/admin", label: "Overview", icon: ShieldCheck },
    { to: "/app/admin/users", label: "People", icon: Users },
    { to: "/app/admin/datasets", label: "Constituency data", icon: Building2 },
  ],
};

const ROLE_LABEL = {
  citizen: "Citizen",
  officer: "Field officer",
  mp: "Member of Parliament",
  super_admin: "Administrator",
};

export default function Sidebar({ onNavigate }) {
  const { role } = useAuth();
  const items = NAV[role] || [];

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col bg-ink text-white">
      <div className="px-5 py-5">
        <Logo light />
      </div>

      <div className="px-4">
        <div className="rounded-xl bg-white/5 px-3 py-2.5">
          <p className="text-[10px] font-600 uppercase tracking-wider text-white/40">
            Signed in as
          </p>
          <p className="mt-0.5 text-sm font-600 text-white/90">
            {ROLE_LABEL[role] || role}
          </p>
        </div>
      </div>

      <nav className="mt-4 flex-1 space-y-1 px-3">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to.split("/").length <= 3}
            onClick={onNavigate}
            className={({ isActive }) =>
              [
                "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-500 transition",
                isActive
                  ? "bg-royal text-white shadow-sm"
                  : "text-white/60 hover:bg-white/5 hover:text-white",
              ].join(" ")
            }
          >
            <Icon className="h-[18px] w-[18px]" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4">
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <p className="text-[11px] leading-relaxed text-white/50">
            AI validates, prioritises and routes every report to the right
            constituency.
          </p>
        </div>
      </div>
    </aside>
  );
}
