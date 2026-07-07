import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  MapPin,
  Languages,
  Sparkles,
  BadgeCheck,
  UserCog,
  Loader2,
  Copy,
} from "lucide-react";
import { getComplaint } from "../api/complaints";
import * as officerApi from "../api/officer";
import * as mpApi from "../api/mp";
import { errorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/Toast";
import usePageHeader from "../lib/usePageHeader";
import { STATUS_FLOW } from "../lib/constants";
import { StatusBadge, UrgencyPill, CategoryTag, EmergencyFlag } from "../components/ui/Badges";
import PriorityGauge from "../components/ui/PriorityGauge";
import Timeline from "../components/Timeline";
import Modal from "../components/ui/Modal";
import Loader from "../components/ui/Loader";

export default function ComplaintDetail() {
  usePageHeader("Report detail", "Full record, AI reasoning and progress");
  const { id } = useParams();
  const navigate = useNavigate();
  const { role } = useAuth();
  const toast = useToast();

  const [c, setC] = useState(null);
  const [busy, setBusy] = useState(false);
  const [assignOpen, setAssignOpen] = useState(false);
  const [officers, setOfficers] = useState([]);
  const [officerId, setOfficerId] = useState("");
  const [statusValue, setStatusValue] = useState("");
  const [note, setNote] = useState("");

  const isStaff = role === "officer" || role === "mp" || role === "super_admin";

  function load() {
    getComplaint(id)
      .then((data) => {
        setC(data);
        setStatusValue(data.status);
      })
      .catch((err) => {
        toast.error(errorMessage(err, "Could not load this report."));
        navigate(-1);
      });
  }
  useEffect(() => {
    load();
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  async function verify() {
    setBusy(true);
    try {
      const updated = await officerApi.verifyComplaint(c.id);
      setC(updated);
      toast.success("Report verified");
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function saveStatus() {
    setBusy(true);
    try {
      const updated = await officerApi.updateStatus(c.id, statusValue, note || null);
      setC(updated);
      setNote("");
      toast.success(`Status set to ${statusValue}`);
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function openAssign() {
    setAssignOpen(true);
    try {
      const list = await mpApi.mpOfficers();
      setOfficers(list);
      if (list[0]) setOfficerId(String(list[0].id));
    } catch {
      setOfficers([]);
    }
  }

  async function confirmAssign() {
    setBusy(true);
    try {
      const updated = await mpApi.assignOfficer(c.id, Number(officerId));
      setC(updated);
      setAssignOpen(false);
      toast.success("Officer assigned");
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (!c) return <Loader label="Loading report" />;

  const showTranslation =
    c.original_language && c.original_language !== "en" && c.translated_text;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <button
        onClick={() => navigate(-1)}
        className="mb-4 inline-flex items-center gap-1.5 text-sm font-500 text-muted transition hover:text-body"
      >
        <ArrowLeft className="h-4 w-4" /> Back
      </button>

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Main column */}
        <div className="space-y-5 lg:col-span-2">
          <div className="card p-6">
            <div className="flex items-start gap-5">
              <div className="shrink-0">
                <PriorityGauge score={c.priority_score} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-mono text-xs text-muted">{c.complaint_code}</p>
                <h2 className="mt-1 font-display text-xl font-700 leading-snug text-body">
                  {c.title}
                </h2>
                <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                  <StatusBadge status={c.status} />
                  <UrgencyPill urgency={c.urgency} />
                  <CategoryTag category={c.category} />
                  {c.is_emergency && <EmergencyFlag compact />}
                </div>
              </div>
            </div>

            <p className="mt-5 whitespace-pre-line text-[15px] leading-relaxed text-body/90">
              {c.description}
            </p>

            {c.image_path && (
              <img
                src={c.image_path}
                alt="report attachment"
                className="mt-4 max-h-80 w-full rounded-xl border border-hairline object-cover"
              />
            )}

            {showTranslation && (
              <div className="mt-4 rounded-xl border border-hairline bg-paper/60 p-3.5">
                <div className="mb-1 flex items-center gap-1.5 text-xs font-600 text-muted">
                  <Languages className="h-3.5 w-3.5" />
                  Original ({c.original_language.toUpperCase()}) · English translation
                </div>
                <p className="text-sm text-body/80">{c.translated_text}</p>
              </div>
            )}
          </div>

          {/* AI reasoning */}
          <div className="card p-5">
            <div className="mb-2 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-saffron" />
              <h3 className="font-display font-600 text-body">AI assessment</h3>
            </div>
            {c.ai_summary && (
              <p className="text-sm leading-relaxed text-body/90">{c.ai_summary}</p>
            )}
            {c.ai_reason && (
              <>
                <p className="mt-3 text-xs font-600 uppercase tracking-wide text-muted">
                  Why this priority?
                </p>
                <p className="mt-1 whitespace-pre-line text-xs leading-relaxed text-muted">
                  {c.ai_reason}
                </p>
              </>
            )}
            {c.dataset_mode && (
              <div className="mt-3 border-t border-hairline pt-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-600 uppercase tracking-wide text-muted">
                    Dataset Mode
                  </span>
                  <span
                    className={`chip ${
                      c.dataset_mode === "Official Government Dataset"
                        ? "bg-success/10 text-success"
                        : "bg-saffron-100 text-saffron-600"
                    }`}
                  >
                    {c.dataset_mode}
                  </span>
                </div>
                {c.matched_datasets?.length > 0 && (
                  <div className="mt-2 flex flex-wrap items-center gap-1.5">
                    <span className="text-xs text-muted">Matched datasets:</span>
                    {c.matched_datasets.map((d) => (
                      <span key={d} className="chip bg-royal-50 text-royal">
                        {d}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {c.duplicate_count > 0 && (
              <div className="mt-3 flex items-center gap-2 rounded-lg bg-saffron-100 px-3 py-2 text-xs font-500 text-saffron-600">
                <Copy className="h-3.5 w-3.5" />
                {c.duplicate_count} possible duplicate report(s) detected in this area.
              </div>
            )}
          </div>
        </div>

        {/* Side column */}
        <div className="space-y-5">
          {isStaff && (
            <div className="card p-5">
              <h3 className="mb-3 font-display font-600 text-body">Actions</h3>
              <div className="space-y-3">
                {c.status === "Submitted" && (
                  <button onClick={verify} disabled={busy} className="btn-primary w-full">
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <BadgeCheck className="h-4 w-4" />}
                    Verify report
                  </button>
                )}

                {role === "mp" && (
                  <button onClick={openAssign} disabled={busy} className="btn-ink w-full">
                    <UserCog className="h-4 w-4" /> Assign officer
                  </button>
                )}

                <div className="rounded-xl border border-hairline p-3">
                  <label className="label">Update status</label>
                  <select
                    className="input"
                    value={statusValue}
                    onChange={(e) => setStatusValue(e.target.value)}
                  >
                    {STATUS_FLOW.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <input
                    className="input mt-2"
                    placeholder="Add a note (optional)"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                  />
                  <button
                    onClick={saveStatus}
                    disabled={busy || statusValue === c.status && !note}
                    className="btn-ghost mt-2 w-full justify-center"
                  >
                    Save update
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="card p-5">
            <div className="mb-3 flex items-center gap-2">
              <MapPin className="h-4 w-4 text-royal" />
              <h3 className="font-display font-600 text-body">Location</h3>
            </div>
            <dl className="space-y-1.5 text-sm">
              {[
                ["State", c.state_name],
                ["District", c.district_name],
                ["Constituency", c.constituency_name],
                ["Ward / Village", c.ward_name],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between gap-3">
                  <dt className="text-muted">{k}</dt>
                  <dd className="text-right font-500 text-body">{v || "—"}</dd>
                </div>
              ))}
              <div className="flex justify-between gap-3 border-t border-hairline pt-1.5">
                <dt className="text-muted">Latitude</dt>
                <dd className="text-right font-mono text-body">
                  {c.latitude != null ? c.latitude : "—"}
                </dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted">Longitude</dt>
                <dd className="text-right font-mono text-body">
                  {c.longitude != null ? c.longitude : "—"}
                </dd>
              </div>
            </dl>
          </div>

          <div className="card p-5">
            <h3 className="mb-3 font-display font-600 text-body">Progress</h3>
            <Timeline events={c.timeline} />
          </div>
        </div>
      </div>

      <Modal
        open={assignOpen}
        onClose={() => setAssignOpen(false)}
        title="Assign a field officer"
        footer={
          <>
            <button className="btn-ghost" onClick={() => setAssignOpen(false)}>
              Cancel
            </button>
            <button className="btn-primary" onClick={confirmAssign} disabled={busy || !officerId}>
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Assign"}
            </button>
          </>
        }
      >
        {officers.length ? (
          <div>
            <label className="label">Officer</label>
            <select
              className="input"
              value={officerId}
              onChange={(e) => setOfficerId(e.target.value)}
            >
              {officers.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name} — {o.email}
                </option>
              ))}
            </select>
            <p className="mt-2 text-xs text-muted">
              The officer must belong to this constituency.
            </p>
          </div>
        ) : (
          <p className="text-sm text-muted">
            No officers are registered for this constituency yet.
          </p>
        )}
      </Modal>
    </motion.div>
  );
}
