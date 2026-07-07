import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut, Menu, ChevronDown, Sparkles } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Topbar({ title, subtitle, onMenu }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  function handleLogout() {
    logout(); // clears token, user, and role from state + localStorage
    navigate("/login", { replace: true }); // replace so Back can't re-enter the app
  }
  const initials = (user?.name || "?")
    .split(" ")
    .map((s) => s[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-hairline bg-white/80 px-4 py-3 backdrop-blur-md sm:px-6">
      <button
        onClick={onMenu}
        className="rounded-lg p-2 text-muted transition hover:bg-paper lg:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="min-w-0 flex-1">
        <h1 className="truncate font-display text-lg font-600 text-body">
          {title}
        </h1>
        {subtitle && <p className="truncate text-xs text-muted">{subtitle}</p>}
      </div>

      <div className="hidden items-center gap-1.5 rounded-full border border-hairline bg-paper px-3 py-1.5 text-xs font-600 text-muted sm:flex">
        <Sparkles className="h-3.5 w-3.5 text-saffron" />
        AI prioritisation active
      </div>

      <div className="relative">
        <button
          onClick={() => setOpen((v) => !v)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          className="flex items-center gap-2 rounded-full border border-hairline bg-white py-1 pl-1 pr-2.5 transition hover:bg-paper"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-royal text-xs font-700 text-white">
            {initials}
          </span>
          <span className="hidden text-sm font-600 text-body sm:block">
            {user?.name?.split(" ")[0]}
          </span>
          <ChevronDown className="h-4 w-4 text-muted" />
        </button>

        {open && (
          <div className="absolute right-0 mt-2 w-56 overflow-hidden rounded-xl border border-hairline bg-white shadow-lift">
            <div className="border-b border-hairline px-4 py-3">
              <p className="text-sm font-600 text-body">{user?.name}</p>
              <p className="truncate text-xs text-muted">{user?.email}</p>
            </div>
            <button
              onMouseDown={handleLogout}
              className="flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-sm font-500 text-emergency transition hover:bg-emergency/5"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
