import { useEffect, useMemo, useState } from "react";
import { UserPlus, Loader2, Search } from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import { listUsers, createUser } from "../../api/admin";
import { getConstituencyIndex } from "../../api/locations";
import { errorMessage } from "../../api/client";
import { useToast } from "../../components/ui/Toast";
import Modal from "../../components/ui/Modal";
import Loader from "../../components/ui/Loader";

const ROLE_META = {
  super_admin: { label: "Admin", cls: "bg-ink/5 text-ink" },
  mp: { label: "MP", cls: "bg-royal-50 text-royal" },
  officer: { label: "Officer", cls: "bg-saffron-100 text-saffron-600" },
  citizen: { label: "Citizen", cls: "bg-paper text-muted" },
};

const BLANK = { name: "", email: "", password: "", phone: "", role: "citizen", constituency_id: "" };

export default function AdminUsers() {
  usePageHeader("People", "Create and review platform accounts");
  const toast = useToast();
  const [users, setUsers] = useState(null);
  const [constituencies, setConstituencies] = useState([]);
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(BLANK);
  const [busy, setBusy] = useState(false);

  function load() {
    listUsers().then(setUsers).catch(() => setUsers([]));
  }
  useEffect(() => {
    load();
    getConstituencyIndex()
      .then((index) =>
        setConstituencies(
          Object.entries(index).map(([id, v]) => ({ id: Number(id), name: v.name }))
        )
      )
      .catch(() => {});
  }, []);

  const needsConstituency = form.role === "mp" || form.role === "officer";
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const filtered = useMemo(() => {
    if (!users) return [];
    if (!q) return users;
    const s = q.toLowerCase();
    return users.filter((u) => `${u.name} ${u.email} ${u.role}`.toLowerCase().includes(s));
  }, [users, q]);

  async function submit() {
    setBusy(true);
    try {
      await createUser({
        name: form.name,
        email: form.email,
        password: form.password,
        phone: form.phone || null,
        role: form.role,
        constituency_id: needsConstituency && form.constituency_id ? Number(form.constituency_id) : null,
      });
      toast.success(`Created ${form.name}`);
      setOpen(false);
      setForm(BLANK);
      load();
    } catch (err) {
      toast.error(errorMessage(err, "Could not create the user."));
    } finally {
      setBusy(false);
    }
  }

  const constituencyName = (id) => constituencies.find((c) => c.id === id)?.name || "—";

  if (users === null) return <Loader label="Loading people" />;

  return (
    <div>
      <div className="mb-5 flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            className="input pl-9"
            placeholder="Search people…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <button className="btn-primary" onClick={() => setOpen(true)}>
          <UserPlus className="h-4 w-4" /> Add person
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-hairline bg-paper/60 text-left text-xs font-600 uppercase tracking-wide text-muted">
              <th className="px-4 py-3">Name</th>
              <th className="hidden px-4 py-3 sm:table-cell">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="hidden px-4 py-3 md:table-cell">Constituency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hairline">
            {filtered.map((u) => {
              const m = ROLE_META[u.role] || ROLE_META.citizen;
              return (
                <tr key={u.id} className="transition hover:bg-paper/40">
                  <td className="px-4 py-3">
                    <p className="font-600 text-body">{u.name}</p>
                    <p className="text-xs text-muted sm:hidden">{u.email}</p>
                  </td>
                  <td className="hidden px-4 py-3 text-muted sm:table-cell">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`chip ${m.cls}`}>{m.label}</span>
                  </td>
                  <td className="hidden px-4 py-3 text-muted md:table-cell">
                    {u.constituency_id ? constituencyName(u.constituency_id) : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Add a person"
        footer={
          <>
            <button className="btn-ghost" onClick={() => setOpen(false)}>Cancel</button>
            <button
              className="btn-primary"
              onClick={submit}
              disabled={busy || !form.name || !form.email || !form.password || (needsConstituency && !form.constituency_id)}
            >
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create"}
            </button>
          </>
        }
      >
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Name</label>
              <input className="input" value={form.name} onChange={set("name")} />
            </div>
            <div>
              <label className="label">Phone</label>
              <input className="input" value={form.phone} onChange={set("phone")} placeholder="Optional" />
            </div>
          </div>
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" value={form.email} onChange={set("email")} />
          </div>
          <div>
            <label className="label">Temporary password</label>
            <input className="input" value={form.password} onChange={set("password")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Role</label>
              <select className="input" value={form.role} onChange={set("role")}>
                <option value="citizen">Citizen</option>
                <option value="officer">Field officer</option>
                <option value="mp">Member of Parliament</option>
                <option value="super_admin">Administrator</option>
              </select>
            </div>
            {needsConstituency && (
              <div>
                <label className="label">Constituency</label>
                <select className="input" value={form.constituency_id} onChange={set("constituency_id")}>
                  <option value="">Select…</option>
                  {constituencies.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}
