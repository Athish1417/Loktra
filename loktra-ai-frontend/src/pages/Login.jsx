import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  ArrowLeft,
  Loader2,
  Radio,
  ShieldCheck,
  Users,
  User,
  Landmark,
  ClipboardCheck,
  Eye,
  EyeOff,
} from "lucide-react";
import Logo from "../components/ui/Logo";
import ForgotPasswordModal from "../components/ForgotPasswordModal";
import { useAuth, HOME_BY_ROLE } from "../context/AuthContext";
import { useToast } from "../components/ui/Toast";
import { errorMessage } from "../api/client";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const ROLES = [
  { value: "citizen", label: "Citizen", icon: User, desc: "Report & track issues" },
  { value: "mp", label: "MP / Admin", icon: Landmark, desc: "Constituency dashboard" },
  { value: "officer", label: "Officer", icon: ClipboardCheck, desc: "Field work queue" },
  { value: "super_admin", label: "Super Admin", icon: ShieldCheck, desc: "Platform control" },
];
const ROLE_LABEL = Object.fromEntries(ROLES.map((r) => [r.value, r.label]));

const HIGHLIGHTS = [
  { icon: Radio, text: "Report issues by text, voice or photo in 8 languages" },
  { icon: ShieldCheck, text: "AI validates, scores and routes to your constituency" },
  { icon: Users, text: "MPs get live decision-support, not just a complaint list" },
];

export default function Login() {
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState("role"); // 'role' | 'credentials'
  const [role, setRole] = useState(null);
  const [form, setForm] = useState({ email: "", password: "" });
  const [show, setShow] = useState(false);
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const [forgotOpen, setForgotOpen] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  function pickRole(value) {
    setRole(value);
    setErrors({});
    setStep("credentials");
  }

  async function submit(e) {
    e.preventDefault();
    const err = {};
    if (!EMAIL_RE.test(form.email)) err.email = "Enter a valid email address.";
    if (form.password.length < 6) err.password = "Password must be at least 6 characters.";
    setErrors(err);
    if (Object.keys(err).length) return;

    setBusy(true);
    try {
      // Enforce the selected role against the backend (source of truth). A mismatch
      // is rejected before any session is established. Redirect by authenticated role.
      const user = await login(form.email, form.password, role);
      toast.success(`Welcome, ${user.name.split(" ")[0]}`);
      const dest = HOME_BY_ROLE[user.role] || location.state?.from?.pathname || "/app";
      navigate(dest, { replace: true });
    } catch (err2) {
      if (err2?.code === "ROLE_MISMATCH") {
        const msg = `This account is not registered as ${ROLE_LABEL[role]}. Please choose the correct role.`;
        setErrors({ form: msg });
        toast.error(msg);
      } else {
        toast.error(errorMessage(err2, "Could not sign in."));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden overflow-hidden bg-ink p-12 text-white lg:flex lg:flex-col">
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full opacity-20 blur-3xl"
          style={{ background: "radial-gradient(circle, #3B49C4, transparent)" }}
        />
        <div
          className="pointer-events-none absolute -bottom-32 -left-16 h-96 w-96 rounded-full opacity-10 blur-3xl"
          style={{ background: "radial-gradient(circle, #F5A524, transparent)" }}
        />
        <Logo light size={32} />

        <div className="relative mt-auto">
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-saffron">
            Constituency Intelligence
          </p>
          <h1 className="mt-3 max-w-md font-display text-4xl font-700 leading-tight">
            Turn civic complaints into governance decisions.
          </h1>
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-white/60">
            Loktra listens to citizens, understands what matters, and hands
            representatives a prioritised, routed picture of their constituency.
          </p>

          <ul className="mt-8 space-y-3">
            {HIGHLIGHTS.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3 text-sm text-white/80">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
                  <Icon className="h-4 w-4 text-saffron" />
                </span>
                {text}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Auth form */}
      <div className="flex items-center justify-center bg-paper px-5 py-10">
        <motion.div
          key={step}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-sm"
        >
          <div className="mb-8 lg:hidden">
            <Logo size={30} />
          </div>

          {step === "role" ? (
            <>
              <h2 className="font-display text-2xl font-700 text-body">Sign in</h2>
              <p className="mt-1 text-sm text-muted">Choose how you're signing in.</p>

              <div className="mt-6 grid grid-cols-2 gap-3">
                {ROLES.map(({ value, label, icon: Icon, desc }) => (
                  <button
                    key={value}
                    onClick={() => pickRole(value)}
                    className="card flex flex-col items-start gap-2 p-4 text-left transition hover:border-royal hover:shadow-lift"
                  >
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-royal-50 text-royal">
                      <Icon className="h-4.5 w-4.5" />
                    </span>
                    <span className="font-display text-sm font-600 text-body">{label}</span>
                    <span className="text-xs text-muted">{desc}</span>
                  </button>
                ))}
              </div>

              <p className="mt-6 text-center text-sm text-muted">
                New to Loktra?{" "}
                <Link to="/register" className="font-600 text-royal hover:underline">
                  Create an account
                </Link>
              </p>
            </>
          ) : (
            <>
              <button
                onClick={() => setStep("role")}
                className="mb-4 inline-flex items-center gap-1.5 text-sm font-600 text-muted hover:text-body"
              >
                <ArrowLeft className="h-4 w-4" /> Back
              </button>

              <h2 className="font-display text-2xl font-700 text-body">
                Sign in as {ROLE_LABEL[role]}
              </h2>
              <p className="mt-1 text-sm text-muted">Enter your credentials to continue.</p>

              <form onSubmit={submit} className="mt-6 space-y-4" noValidate>
                {errors.form && (
                  <div className="rounded-lg border border-emergency/20 bg-emergency/5 px-3 py-2 text-sm font-500 text-emergency">
                    {errors.form}
                  </div>
                )}
                <div>
                  <label className="label">Email</label>
                  <input
                    className="input"
                    type="email"
                    autoFocus
                    value={form.email}
                    onChange={set("email")}
                    placeholder="you@example.com"
                  />
                  {errors.email && <p className="mt-1 text-xs font-500 text-emergency">{errors.email}</p>}
                </div>
                <div>
                  <div className="mb-1.5 flex items-center justify-between">
                    <label className="label mb-0">Password</label>
                    <button
                      type="button"
                      onClick={() => setForgotOpen(true)}
                      className="text-xs font-600 text-royal hover:underline"
                    >
                      Forgot password?
                    </button>
                  </div>
                  <div className="relative">
                    <input
                      className="input pr-10"
                      type={show ? "text" : "password"}
                      value={form.password}
                      onChange={set("password")}
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShow((s) => !s)}
                      className="absolute inset-y-0 right-0 flex items-center px-3 text-muted hover:text-body"
                      aria-label={show ? "Hide password" : "Show password"}
                    >
                      {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {errors.password && <p className="mt-1 text-xs font-500 text-emergency">{errors.password}</p>}
                </div>

                <button className="btn-primary w-full" disabled={busy}>
                  {busy ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      Sign in
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </form>

              <p className="mt-4 text-center text-sm text-muted">
                New to Loktra?{" "}
                <Link to="/register" className="font-600 text-royal hover:underline">
                  Create an account
                </Link>
              </p>

              <p className="mt-6 text-center text-xs text-muted">
                Use the demo credentials provided in the README.
              </p>
            </>
          )}
        </motion.div>
      </div>

      <ForgotPasswordModal open={forgotOpen} onClose={() => setForgotOpen(false)} />
    </div>
  );
}
