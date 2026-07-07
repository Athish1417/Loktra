import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Mic,
  MicOff,
  ImagePlus,
  X,
  Loader2,
  CheckCircle2,
  Send,
  Sparkles,
  Ban,
  Crosshair,
} from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import useSpeech from "../../lib/useSpeech";
import { LANGUAGES } from "../../lib/constants";
import LocationCascade from "../../components/LocationCascade";
import { submitComplaint } from "../../api/complaints";
import { getConstituencyIndex } from "../../api/locations";
import { useAuth } from "../../context/AuthContext";
import { errorMessage } from "../../api/client";
import { useToast } from "../../components/ui/Toast";
import {
  StatusBadge,
  UrgencyPill,
  CategoryTag,
  EmergencyFlag,
  DatasetModeBadge,
} from "../../components/ui/Badges";
import PriorityGauge from "../../components/ui/PriorityGauge";

const EMPTY = {
  title: "",
  description: "",
  language: "en",
  category: "",
  state_id: "",
  district_id: "",
  constituency_id: "",
  ward_id: "",
  latitude: "",
  longitude: "",
};

function homeLocation(user) {
  return {
    state_id: user?.home_state_id || "",
    district_id: user?.home_district_id || "",
    constituency_id: user?.home_constituency_id || "",
    ward_id: user?.home_ward_id || "",
  };
}

export default function SubmitComplaint() {
  usePageHeader("Report an issue", "Describe a civic problem — AI does the rest");
  const toast = useToast();
  const { user } = useAuth();
  const hasHome = !!user?.home_constituency_id;

  const [form, setForm] = useState(() => ({ ...EMPTY, ...homeLocation(user) }));
  const [overrideLoc, setOverrideLoc] = useState(!hasHome);
  const [homeLabel, setHomeLabel] = useState("");
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [rejected, setRejected] = useState(null);
  const [locating, setLocating] = useState(false);
  const [resetKey, setResetKey] = useState(0); // remounts the location cascade on reset

  const langMeta = LANGUAGES.find((l) => l.code === form.language) || LANGUAGES[0];
  const speech = useSpeech(langMeta.speech, (text) =>
    setForm((f) => ({
      ...f,
      description: (f.description ? f.description + " " : "") + text,
    }))
  );

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const patch = (p) => setForm((f) => ({ ...f, ...p }));

  // Resolve the registered constituency name for the "using your location" note.
  useEffect(() => {
    if (!hasHome) return;
    getConstituencyIndex()
      .then((idx) => setHomeLabel(idx[user.home_constituency_id]?.name || "your saved location"))
      .catch(() => setHomeLabel("your saved location"));
  }, [hasHome, user]);

  function useMyLocation() {
    if (!navigator.geolocation) {
      toast.error("Geolocation isn't supported in this browser.");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        patch({
          latitude: pos.coords.latitude.toFixed(6),
          longitude: pos.coords.longitude.toFixed(6),
        });
        setLocating(false);
        toast.success("Current location captured");
      },
      () => {
        setLocating(false);
        toast.error("Could not get your location. You can enter it manually.");
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  function onImage(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImage(file);
    setPreview(URL.createObjectURL(file));
  }
  function clearImage() {
    setImage(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
  }

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setRejected(null);
    try {
      const data = await submitComplaint(
        {
          title: form.title,
          description: form.description,
          language: form.language,
          category: form.category || undefined,
          state_id: form.state_id || undefined,
          district_id: form.district_id || undefined,
          constituency_id: form.constituency_id || undefined,
          ward_id: form.ward_id || undefined,
          latitude: form.latitude || undefined,
          longitude: form.longitude || undefined,
        },
        image
      );
      setResult(data);
      toast.success("Report submitted and prioritised");
    } catch (err) {
      if (err?.response?.status === 422) {
        // Governance-relevance guard rejected it.
        setRejected(errorMessage(err));
      } else {
        toast.error(errorMessage(err, "Could not submit your report."));
      }
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setForm({ ...EMPTY, ...homeLocation(user) });
    setOverrideLoc(!hasHome);
    clearImage();
    setResult(null);
    setRejected(null);
    setResetKey((k) => k + 1);
  }

  // ---- Success view ----
  if (result) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto max-w-xl"
      >
        <div className="card overflow-hidden">
          <div className="flex items-center gap-3 border-b border-hairline bg-success/5 px-6 py-5">
            <CheckCircle2 className="h-6 w-6 text-success" />
            <div>
              <h2 className="font-display text-lg font-600 text-body">
                Report received
              </h2>
              <p className="font-mono text-sm text-muted">{result.complaint_code}</p>
            </div>
          </div>

          <div className="flex items-center gap-5 px-6 py-6">
            <PriorityGauge score={result.priority_score} />
            <div className="min-w-0 flex-1">
              <div className="mb-2 flex flex-wrap items-center gap-1.5">
                <CategoryTag category={result.category} />
                <UrgencyPill urgency={result.urgency} />
                {result.is_emergency && <EmergencyFlag compact />}
              </div>
              <p className="text-sm leading-relaxed text-muted">
                {result.ai_summary}
              </p>
              {result.dataset_mode && (
                <div className="mt-2.5">
                  <DatasetModeBadge
                    mode={result.dataset_mode}
                    matched={result.matched_datasets}
                  />
                </div>
              )}
            </div>
          </div>

          <div className="border-t border-hairline px-6 py-4">
            <div className="flex items-start gap-2 rounded-xl bg-royal-50 p-3">
              <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-royal" />
              <p className="whitespace-pre-line text-xs leading-relaxed text-royal-600">
                {result.ai_reason}
              </p>
            </div>
          </div>

          <div className="flex gap-2 border-t border-hairline bg-paper/50 px-6 py-4">
            <button onClick={reset} className="btn-primary flex-1">
              Report another
            </button>
            <Link to="/app/my-reports" className="btn-ghost flex-1 justify-center">
              View my reports
            </Link>
          </div>
        </div>
      </motion.div>
    );
  }

  // ---- Form view ----
  return (
    <div className="mx-auto max-w-2xl">
      <form onSubmit={submit} className="space-y-5">
        {rejected && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-3 rounded-2xl border border-emergency/20 bg-emergency/5 p-4"
          >
            <Ban className="mt-0.5 h-5 w-5 shrink-0 text-emergency" />
            <div>
              <p className="text-sm font-600 text-emergency">Post not accepted</p>
              <p className="mt-0.5 text-sm text-body/80">{rejected}</p>
            </div>
          </motion.div>
        )}

        <div className="card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-display font-600 text-body">What's the issue?</h3>
            <select
              value={form.language}
              onChange={set("language")}
              className="rounded-lg border border-hairline bg-white px-2.5 py-1.5 text-xs font-600 text-muted outline-none focus:border-royal"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-4">
            <div>
              <label className="label">Title</label>
              <input
                className="input"
                required
                maxLength={140}
                value={form.title}
                onChange={set("title")}
                placeholder="e.g. Water pipeline burst near the market"
              />
            </div>

            <div>
              <div className="mb-1.5 flex items-center justify-between">
                <label className="label mb-0">Description</label>
                <button
                  type="button"
                  onClick={speech.toggle}
                  disabled={!speech.supported}
                  className={[
                    "inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-600 transition",
                    speech.listening
                      ? "bg-emergency/10 text-emergency animate-pulse-ring"
                      : "bg-royal-50 text-royal hover:bg-royal-100",
                    !speech.supported && "opacity-40",
                  ].join(" ")}
                  title={speech.supported ? "Dictate" : "Voice input not supported in this browser"}
                >
                  {speech.listening ? <MicOff className="h-3.5 w-3.5" /> : <Mic className="h-3.5 w-3.5" />}
                  {speech.listening ? "Listening…" : "Speak"}
                </button>
              </div>
              <textarea
                className="input min-h-[120px] resize-y"
                required
                value={form.description}
                onChange={set("description")}
                placeholder="Describe what's happening, since when, and where exactly…"
              />
            </div>

            {/* Image upload */}
            {preview ? (
              <div className="relative overflow-hidden rounded-xl border border-hairline">
                <img src={preview} alt="attachment" className="max-h-56 w-full object-cover" />
                <button
                  type="button"
                  onClick={clearImage}
                  className="absolute right-2 top-2 rounded-lg bg-ink/70 p-1.5 text-white backdrop-blur"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <label className="flex cursor-pointer items-center justify-center gap-2 rounded-xl border border-dashed border-hairline bg-paper/50 py-5 text-sm font-500 text-muted transition hover:border-royal hover:text-royal">
                <ImagePlus className="h-5 w-5" />
                Add a photo (optional)
                <input type="file" accept="image/*" className="hidden" onChange={onImage} />
              </label>
            )}
          </div>
        </div>

        <div className="card p-5">
          <h3 className="mb-4 font-display font-600 text-body">Where is it?</h3>
          {hasHome && !overrideLoc ? (
            <div className="rounded-xl border border-hairline bg-paper/50 p-3.5">
              <p className="text-sm text-body">
                Reporting for your registered location
                {homeLabel ? (
                  <>
                    : <strong className="font-600">{homeLabel}</strong>
                  </>
                ) : (
                  ""
                )}
                .
              </p>
              <button
                type="button"
                onClick={() => setOverrideLoc(true)}
                className="mt-2 text-sm font-600 text-royal hover:underline"
              >
                Report for another location
              </button>
            </div>
          ) : (
            <>
              <LocationCascade key={resetKey} value={form} onChange={patch} />
              {hasHome && (
                <button
                  type="button"
                  onClick={() => {
                    patch(homeLocation(user));
                    setOverrideLoc(false);
                  }}
                  className="mt-2 text-xs font-600 text-muted hover:text-body"
                >
                  Use my registered location instead
                </button>
              )}
              <p className="mt-3 text-xs text-muted">
                Routing the report to the correct constituency puts it in front of the
                right MP and field officers.
              </p>
            </>
          )}

          <div className="mt-4 border-t border-hairline pt-4">
            <div className="mb-1.5 flex items-center justify-between">
              <label className="label mb-0">Exact coordinates (optional)</label>
              <button
                type="button"
                onClick={useMyLocation}
                disabled={locating}
                className="inline-flex items-center gap-1.5 rounded-lg bg-royal-50 px-2.5 py-1 text-xs font-600 text-royal transition hover:bg-royal-100 disabled:opacity-50"
              >
                {locating ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Crosshair className="h-3.5 w-3.5" />
                )}
                Use my current location
              </button>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <input
                className="input"
                type="number"
                step="any"
                placeholder="Latitude"
                value={form.latitude}
                onChange={set("latitude")}
              />
              <input
                className="input"
                type="number"
                step="any"
                placeholder="Longitude"
                value={form.longitude}
                onChange={set("longitude")}
              />
            </div>
          </div>
        </div>

        <button className="btn-primary w-full py-3 text-[15px]" disabled={busy}>
          {busy ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Analysing & routing…
            </>
          ) : (
            <>
              <Send className="h-4 w-4" /> Submit report
            </>
          )}
        </button>
      </form>
    </div>
  );
}
